"""Tests du CORS : le navigateur ne doit autoriser que le frontend connu à appeler l'API.

Le navigateur envoie d'abord une requête « de pré-vérification » (méthode OPTIONS) pour demander
la permission ; on la simule ici avec les en-têtes que Chrome ou Firefox enverraient.
"""
import pytest

from config.cors import CORS_ORIGINS

FRONTEND = "http://localhost:5173"


def _preflight(client, origin, method="GET", headers="authorization"):
    return client.options(
        "/history",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": headers,
        },
    )


def test_le_frontend_de_developpement_est_autorise_par_defaut():
    assert FRONTEND in CORS_ORIGINS


@pytest.mark.parametrize("method", ["GET", "POST", "DELETE"])
def test_preflight_du_frontend_accepte(client, method):
    response = _preflight(client, FRONTEND, method)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND
    assert method in response.headers["access-control-allow-methods"]
    assert "authorization" in response.headers["access-control-allow-headers"].lower()


def test_preflight_dune_origine_inconnue_refuse(client):
    response = _preflight(client, "http://site-malveillant.example")

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_reponse_normale_porte_lentete_pour_le_frontend(client):
    response = client.get("/", headers={"Origin": FRONTEND})

    assert response.headers["access-control-allow-origin"] == FRONTEND


def test_reponse_normale_sans_en_tete_pour_une_origine_inconnue(client):
    response = client.get("/", headers={"Origin": "http://site-malveillant.example"})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_les_cookies_ne_sont_pas_autorises(client):
    """Le jeton passe par l'en-tête Authorization : pas besoin d'autoriser les cookies cross-origin."""
    response = _preflight(client, FRONTEND)

    assert "access-control-allow-credentials" not in response.headers
