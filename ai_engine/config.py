"""Réglages du moteur, lus dans les variables d'environnement (voir .env.example)."""

import os

from dotenv import load_dotenv

load_dotenv()

# Modèle utilisé pour le zero-shot. Le changer = modifier cette variable, pas le code.
MODEL_NAME: str = os.getenv("MODEL_NAME", "google/siglip2-base-patch16-224")

# « cpu » par défaut (marche partout). « cuda » pour utiliser une carte NVIDIA.
DEVICE: str = os.getenv("DEVICE", "cpu")

# Taille maximale d'une image acceptée, en octets (la variable est exprimée en Mo).
MAX_IMAGE_BYTES: int = int(float(os.getenv("MAX_IMAGE_MB", "10")) * 1024 * 1024)
