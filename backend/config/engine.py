import os

from dotenv import load_dotenv

load_dotenv()

# Adresse du moteur IA de diagnostic (conteneur ai_engine). En local : http://localhost:8001.
# Dans Docker Compose, ce sera le nom du service, par exemple http://ai_engine:8001.
ENGINE_URL = os.getenv("ENGINE_URL", "http://localhost:8001").rstrip("/")


def _float_from_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        raise RuntimeError(
            f"{name} invalide : doit être un nombre. "
            "Merci de se référer au fichier .env.example."
        )


# Délai maximal (en secondes) accordé au moteur pour répondre. Large, car sur CPU
# une inférence peut prendre quelques secondes.
ENGINE_TIMEOUT = _float_from_env("ENGINE_TIMEOUT", 30.0)
