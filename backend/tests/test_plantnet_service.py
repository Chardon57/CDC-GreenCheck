"""Tests de services/plantnet_service.py.

Pl@ntNet est simulé avec httpx2.MockTransport : aucun appel réseau, aucun quota consommé.
La réponse de référence est une vraie réponse de l'API (photo d'une Monstera).
"""
import copy
import logging

import httpx2
import pytest

from config.plantnet import PLANTNET_API_KEY
from services.plantnet_service import (
    PlantIdentification,
    PlantNetUnavailableError,
    PlantNotRecognizedError,
    identify_plant,
)

REAL_RESPONSE = {
    "query": {"project": "all", "images": ["5e13dc833fb93577666835f6a5323b87"], "organs": ["auto"]},
    "predictedOrgans": [{"organ": "leaf", "score": 0.85562}],
    "language": "fr",
    "bestMatch": "Monstera deliciosa Liebm.",
    "results": [
        {
            "score": 0.73534,
            "species": {
                "scientificNameWithoutAuthor": "Monstera deliciosa",
                "scientificNameAuthorship": "Liebm.",
                "genus": {"scientificNameWithoutAuthor": "Monstera"},
                "family": {"scientificNameWithoutAuthor": "Araceae"},
                "commonNames": ["Monstera", "Ananas du pauvre", "Cériman"],
                "scientificName": "Monstera deliciosa Liebm.",
            },
            "gbif": {"id": "2868241"},
            "powo": {"id": "87478-1"},
        }
    ],
    "version": "2026-03-20 (7.5)",
    "remainingIdentificationRequests": 499,
}

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

def test_identification_reussie():
    result = identify_plant(IMAGE, client=client_returning(json=REAL_RESPONSE))

    assert result == PlantIdentification(
        vernacular_name="Monstera",
        official_name="Monstera deliciosa",  # sans le nom d'auteur "Liebm."
        score=0.73534,
        family="Araceae",  # famille botanique (latin), telle que fournie par Pl@ntNet
    )


def test_famille_absente_de_la_reponse():
    data = copy.deepcopy(REAL_RESPONSE)
    del data["results"][0]["species"]["family"]

    result = identify_plant(IMAGE, client=client_returning(json=data))

    assert result.family is None
    assert result.official_name == "Monstera deliciosa"  # le reste de l'identification est intact


def test_famille_nulle_dans_la_reponse():
    data = copy.deepcopy(REAL_RESPONSE)
    data["results"][0]["species"]["family"] = None

    assert identify_plant(IMAGE, client=client_returning(json=data)).family is None


def test_la_requete_envoyee_a_plantnet_est_correcte():
    envoyees = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        envoyees.append(request)
        return httpx2.Response(200, json=REAL_RESPONSE)

    client = httpx2.Client(transport=httpx2.MockTransport(handler))
    identify_plant(IMAGE, filename="ma_plante.jpg", client=client)

    (request,) = envoyees
    assert request.method == "POST"
    assert request.url.path == "/v2/identify/all"
    assert request.url.params["api-key"] == PLANTNET_API_KEY
    assert request.url.params["lang"] == "fr"
    assert request.url.params["nb-results"] == "1"
    assert request.headers["content-type"].startswith("multipart/form-data")
    assert b'name="images"' in request.content
    assert b'filename="ma_plante.jpg"' in request.content
    assert IMAGE in request.content


def test_sans_nom_courant_on_retombe_sur_le_nom_scientifique():
    data = copy.deepcopy(REAL_RESPONSE)
    data["results"][0]["species"]["commonNames"] = []

    result = identify_plant(IMAGE, client=client_returning(json=data))

    assert result.vernacular_name == "Monstera deliciosa"


# --- Plante non reconnue ------------------------------------------------------------

def test_liste_de_resultats_vide():
    data = {**REAL_RESPONSE, "results": []}

    with pytest.raises(PlantNotRecognizedError):
        identify_plant(IMAGE, client=client_returning(json=data))


def test_score_trop_faible():
    data = copy.deepcopy(REAL_RESPONSE)
    data["results"][0]["score"] = 0.01

    with pytest.raises(PlantNotRecognizedError):
        identify_plant(IMAGE, client=client_returning(json=data))


def test_http_404_signifie_aucune_plante_identifiable():
    with pytest.raises(PlantNotRecognizedError):
        identify_plant(IMAGE, client=client_returning(404, json={"message": "Species not found"}))


# --- Pl@ntNet indisponible ou mal configuré ----------------------------------------

@pytest.mark.parametrize("status_code", [401, 403, 429, 500, 502, 503])
def test_erreurs_http_de_plantnet(status_code):
    with pytest.raises(PlantNetUnavailableError):
        identify_plant(IMAGE, client=client_returning(status_code, json={"error": "..."}))


def test_timeout():
    client = client_raising(lambda request: httpx2.ReadTimeout("timed out", request=request))

    with pytest.raises(PlantNetUnavailableError):
        identify_plant(IMAGE, client=client)


def test_reseau_injoignable():
    client = client_raising(lambda request: httpx2.ConnectError("connexion refusée", request=request))

    with pytest.raises(PlantNetUnavailableError):
        identify_plant(IMAGE, client=client)


def test_reponse_200_qui_nest_pas_du_json():
    with pytest.raises(PlantNetUnavailableError):
        identify_plant(IMAGE, client=client_returning(200, content=b"<html>pas du json</html>"))


@pytest.mark.parametrize(
    "data",
    [
        {},  # pas de clé "results"
        {"results": [{"score": 0.9}]},  # pas de "species"
        {"results": [{"score": 0.9, "species": {}}]},  # pas de nom scientifique
        {"results": [{"score": "abc", "species": {"scientificNameWithoutAuthor": "X"}}]},  # score illisible
        {"results": "texte"},  # mauvais type
    ],
)
def test_structure_de_reponse_inattendue(data):
    with pytest.raises(PlantNetUnavailableError):
        identify_plant(IMAGE, client=client_returning(json=data))


# --- La clé API ne doit jamais fuiter -----------------------------------------------

def test_la_cle_api_ne_fuite_ni_dans_lexception_ni_dans_les_logs(caplog):
    """Même si l'erreur d'origine contient l'URL (donc la clé), rien ne doit en ressortir."""
    caplog.set_level(logging.DEBUG)
    client = client_raising(
        lambda request: httpx2.ReadTimeout(f"timeout sur {request.url}", request=request)
    )

    with pytest.raises(PlantNetUnavailableError) as excinfo:
        identify_plant(IMAGE, client=client)

    assert PLANTNET_API_KEY not in str(excinfo.value)
    assert PLANTNET_API_KEY not in repr(excinfo.value)
    assert excinfo.value.__suppress_context__ is True  # l'erreur d'origine n'apparaît pas dans la traceback
    assert PLANTNET_API_KEY not in caplog.text
