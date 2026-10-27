import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.analysis import Analysis
from services.image_service import delete_image

logger = logging.getLogger(__name__)


class AnalysisNotFoundError(Exception):
    """Levée quand l'analyse demandée n'existe pas, ou n'appartient pas à l'utilisateur."""


def get_user_analyses(session: Session, id_user: int) -> list[Analysis]:
    return list(
        session.scalars(
            select(Analysis)
            .where(Analysis.id_user == id_user)
            .order_by(Analysis.date.desc())
        )
    )


def get_user_analysis(session: Session, id_user: int, id_analysis: int) -> Analysis:
    analysis = session.scalar(
        select(Analysis).where(
            Analysis.id_analysis == id_analysis,
            Analysis.id_user == id_user,
        )
    )
    if analysis is None:
        raise AnalysisNotFoundError()
    return analysis


def delete_user_analysis(session: Session, id_user: int, id_analysis: int) -> None:
    """Supprime une analyse de l'utilisateur, puis sa photo.

    Ordre voulu : la base d'abord. Si la suppression du fichier échoue ensuite, il reste une photo
    orpheline sur le disque (sans conséquence pour l'utilisateur), alors que l'ordre inverse
    laisserait une analyse sans photo, visible dans l'historique.
    """
    analysis = get_user_analysis(session, id_user, id_analysis)
    session.delete(analysis)
    session.commit()
    try:
        delete_image(id_user, id_analysis)
    except OSError:
        logger.warning("Photo de l'analyse %s non supprimée du disque.", id_analysis, exc_info=True)
