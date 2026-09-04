from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import jwt


from models.user import User
from schemas.user import UserCreate

from config.security import ACCESS_TOKEN_EXPIRE, JWT_ALGORITHM, JWT_SECRET_KEY

#                           Création de l'utilisateur
# -------------------------------------------------------------------------------------
_hasher = PasswordHasher()


class EmailAlreadyExistsError(Exception):
    """Levée quand un utilisateur tente de s'inscrire avec un e-mail déjà utilisé."""


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, password)
    except VerifyMismatchError:
        return False


def register_user(session: Session, user_data: UserCreate) -> User:
    existing = session.scalar(select(User).where(User.email == user_data.email))
    if existing is not None:
        raise EmailAlreadyExistsError()

    user = User(
        surname=user_data.surname,
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

#                         Authentification de l'utilisateur
# -------------------------------------------------------------------------------------

class InvalidCredentialsError(Exception):
    """Levée quand l'e-mail ou le mot de passe fourni est incorrect."""


def authenticate_user(session: Session, email: str, password: str) -> User:
    user = session.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(password, user.password):
        raise InvalidCredentialsError()
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

#                     Vérification de connexion de l'utilisateur
# -------------------------------------------------------------------------------------

class ExpiredTokenError(Exception):
    """Levée quand le token JWT a expiré."""


class InvalidTokenError(Exception):
    """Levée quand le token JWT est invalide (signature incorrecte, format corrompu...)."""


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()