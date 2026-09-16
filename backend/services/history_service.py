from sqlalchemy import select
from sqlalchemy.orm import Session

from models.analysis import Analysis


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