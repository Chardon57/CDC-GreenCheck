import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_BACKEND_DIR = Path(__file__).resolve().parent.parent

# Dossier où sont rangées les photos des utilisateurs : <UPLOADS_DIR>/<id_user>/<id_analysis>.jpg
_uploads = Path(os.getenv("UPLOADS_DIR", "uploads"))
# Un chemin relatif est interprété par rapport au dossier backend/ (et non au dossier d'où l'on lance uvicorn).
UPLOADS_DIR = _uploads if _uploads.is_absolute() else _BACKEND_DIR / _uploads


def _float_from_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        raise RuntimeError(
            f"{name} invalide : doit être un nombre. "
            "Merci de se référer au fichier .env.example."
        )


# Taille maximale d'une photo envoyée par l'utilisateur (la variable est exprimée en Mo).
MAX_UPLOAD_BYTES = int(_float_from_env("MAX_UPLOAD_MB", 10.0) * 1024 * 1024)

# Après réception, la photo est réduite (si besoin) pour que son plus grand côté ne dépasse pas
# cette valeur (en pixels), puis enregistrée en JPEG de cette qualité (1 à 95).
IMAGE_MAX_SIDE = 1600
JPEG_QUALITY = 88
