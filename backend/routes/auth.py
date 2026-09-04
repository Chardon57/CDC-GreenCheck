from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas.auth import Token
from config.database import db
from schemas.user import UserCreate, UserRead, UserLogin
from services.auth_service import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    authenticate_user,
    create_access_token,
    register_user,
)
from models.user import User

from dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, session: Session = Depends(db.get_session)):
    try:
        user = register_user(session, user_data)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà avec cette adresse e-mail.",
        )
    return user

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, session: Session = Depends(db.get_session)):
    try:
        user = authenticate_user(session, credentials.email, credentials.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou mot de passe invalide(s).",
        )
    access_token=create_access_token(data={"sub": str(user.id_user)})
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user