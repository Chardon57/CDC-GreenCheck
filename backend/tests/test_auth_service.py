"""Tests unitaires de services/auth_service.py (sans passer par HTTP)."""
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from sqlalchemy import select

from config.security import JWT_ALGORITHM, JWT_SECRET_KEY
from models.user import User
from schemas.user import UserCreate
from services.auth_service import (
    EmailAlreadyExistsError,
    ExpiredTokenError,
    InvalidCredentialsError,
    InvalidTokenError,
    authenticate_user,
    create_access_token,
    decode_access_token,
    hash_password,
    register_user,
    verify_password,
)


# --- Hachage des mots de passe -------------------------------------------------

def test_hash_password_utilise_argon2id():
    assert hash_password("motdepasse123").startswith("$argon2id$")


def test_hash_password_ne_contient_pas_le_mot_de_passe_en_clair():
    assert "motdepasse123" not in hash_password("motdepasse123")


def test_hash_password_est_sale_deux_hash_du_meme_mot_de_passe_different():
    assert hash_password("motdepasse123") != hash_password("motdepasse123")


def test_verify_password_accepte_le_bon_mot_de_passe():
    hashed = hash_password("motdepasse123")
    assert verify_password("motdepasse123", hashed) is True


def test_verify_password_refuse_un_mauvais_mot_de_passe():
    hashed = hash_password("motdepasse123")
    assert verify_password("autre_mot_de_passe", hashed) is False


# --- Inscription -----------------------------------------------------------------

def test_register_user_enregistre_un_hash_et_non_le_mot_de_passe(session, user_payload):
    user = register_user(session, UserCreate(**user_payload))

    assert user.id_user is not None
    assert user.password != user_payload["password"]
    assert user.password.startswith("$argon2id$")


def test_register_user_refuse_un_email_deja_utilise(session, user_payload):
    register_user(session, UserCreate(**user_payload))

    with pytest.raises(EmailAlreadyExistsError):
        register_user(session, UserCreate(**user_payload))

    # Aucun doublon n'a été créé en base
    assert len(session.scalars(select(User)).all()) == 1


# --- Authentification ------------------------------------------------------------

def test_authenticate_user_renvoie_lutilisateur_avec_de_bons_identifiants(session, user_payload):
    register_user(session, UserCreate(**user_payload))

    user = authenticate_user(session, user_payload["email"], user_payload["password"])

    assert user.email == user_payload["email"]


def test_authenticate_user_mauvais_mot_de_passe(session, user_payload):
    register_user(session, UserCreate(**user_payload))

    with pytest.raises(InvalidCredentialsError):
        authenticate_user(session, user_payload["email"], "mauvais_mot_de_passe")


def test_authenticate_user_email_inconnu(session):
    with pytest.raises(InvalidCredentialsError):
        authenticate_user(session, "inconnu@example.com", "motdepasse123")


# --- Jetons JWT ------------------------------------------------------------------

def test_create_access_token_contient_sub_et_exp():
    token = create_access_token({"sub": "42"})
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

    assert payload["sub"] == "42"
    assert "exp" in payload


def test_create_access_token_ne_modifie_pas_le_dictionnaire_fourni():
    data = {"sub": "42"}
    create_access_token(data)
    assert data == {"sub": "42"}


def test_decode_access_token_aller_retour():
    token = create_access_token({"sub": "42"})
    assert decode_access_token(token)["sub"] == "42"


def test_decode_access_token_token_expire():
    expired = jwt.encode(
        {"sub": "42", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    with pytest.raises(ExpiredTokenError):
        decode_access_token(expired)


def test_decode_access_token_signature_falsifiee():
    forged = jwt.encode(
        {"sub": "42", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "une-autre-cle-secrete-de-32-octets-minimum",
        algorithm=JWT_ALGORITHM,
    )
    with pytest.raises(InvalidTokenError):
        decode_access_token(forged)


def test_decode_access_token_texte_quelconque():
    with pytest.raises(InvalidTokenError):
        decode_access_token("ceci-n-est-pas-un-jwt")
