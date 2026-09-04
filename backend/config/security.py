import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not _SECRET_KEY:
    raise RuntimeError(
        "Variable d'environnement manquante : JWT_SECRET_KEY. "
        "Merci de se référer au fichier .env.example."
    )
JWT_SECRET_KEY = _SECRET_KEY

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

try:
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
except ValueError:
    raise RuntimeError(
        "JWT_EXPIRE_MINUTES invalide : doit être un nombre entier. "
        "Merci de se référer au fichier .env.example."
    )

ACCESS_TOKEN_EXPIRE = timedelta(minutes=JWT_EXPIRE_MINUTES)