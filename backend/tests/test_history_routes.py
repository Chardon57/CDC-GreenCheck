"""Tests d'intégration des routes /history (liste, détail, isolation entre utilisateurs)."""
from datetime import datetime

from sqlalchemy import select

from models.analysis import Analysis
from models.plant import Plant
from models.result import Result
from models.treatment import Treatment
from models.user import User


def _creer_analyse(session, email: str, date: datetime, plante="Monstera", diagnostic="Excès d'arrosage"):
    """Insère une analyse complète (plante, résultat, traitement) pour l'utilisateur `email`."""
    user = session.scalar(select(User).where(User.email == email))
    plant = Plant(vernacular_name=plante, official_name=f"{plante} officinalis")
    treatment = Treatment(advice="Réduire la fréquence d'arrosage.")
    result = Result(label=diagnostic, treatments=[treatment])
    analysis = Analysis(
        date=date,
        plant_location="Salon",
        plant_exposition="Lumière indirecte",
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


def test_history_renvoie_les_analyses_avec_plante_resultat_et_traitements(
    client, session, make_auth_headers
):
    headers = make_auth_headers("a@example.com")
    _creer_analyse(session, "a@example.com", datetime(2026, 6, 22, 14, 32))

    response = client.get("/history", headers=headers)

    assert response.status_code == 200
    (item,) = response.json()
    assert item["plant"]["vernacular_name"] == "Monstera"
    assert item["result"]["label"] == "Excès d'arrosage"
    assert item["confidence"] == 0.87
    # Sérialisation imbriquée du traitement (régression sur la coquille id_treatmentt)
    assert item["result"]["treatments"][0]["advice"] == "Réduire la fréquence d'arrosage."
    assert "id_treatment" in item["result"]["treatments"][0]


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
