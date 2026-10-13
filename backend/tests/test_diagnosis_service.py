"""Tests de services/diagnosis_service.py.

Le moteur IA est simulé avec httpx2.MockTransport : aucun appel réseau, le vrai moteur
n'a pas besoin d'être lancé.
"""
import httpx2
import pytest

from config.engine import ENGINE_URL
from services.diagnosis_service import (
    DiagnosisImageRejectedError,
    DiagnosisUnavailableError,
    PlantDiagnosis,
    diagnose_plant,
)

# Réponse réelle du moteur (photo de feuille atteinte d'oïdium)
REAL_RESPONSE = {"label": "Oïdium", "confidence": 0.6861112713813782}

IMAGE = b"\xff\xd8\xff\xe0-faux-contenu-jpeg"


def client_returning(status_code=200, json=None, content=None):
    """Client HTTP dont toutes les requêtes reçoivent la même réponse prédéfinie."""

    def handler(request: httpx2.Request) -> httpx2.Response:
        if content is not None:
            return httpx2.Response(status_code, content=content)
        return httpx2.Response(status_code, json=json)

    return httpx2.Client(transport=httpx2.MockTransport(handler))


def client_raising(exception_factory):
    def handler(request: httpx2.Request):
        raise exception_factory(request)

    return httpx2.Client(transport=httpx2.MockTransport(handler))


# --- Cas nominal --------------------------------------------------------------------

def test_diagnostic_reussi():
    result = diagnose_plant(IMAGE, client=client_returning(json=REAL_RESPONSE))

    assert result == PlantDiagnosis(label="Oïdium", confidence=0.6861112713813782)


def test_la_requete_envoyee_au_moteur_est_correcte():
    envoyees = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        envoyees.append(request)
        return httpx2.Response(200, json=REAL_RESPONSE)

    client = httpx2.Client(transport=httpx2.MockTransport(handler))
    diagnose_plant(IMAGE, filename="ma_plante.png", content_type="image/png", client=client)

    (request,) = envoyees
    assert request.method == "POST"
    assert str(request.url) == f"{ENGINE_URL}/diagnose"
    assert request.headers["content-type"].startswith("multipart/form-data")
    assert b'name="image"' in request.content
    assert b'filename="ma_plante.png"' in request.content
    assert b"image/png" in request.content
    assert IMAGE in request.content


def test_confiance_aux_bornes_acceptee():
    for valeur in (0.0, 1.0):
        data = {"label": "Rouille", "confidence": valeur}
        assert diagnose_plant(IMAGE, client=client_returning(json=data)).confidence == valeur


# --- Image refusée par le moteur ----------------------------------------------------

@pytest.mark.parametrize("status", [413, 415, 422])
def test_image_refusee(status):
    client = client_returning(status, json={"detail": "refusée"})

    with pytest.raises(DiagnosisImageRejectedError):
        diagnose_plant(IMAGE, client=client)


# --- Moteur indisponible ------------------------------------------------------------

@pytest.mark.parametrize("status", [404, 500, 502, 503])
def test_statut_http_inattendu(status):
    with pytest.raises(DiagnosisUnavailableError):
        diagnose_plant(IMAGE, client=client_returning(status, json={}))


def test_moteur_eteint():
    client = client_raising(lambda request: httpx2.ConnectError("refusé", request=request))

    with pytest.raises(DiagnosisUnavailableError):
        diagnose_plant(IMAGE, client=client)


def test_delai_depasse():
    client = client_raising(lambda request: httpx2.ReadTimeout("trop long", request=request))

    with pytest.raises(DiagnosisUnavailableError):
        diagnose_plant(IMAGE, client=client)


# --- Réponse inexploitable ----------------------------------------------------------

@pytest.mark.parametrize(
    "json",
    [
        {},
        {"label": "Oïdium"},
        {"confidence": 0.5},
        {"label": "", "confidence": 0.5},
        {"label": "   ", "confidence": 0.5},
        {"label": 12, "confidence": 0.5},
        {"label": "Oïdium", "confidence": "beaucoup"},
        {"label": "Oïdium", "confidence": None},
        {"label": "Oïdium", "confidence": 1.5},
        {"label": "Oïdium", "confidence": -0.1},
        [],
    ],
)
def test_reponse_json_invalide(json):
    with pytest.raises(DiagnosisUnavailableError):
        diagnose_plant(IMAGE, client=client_returning(json=json))


def test_reponse_non_json():
    with pytest.raises(DiagnosisUnavailableError):
        diagnose_plant(IMAGE, client=client_returning(content=b"<html>erreur</html>"))
