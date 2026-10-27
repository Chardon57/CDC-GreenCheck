import os

from dotenv import load_dotenv

load_dotenv()

# Origines (adresse du frontend) autorisées à appeler l'API depuis un navigateur.
# En développement, Vite sert le frontend sur http://localhost:5173. En production, on
# indiquera l'adresse réelle du site dans CORS_ORIGINS (plusieurs adresses : séparées par des virgules).
# Une origine = schéma + domaine + port, sans chemin ni « / » final.
_DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"

CORS_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ORIGINS", _DEFAULT_ORIGINS).split(",")
    if origin.strip()
]
