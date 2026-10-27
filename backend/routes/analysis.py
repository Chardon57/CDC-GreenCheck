import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from config import storage
from config.database import db
from dependencies import get_current_user
from models.user import User
from schemas.analysis import AnalysisCreate, AnalysisRead, Cultivation, Exposition, Location
from services.analysis_service import UnknownDiagnosisError, run_analysis
from services.diagnosis_service import DiagnosisImageRejectedError, DiagnosisUnavailableError
from services.image_service import InvalidImageError, UnsupportedImageFormatError
from services.plantnet_service import PlantNetUnavailableError, PlantNotRecognizedError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


# `def` (et non `async def`) : la fonction fait des appels réseau et disque bloquants ; FastAPI
# l'exécute alors dans un thread à part et le serveur reste disponible pour les autres requêtes.
@router.post("", response_model=AnalysisRead, status_code=status.HTTP_201_CREATED)
def create_analysis(
    image: UploadFile = File(...),
    plant_location: Location | None = Form(default=None),
    plant_exposition: Exposition | None = Form(default=None),
    plant_cultivation: Cultivation | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(db.get_session),
):
    # On lit au plus (limite + 1) octets : si on obtient plus que la limite, c'est trop gros.
    raw = image.file.read(storage.MAX_UPLOAD_BYTES + 1)
    if len(raw) > storage.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Photo trop volumineuse.",
        )

    context = AnalysisCreate(
        plant_location=plant_location,
        plant_exposition=plant_exposition,
        plant_cultivation=plant_cultivation,
    )

    try:
        return run_analysis(session, current_user.id_user, raw, context)
    except UnsupportedImageFormatError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Format de photo non supporté (JPEG, PNG ou WebP attendu).",
        )
    except (InvalidImageError, DiagnosisImageRejectedError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Photo illisible ou inexploitable.",
        )
    except PlantNotRecognizedError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Aucune plante n'a été reconnue sur cette photo.",
        )
    except (PlantNetUnavailableError, DiagnosisUnavailableError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le service d'analyse est momentanément indisponible. Réessayez plus tard.",
        )
    except UnknownDiagnosisError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'analyse.",
        )
