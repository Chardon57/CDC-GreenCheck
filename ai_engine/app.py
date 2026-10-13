"""API du moteur IA : POST /diagnose (image -> label + confidence) et GET /health."""

import io
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel, Field

import config
from diagnoser import Diagnoser
from labels import DIAGNOSTICS

logger = logging.getLogger("ai_engine")

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


class DiagnosisResponse(BaseModel):
    label: str = Field(description="Nom exact d'une maladie de la table `disease`")
    confidence: float = Field(ge=0.0, le=1.0, description="Confiance du diagnostic, de 0 à 1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import ici (et non en haut du fichier) pour que les tests n'aient pas besoin de PyTorch.
    from siglip_embedder import SiglipEmbedder

    embedder = SiglipEmbedder(config.MODEL_NAME, config.DEVICE)
    app.state.diagnoser = Diagnoser(embedder, DIAGNOSTICS)
    app.state.device = embedder.device
    yield


app = FastAPI(
    title="GreenCheck — moteur IA",
    description="Diagnostic de l'état d'une plante par comparaison image/texte (zero-shot).",
    version="0.1.0",
    lifespan=lifespan,
)


def get_diagnoser(request: Request) -> Diagnoser:
    return request.app.state.diagnoser


@app.get("/health")
def health(request: Request):
    return {
        "status": "ok",
        "model": config.MODEL_NAME,
        "device": getattr(request.app.state, "device", None),
    }


# `def` (et non `async def`) : l'inférence est un calcul bloquant ; FastAPI exécute alors la
# fonction dans un thread à part et le serveur reste disponible pour les autres requêtes.
@app.post("/diagnose", response_model=DiagnosisResponse)
def diagnose(image: UploadFile = File(...), diagnoser: Diagnoser = Depends(get_diagnoser)):
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Type de fichier non supporté (JPEG, PNG ou WebP attendu).",
        )

    # On lit au plus (limite + 1) octets : si on obtient plus que la limite, c'est trop gros.
    data = image.file.read(config.MAX_IMAGE_BYTES + 1)
    if len(data) > config.MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image trop volumineuse.")

    try:
        pil_image = Image.open(io.BytesIO(data))
        # Les photos de téléphone sont souvent stockées « couchées » avec une indication
        # d'orientation (EXIF) : on la applique pour que le modèle voie la plante à l'endroit.
        pil_image = ImageOps.exif_transpose(pil_image)
        pil_image = pil_image.convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(status_code=422, detail="Fichier image illisible ou corrompu.") from None

    result = diagnoser.diagnose(pil_image)
    return DiagnosisResponse(label=result.label, confidence=result.confidence)
