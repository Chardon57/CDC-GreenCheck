from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from config.database import db
from dependencies import get_current_user
from models.user import User
from schemas.analysis import AnalysisRead
from services.history_service import AnalysisNotFoundError, get_user_analyses, get_user_analysis
from services.image_service import image_path

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


@router.get("/{id_analysis}/image")
def get_history_image(
    id_analysis: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(db.get_session),
):
    """Photo de l'analyse. Même règle que le détail : on ne sert que les analyses de l'utilisateur."""
    try:
        analysis = get_user_analysis(session, current_user.id_user, id_analysis)
    except AnalysisNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analyse introuvable.",
        )

    path = image_path(current_user.id_user, analysis.id_analysis)
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image introuvable.",
        )
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "private, max-age=3600"})
