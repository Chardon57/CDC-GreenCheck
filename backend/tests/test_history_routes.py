"""Tests d'intégration des routes /history (liste, détail, isolation entre utilisateurs)."""
from datetime import datetime

import pytest
from sqlalchemy import func, select

from config import storage

from models.analysis import Analysis
from models.disease import Disease
from models.plant import Plant
from models.result import Result
from models.treatment import Treatment
from models.user import User
from services import history_service, image_service


def _creer_analyse(
    session, email: str, date: datetime, plante="Monstera", etat="Attention", maladie="Excès d'arrosage",
    famille=None, culture=None,
):
    """Insère une analyse complète (plante, maladie + conseils, résultat) pour l'utilisateur `email`."""
    user = session.scalar(select(User).where(User.email == email))
    plant = Plant(vernacular_name=plante, official_name=f"{plante} officinalis", family=famille)
    treatment = Treatment(advice="Réduire la fréquence d'arrosage.")
    disease = session.scalar(select(Disease).where(Disease.name == maladie))
    if disease is None:
        disease = Disease(name=maladie, treatments=[treatment])
    result = Result(label=etat, disease=disease)
    analysis = Analysis(
        date=date,
        plant_location="Salon",
        plant_exposition="Lumière indirecte",
        plant_cultivation=culture,
        confidence=0.87,
        user=user,
        plant=plant,
        result=result,
    )
    session.add(analysis)
    session.commit()
    return analysis.id_analysis


# --- Authentification obligatoire ---------------------------------------------------

def test_history_sans_token_est_refuse(client):
    assert client.get("/history").status_code in (401, 403)


def test_history_detail_sans_token_est_refuse(client):
    assert client.get("/history/1").status_code in (401, 403)


# --- GET /history ------------------------------------------------------------------

def test_history_vide_pour_un_nouvel_utilisateur(client, make_auth_headers):
    headers = make_auth_headers()

    response = client.get("/history", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


def test_history_renvoie_les_analyses_avec_plante_etat_maladie_et_conseils(
    client, session, make_auth_headers
):
    headers = make_auth_headers("a@example.com")
    _creer_analyse(session, "a@example.com", datetime(2026, 6, 22, 14, 32))

    response = client.get("/history", headers=headers)

    assert response.status_code == 200
    (item,) = response.json()
    assert item["plant"]["vernacular_name"] == "Monstera"
    assert item["result"]["label"] == "Attention"  # l'état affiché dans l'historique
    assert item["result"]["disease"]["name"] == "Excès d'arrosage"
    assert item["confidence"] == 0.87
    # Sérialisation imbriquée : résultat -> maladie -> conseils
    (treatment,) = item["result"]["disease"]["treatments"]
    assert treatment["advice"] == "Réduire la fréquence d'arrosage."
    assert "id_treatment" in treatment  # régression sur l'ancienne coquille id_treatmentt


def test_history_expose_la_famille_de_la_plante_et_le_type_de_culture(client, session, make_auth_headers):
    headers = make_auth_headers("a@example.com")
    _creer_analyse(
        session, "a@example.com", datetime(2026, 6, 22), famille="Araceae", culture="En pot"
    )

    (item,) = client.get("/history", headers=headers).json()

    assert item["plant"]["family"] == "Araceae"
    assert item["plant_cultivation"] == "En pot"


def test_history_anciennes_analyses_sans_famille_ni_type_de_culture(client, session, make_auth_headers):
    """Les lignes créées avant l'ajout des colonnes valent NULL : elles doivent rester lisibles."""
    headers = make_auth_headers("a@example.com")
    _creer_analyse(session, "a@example.com", datetime(2026, 6, 22))

    (item,) = client.get("/history", headers=headers).json()

    assert item["plant"]["family"] is None
    assert item["plant_cultivation"] is None


def test_history_tri_de_la_plus_recente_a_la_plus_ancienne(client, session, make_auth_headers):
    headers = make_auth_headers("a@example.com")
    ancienne = _creer_analyse(session, "a@example.com", datetime(2026, 1, 1))
    recente = _creer_analyse(session, "a@example.com", datetime(2026, 6, 1))
    milieu = _creer_analyse(session, "a@example.com", datetime(2026, 3, 1))

    ids = [item["id_analysis"] for item in client.get("/history", headers=headers).json()]

    assert ids == [recente, milieu, ancienne]


def test_history_ne_renvoie_que_les_analyses_de_lutilisateur_connecte(
    client, session, make_auth_headers
):
    headers_a = make_auth_headers("a@example.com")
    make_auth_headers("b@example.com")
    id_a = _creer_analyse(session, "a@example.com", datetime(2026, 6, 1))
    _creer_analyse(session, "b@example.com", datetime(2026, 6, 2))

    ids = [item["id_analysis"] for item in client.get("/history", headers=headers_a).json()]

    assert ids == [id_a]


# --- GET /history/{id_analysis} --------------------------------------------------

def test_history_detail_renvoie_lanalyse(client, session, make_auth_headers):
    headers = make_auth_headers("a@example.com")
    id_analysis = _creer_analyse(session, "a@example.com", datetime(2026, 6, 22, 14, 32))

    response = client.get(f"/history/{id_analysis}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id_analysis"] == id_analysis


def test_history_detail_inexistant_renvoie_404(client, make_auth_headers):
    headers = make_auth_headers()

    assert client.get("/history/9999", headers=headers).status_code == 404


def test_history_detail_dun_autre_utilisateur_renvoie_404_et_non_403(
    client, session, make_auth_headers
):
    """Un 403 confirmerait l'existence de l'analyse : on répond 404, comme si elle n'existait pas."""
    make_auth_headers("a@example.com")
    headers_b = make_auth_headers("b@example.com")
    id_a = _creer_analyse(session, "a@example.com", datetime(2026, 6, 1))

    inexistant = client.get("/history/9999", headers=headers_b)
    autre_utilisateur = client.get(f"/history/{id_a}", headers=headers_b)

    assert autre_utilisateur.status_code == 404
    assert autre_utilisateur.json() == inexistant.json()  # indiscernable d'une analyse inexistante


# --- DELETE /history/{id_analysis} -----------------------------------------------

@pytest.fixture()
def uploads(tmp_path, monkeypatch):
    """Dossier de photos temporaire : les tests n'écrivent jamais dans le vrai dossier uploads/."""
    monkeypatch.setattr(storage, "UPLOADS_DIR", tmp_path)
    return tmp_path


def _poser_photo(uploads, id_user: int, id_analysis: int):
    path = image_service.save_image(b"jpeg-factice", id_user, id_analysis)
    assert path.is_file()
    return path


def _id_user(session, email: str) -> int:
    return session.scalar(select(User.id_user).where(User.email == email))


def test_suppression_sans_token_est_refusee(client):
    assert client.delete("/history/1").status_code in (401, 403)


def test_suppression_retire_lanalyse_et_sa_photo(client, session, make_auth_headers, uploads):
    headers = make_auth_headers("a@example.com")
    id_analysis = _creer_analyse(session, "a@example.com", datetime(2026, 6, 1))
    photo = _poser_photo(uploads, _id_user(session, "a@example.com"), id_analysis)

    response = client.delete(f"/history/{id_analysis}", headers=headers)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/history/{id_analysis}", headers=headers).status_code == 404
    assert client.get("/history", headers=headers).json() == []
    assert not photo.exists()


def test_suppression_conserve_la_plante_et_le_catalogue(client, session, make_auth_headers, uploads):
    """Seule la ligne Analysis disparaît : la plante, le résultat et la maladie ne sont pas touchés."""
    headers = make_auth_headers("a@example.com")
    id_analysis = _creer_analyse(session, "a@example.com", datetime(2026, 6, 1))

    assert client.delete(f"/history/{id_analysis}", headers=headers).status_code == 204

    session.expire_all()
    assert session.scalar(select(func.count()).select_from(Plant)) == 1
    assert session.scalar(select(func.count()).select_from(Result)) == 1
    assert session.scalar(select(func.count()).select_from(Disease)) == 1


def test_suppression_ne_touche_pas_aux_autres_analyses(client, session, make_auth_headers, uploads):
    headers = make_auth_headers("a@example.com")
    id_user = None
    a_supprimer = _creer_analyse(session, "a@example.com", datetime(2026, 6, 1))
    a_garder = _creer_analyse(session, "a@example.com", datetime(2026, 6, 2))
    id_user = _id_user(session, "a@example.com")
    _poser_photo(uploads, id_user, a_supprimer)
    photo_gardee = _poser_photo(uploads, id_user, a_garder)

    assert client.delete(f"/history/{a_supprimer}", headers=headers).status_code == 204

    assert [i["id_analysis"] for i in client.get("/history", headers=headers).json()] == [a_garder]
    assert photo_gardee.is_file()


def test_suppression_inexistante_renvoie_404(client, make_auth_headers, uploads):
    headers = make_auth_headers()

    assert client.delete("/history/9999", headers=headers).status_code == 404


def test_suppression_de_lanalyse_dun_autre_utilisateur_est_impossible(
    client, session, make_auth_headers, uploads
):
    """Réponse identique à une analyse inexistante, et rien n'est supprimé (ni ligne ni photo)."""
    headers_a = make_auth_headers("a@example.com")
    headers_b = make_auth_headers("b@example.com")
    id_a = _creer_analyse(session, "a@example.com", datetime(2026, 6, 1))
    photo = _poser_photo(uploads, _id_user(session, "a@example.com"), id_a)

    inexistant = client.delete("/history/9999", headers=headers_b)
    autre_utilisateur = client.delete(f"/history/{id_a}", headers=headers_b)

    assert autre_utilisateur.status_code == 404
    assert autre_utilisateur.json() == inexistant.json()
    assert client.get(f"/history/{id_a}", headers=headers_a).status_code == 200
    assert photo.is_file()


def test_suppression_sans_fichier_photo_reussit(client, session, make_auth_headers, uploads):
    """Une analyse dont la photo a déjà disparu doit rester supprimable."""
    headers = make_auth_headers("a@example.com")
    id_analysis = _creer_analyse(session, "a@example.com", datetime(2026, 6, 1))

    assert client.delete(f"/history/{id_analysis}", headers=headers).status_code == 204


def test_suppression_reussit_meme_si_la_photo_ne_peut_etre_effacee(
    client, session, make_auth_headers, uploads, monkeypatch
):
    """La base fait foi : une erreur disque ne doit pas faire échouer la suppression."""
    headers = make_auth_headers("a@example.com")
    id_analysis = _creer_analyse(session, "a@example.com", datetime(2026, 6, 1))

    def echec(*args, **kwargs):
        raise PermissionError("disque en lecture seule")

    monkeypatch.setattr(history_service, "delete_image", echec)

    assert client.delete(f"/history/{id_analysis}", headers=headers).status_code == 204
    assert client.get(f"/history/{id_analysis}", headers=headers).status_code == 404
