# Orchestration d'une analyse : photo -> Pl@ntNet (quelle plante ?) -> moteur IA (quel état ?)
# -> enregistrement en base et sur disque.
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.analysis import Analysis
from models.disease import Disease
from models.plant import Plant
from models.result import Result
from schemas.analysis import AnalysisCreate
from services.diagnosis_service import diagnose_plant
from services.image_service import delete_image, normalize_image, save_image
from services.plantnet_service import PlantIdentification, identify_plant

logger = logging.getLogger(__name__)

# Les fichiers envoyés aux services externes : la photo a été normalisée en JPEG.
_FILENAME = "plante.jpg"
_CONTENT_TYPE = "image/jpeg"


class UnknownDiagnosisError(Exception):
    """Le moteur a renvoyé un diagnostic absent de la base (listes labels.py / seed désynchronisées)."""


def run_analysis(
    session: Session, id_user: int, raw_image: bytes, context: AnalysisCreate
) -> Analysis:
    """Réalise une analyse complète et l'enregistre. Peut lever, dans l'ordre des étapes :

    - image_service : InvalidImageError, UnsupportedImageFormatError
    - plantnet_service : PlantNotRecognizedError, PlantNetUnavailableError
    - diagnosis_service : DiagnosisImageRejectedError, DiagnosisUnavailableError
    - UnknownDiagnosisError

    Rien n'est enregistré (ni en base, ni sur disque) si l'une des étapes échoue.
    """
    # 1) Photo valide ? Vérifiée AVANT tout appel externe : le quota Pl@ntNet (500/jour) est précieux.
    jpeg = normalize_image(raw_image)

    # 2) Quelle plante ? Si ce n'est pas une plante, on s'arrête là, sans solliciter le moteur IA.
    identification = identify_plant(jpeg, _FILENAME, _CONTENT_TYPE)

    # 3) Dans quel état ?
    diagnosis = diagnose_plant(jpeg, _FILENAME, _CONTENT_TYPE)

    # 4) Quel verdict de la base correspond à ce diagnostic ?
    result = session.scalar(
        select(Result).join(Result.disease).where(Disease.name == diagnosis.label)
    )
    if result is None:
        logger.error("Diagnostic inconnu renvoyé par le moteur : %r", diagnosis.label)
        raise UnknownDiagnosisError(diagnosis.label)

    # 5) Enregistrement. L'identifiant de l'analyse n'existe qu'après l'insertion : on insère
    #    (flush), on écrit le fichier nommé avec cet identifiant, puis seulement on valide (commit).
    #    Si l'un des deux échoue, tout est annulé.
    plant = _get_or_create_plant(session, identification)
    analysis = Analysis(
        date=datetime.now(timezone.utc).replace(tzinfo=None),  # UTC, sans fuseau (voir AnalysisRead)
        plant_location=context.plant_location,
        plant_exposition=context.plant_exposition,
        plant_cultivation=context.plant_cultivation,
        confidence=diagnosis.confidence,
        id_user=id_user,
        plant=plant,
        result=result,
    )
    session.add(analysis)
    try:
        session.flush()
        save_image(jpeg, id_user, analysis.id_analysis)
        session.commit()
    except Exception:
        session.rollback()
        if analysis.id_analysis is not None:
            delete_image(id_user, analysis.id_analysis)
        raise

    logger.info(
        "Analyse %s créée (utilisateur %s) : %s, %s (%.2f).",
        analysis.id_analysis, id_user, plant.official_name, diagnosis.label, diagnosis.confidence,
    )
    return analysis


def _get_or_create_plant(session: Session, identification: PlantIdentification) -> Plant:
    """Réutilise la plante déjà connue (même nom scientifique) ou la crée."""
    plant = session.scalar(select(Plant).where(Plant.official_name == identification.official_name))
    if plant is None:
        return Plant(
            vernacular_name=identification.vernacular_name,
            official_name=identification.official_name,
            family=identification.family,
        )
    if plant.family is None and identification.family:
        plant.family = identification.family  # complète les plantes créées avant l'ajout de la famille
    return plant
