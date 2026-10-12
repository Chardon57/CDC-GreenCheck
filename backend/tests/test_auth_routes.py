"""Tests d'intégration des routes /auth (requêtes HTTP simulées, base SQLite)."""
from datetime import datetime, timedelta, timezone

import jwt

from config.security import JWT_ALGORITHM, JWT_SECRET_KEY


# --- POST /auth/register ----------------------------------------------------------

def test_register_succes_renvoie_201_sans_mot_de_passe(client, user_payload):
    response = client.post("/auth/register", json=user_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == user_payload["email"]
    assert "id_user" in body
    assert "password" not in body  # le hash ne doit jamais sortir de l'API


def test_register_email_deja_utilise_renvoie_409(client, user_payload):
    client.post("/auth/register", json=user_payload)

    response = client.post("/auth/register", json=user_payload)

    assert response.status_code == 409


def test_register_mot_de_passe_trop_court_renvoie_422(client, user_payload):
    user_payload["password"] = "court"

    response = client.post("/auth/register", json=user_payload)

    assert response.status_code == 422


def test_register_email_invalide_renvoie_422(client, user_payload):
    user_payload["email"] = "pas-un-email"

    response = client.post("/auth/register", json=user_payload)

    assert response.status_code == 422


def test_register_champ_manquant_renvoie_422(client, user_payload):
    del user_payload["surname"]

    response = client.post("/auth/register", json=user_payload)

    assert response.status_code == 422


# --- POST /auth/login -------------------------------------------------------------

def test_login_succes_renvoie_un_token_bearer(client, user_payload):
    client.post("/auth/register", json=user_payload)

    response = client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_mauvais_mot_de_passe_renvoie_401(client, user_payload):
    client.post("/auth/register", json=user_payload)

    response = client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": "mauvais_mot_de_passe"},
    )

    assert response.status_code == 401


def test_login_email_inconnu_renvoie_401(client):
    response = client.post(
        "/auth/login",
        json={"email": "inconnu@example.com", "password": "motdepasse123"},
    )

    assert response.status_code == 401


def test_login_anti_enumeration_meme_reponse_pour_email_inconnu_et_mauvais_mot_de_passe(
    client, user_payload
):
    """Un attaquant ne doit pas pouvoir deviner quels e-mails sont inscrits."""
    client.post("/auth/register", json=user_payload)

    mauvais_mdp = client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": "mauvais_mot_de_passe"},
    )
    email_inconnu = client.post(
        "/auth/login",
        json={"email": "inconnu@example.com", "password": "motdepasse123"},
    )

    assert mauvais_mdp.status_code == email_inconnu.status_code == 401
    assert mauvais_mdp.json() == email_inconnu.json()


# --- GET /auth/me -----------------------------------------------------------------

def test_me_avec_token_valide_renvoie_lutilisateur(client, user_payload, make_auth_headers):
    headers = make_auth_headers(user_payload["email"])

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == user_payload["email"]
    assert "password" not in body


def test_me_sans_token_est_refuse(client):
    response = client.get("/auth/me")

    # HTTPBearer répond 401 ou 403 selon la version de FastAPI/Starlette :
    # dans les deux cas l'accès doit être refusé.
    assert response.status_code in (401, 403)


def test_me_avec_token_invalide_renvoie_401(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer ceci-n-est-pas-un-jwt"})

    assert response.status_code == 401


def test_me_avec_token_expire_renvoie_401(client, make_auth_headers):
    make_auth_headers()
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401


def test_me_avec_token_dun_utilisateur_inexistant_renvoie_401(client):
    ghost = jwt.encode(
        {"sub": "9999", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {ghost}"})

    assert response.status_code == 401
