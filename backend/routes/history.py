from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import db
from dependencies import get_current_user
from models.user import User
from schemas.analysis import AnalysisRead
from services.history_service import AnalysisNotFoundError, get_user_analyses, get_user_analysis

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[AnalysisRead])
def list_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(db.get_session),
):
    return get_user_analyses(session, current_user.id_user)


@router.get("/{id_analysis}", response_model=AnalysisRead)
def get_history_item(
    id_analysis: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(db.get_session),
):
    try:
        return get_user_analysis(session, current_user.id_user, id_analysis)
    except AnalysisNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analyse introuvable.",
        )