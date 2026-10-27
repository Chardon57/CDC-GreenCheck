"""Tests de POST /analysis et de GET /history/{id}/image.

Pl@ntNet et le moteur IA sont remplacés par des faux : aucun appel réseau, aucun quota consommé.
"""
import io
from types import SimpleNamespace

import pytest
from sqlalchemy import func, select

from config import storage
from models.analysis import Analysis
from models.disease import Disease
from models.plant import Plant
from models.result import Result
from models.treatment import Treatment
from models.user import User
from PIL import Image
from services import analysis_service
from schemas.analysis import AnalysisCreate
from services.diagnosis_service import (
    DiagnosisImageRejectedError,
    DiagnosisUnavailableError,
    PlantDiagnosis,
)
from services.plantnet_service import (
    PlantIdentification,
    PlantNetUnavailableError,
    PlantNotRecognizedError,
)

EMAIL = "a@example.com"


def make_image(fmt="PNG", size=(64, 48)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, "green").save(buffer, fmt)
    return buffer.getvalue()


@pytest.fixture()
def uploads(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "UPLOADS_DIR", tmp_path / "uploads")
    return tmp_path / "uploads"


@pytest.fixture()
def catalogue(session):
    """Le verdict « Malade / Oïdium » existe en base (en production, c'est le rôle du seed)."""
    disease = Disease(name="Oïdium", treatments=[Treatment(advice="Retirer les feuilles atteintes.")])
    session.add(Result(label="Malade", disease=disease))
    session.commit()


@pytest.fixture()
def fakes(monkeypatch):
    """Faux Pl@ntNet et faux moteur IA : enregistrent leurs appels et peuvent être mis en erreur."""
    state = SimpleNamespace(
        identify_calls=[],
        diagnose_calls=[],
        identification=PlantIdentification("Monstera", "Monstera deliciosa", 0.73, "Araceae"),
        diagnosis=PlantDiagnosis("Oïdium", 0.69),
        identify_error=None,
        diagnose_error=None,
    )

    def identify(image, filename="image.jpg", content_type="image/jpeg", **kwargs):
        state.identify_calls.append(image)
        if state.identify_error:
            raise state.identify_error
        return state.identification

    def diagnose(image, filename="image.jpg", content_type="image/jpeg", **kwargs):
        state.diagnose_calls.append(image)
        if state.diagnose_error:
            raise state.diagnose_error
        return state.diagnosis

    monkeypatch.setattr(analysis_service, "identify_plant", identify)
    monkeypatch.setattr(analysis_service, "diagnose_plant", diagnose)
    return state


@pytest.fixture()
def headers(make_auth_headers):
    return make_auth_headers(EMAIL)


def post(client, headers, data=None, content_type="image/png", **form):
    data = make_image() if data is None else data
    return client.post(
        "/analysis", headers=headers, files={"image": ("photo.png", data, content_type)}, data=form
    )


def count(session, model) -> int:
    return session.scalar(select(func.count()).select_from(model))


def fichiers(uploads) -> list:
    return [p for p in uploads.rglob("*") if p.is_file()] if uploads.exists() else []


# --- Authentification ---------------------------------------------------------------

def test_sans_token_refuse(client, uploads, fakes):
    response = client.post("/analysis", files={"image": ("p.png", make_image(), "image/png")})

    assert response.status_code in (401, 403)
    assert fakes.identify_calls == []


# --- Cas nominal --------------------------------------------------------------------

def test_analyse_reussie(client, session, headers, uploads, catalogue, fakes):
    response = post(
        client, headers,
        plant_location="Intérieur", plant_exposition="Mi-ombre", plant_cultivation="En pot",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["plant"]["vernacular_name"] == "Monstera"
    assert body["plant"]["official_name"] == "Monstera deliciosa"
    assert body["plant"]["family"] == "Araceae"
    assert body["result"]["label"] == "Malade"
    assert body["result"]["disease"]["name"] == "Oïdium"
    assert body["result"]["disease"]["treatments"][0]["advice"] == "Retirer les feuilles atteintes."
    assert body["confidence"] == 0.69
    assert body["plant_location"] == "Intérieur"
    assert body["plant_exposition"] == "Mi-ombre"
    assert body["plant_cultivation"] == "En pot"
    assert body["date"].endswith("Z")  # heure UTC explicite : le navigateur la convertit en heure locale


def test_la_photo_est_enregistree_sous_id_utilisateur_et_id_analyse(
    client, session, headers, uploads, catalogue, fakes
):
    body = post(client, headers).json()

    id_user = session.scalar(select(User.id_user).where(User.email == EMAIL))
    path = uploads / str(id_user) / f"{body['id_analysis']}.jpg"
    assert path.is_file()
    assert path.read_bytes()[:3] == b"\xff\xd8\xff"  # signature d'un fichier JPEG
    assert [p for p in fichiers(uploads)] == [path]


def test_les_services_externes_recoivent_la_photo_normalisee(
    client, headers, uploads, catalogue, fakes
):
    """Même si l'utilisateur envoie un PNG, Pl@ntNet et le moteur reçoivent le JPEG normalisé."""
    post(client, headers, data=make_image("PNG"))

    assert fakes.identify_calls[0][:3] == b"\xff\xd8\xff"
    assert fakes.diagnose_calls[0] == fakes.identify_calls[0]


def test_le_contexte_est_facultatif(client, headers, uploads, catalogue, fakes):
    body = post(client, headers).json()

    assert body["plant_location"] is None
    assert body["plant_exposition"] is None
    assert body["plant_cultivation"] is None


def test_une_plante_deja_connue_est_reutilisee(client, session, headers, uploads, catalogue, fakes):
    post(client, headers)
    post(client, headers)

    assert count(session, Plant) == 1
    assert count(session, Analysis) == 2


def test_la_famille_est_completee_sur_une_plante_creee_avant_son_ajout(
    client, session, headers, uploads, catalogue, fakes
):
    session.add(Plant(vernacular_name="Monstera", official_name="Monstera deliciosa", family=None))
    session.commit()

    post(client, headers)

    assert session.scalar(select(Plant.family)) == "Araceae"
    assert count(session, Plant) == 1


# --- Contexte invalide --------------------------------------------------------------

@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("plant_location", "Cave"),
        ("plant_exposition", "Plein soleil"),
        ("plant_cultivation", "Hors-sol"),
    ],
)
def test_valeur_de_contexte_invalide(client, session, headers, uploads, catalogue, fakes, champ, valeur):
    response = post(client, headers, **{champ: valeur})

    assert response.status_code == 422
    assert fakes.identify_calls == []
    assert count(session, Analysis) == 0


def test_champ_image_manquant(client, headers, uploads, catalogue, fakes):
    response = client.post("/analysis", headers=headers, data={"plant_location": "Intérieur"})

    assert response.status_code == 422
    assert fakes.identify_calls == []


# --- Photo invalide : aucun appel externe (le quota Pl@ntNet est préservé) ----------

@pytest.mark.parametrize(
    "data, statut",
    [
        (b"", 422),
        (b"ceci n'est pas une image", 422),
        (make_image("PNG")[:30], 422),
        (make_image("GIF"), 415),
        (make_image("BMP"), 415),
    ],
    ids=["vide", "texte", "tronquee", "gif", "bmp"],
)
def test_photo_invalide(client, session, headers, uploads, catalogue, fakes, data, statut):
    response = post(client, headers, data=data)

    assert response.status_code == statut
    assert fakes.identify_calls == []
    assert fakes.diagnose_calls == []
    assert count(session, Analysis) == 0
    assert fichiers(uploads) == []


def test_photo_trop_volumineuse(client, session, headers, uploads, catalogue, fakes, monkeypatch):
    monkeypatch.setattr(storage, "MAX_UPLOAD_BYTES", 100)

    response = post(client, headers, data=make_image(size=(300, 300)))

    assert response.status_code == 413
    assert fakes.identify_calls == []
    assert count(session, Analysis) == 0


# --- Échecs des services externes : rien n'est enregistré ---------------------------

def test_plante_non_reconnue(client, session, headers, uploads, catalogue, fakes):
    fakes.identify_error = PlantNotRecognizedError()

    response = post(client, headers)

    assert response.status_code == 422
    assert "plante" in response.json()["detail"].lower()
    assert fakes.diagnose_calls == []  # inutile de solliciter le moteur IA
    assert count(session, Analysis) == 0
    assert count(session, Plant) == 0
    assert fichiers(uploads) == []


@pytest.mark.parametrize(
    "cible, erreur, statut",
    [
        ("identify_error", PlantNetUnavailableError(), 503),
        ("diagnose_error", DiagnosisUnavailableError(), 503),
        ("diagnose_error", DiagnosisImageRejectedError(), 422),
    ],
)
def test_echec_d_un_service_externe(
    client, session, headers, uploads, catalogue, fakes, cible, erreur, statut
):
    setattr(fakes, cible, erreur)

    response = post(client, headers)

    assert response.status_code == statut
    assert count(session, Analysis) == 0
    assert count(session, Plant) == 0
    assert fichiers(uploads) == []


def test_diagnostic_inconnu_de_la_base(client, session, headers, uploads, catalogue, fakes):
    fakes.diagnosis = PlantDiagnosis("Maladie imaginaire", 0.9)

    response = post(client, headers)

    assert response.status_code == 500
    assert "imaginaire" not in response.text  # aucun détail interne ne fuite vers l'utilisateur
    assert count(session, Analysis) == 0
    assert fichiers(uploads) == []


# --- Atomicité : base de données et fichier vont ensemble ---------------------------

def _creer_utilisateur(session) -> int:
    user = User(surname="Dupont", name="Jean", email=EMAIL, password="x")
    session.add(user)
    session.commit()
    return user.id_user


def test_echec_d_ecriture_du_fichier_annule_l_analyse(session, uploads, catalogue, fakes, monkeypatch):
    id_user = _creer_utilisateur(session)

    def disque_plein(*args, **kwargs):
        raise OSError("disque plein")

    monkeypatch.setattr(analysis_service, "save_image", disque_plein)

    with pytest.raises(OSError):
        analysis_service.run_analysis(
            session, id_user, make_image(), AnalysisCreate()
        )

    assert count(session, Analysis) == 0
    assert count(session, Plant) == 0


def test_echec_de_la_validation_en_base_supprime_le_fichier(
    session, uploads, catalogue, fakes, monkeypatch
):
    id_user = _creer_utilisateur(session)

    def commit_en_echec():
        raise RuntimeError("base indisponible")

    monkeypatch.setattr(session, "commit", commit_en_echec)

    with pytest.raises(RuntimeError):
        analysis_service.run_analysis(
            session, id_user, make_image(), AnalysisCreate()
        )

    assert fichiers(uploads) == []  # le fichier déjà écrit a été nettoyé


# --- GET /history/{id}/image --------------------------------------------------------

def test_image_servie_a_son_proprietaire(client, headers, uploads, catalogue, fakes):
    id_analysis = post(client, headers).json()["id_analysis"]

    response = client.get(f"/history/{id_analysis}/image", headers=headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content[:3] == b"\xff\xd8\xff"
    assert "private" in response.headers["cache-control"]


def test_image_sans_token_refusee(client, headers, uploads, catalogue, fakes):
    id_analysis = post(client, headers).json()["id_analysis"]

    assert client.get(f"/history/{id_analysis}/image").status_code in (401, 403)


def test_image_d_un_autre_utilisateur_renvoie_404(client, make_auth_headers, uploads, catalogue, fakes):
    headers_a = make_auth_headers("a@example.com")
    headers_b = make_auth_headers("b@example.com")
    id_a = post(client, headers_a).json()["id_analysis"]

    assert client.get(f"/history/{id_a}/image", headers=headers_b).status_code == 404


def test_image_d_une_analyse_inexistante(client, headers, uploads):
    assert client.get("/history/9999/image", headers=headers).status_code == 404


def test_fichier_image_manquant_renvoie_404(client, headers, uploads, catalogue, fakes):
    id_analysis = post(client, headers).json()["id_analysis"]
    for fichier in fichiers(uploads):
        fichier.unlink()

    assert client.get(f"/history/{id_analysis}/image", headers=headers).status_code == 404
