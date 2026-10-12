import os

from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("PLANTNET_API_KEY")
if not _API_KEY:
    raise RuntimeError(
        "Variable d'environnement manquante : PLANTNET_API_KEY. "
        "Merci de se référer au fichier .env.example."
    )
PLANTNET_API_KEY = _API_KEY

PLANTNET_BASE_URL = os.getenv("PLANTNET_BASE_URL", "https://my-api.plantnet.org")


def _float_from_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        raise RuntimeError(
            f"{name} invalide : doit être un nombre. "
            "Merci de se référer au fichier .env.example."
        )

PLANTNET_TIMEOUT = _float_from_env("PLANTNET_TIMEOUT", 15.0)

PLANTNET_MIN_SCORE = _float_from_env("PLANTNET_MIN_SCORE", 0.2)
