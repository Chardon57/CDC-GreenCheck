from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.analysis import router as analysis_router
from routes.auth import router as auth_router
from routes.history import router as history_router

from config.cors import CORS_ORIGINS
import models  # noqa: F401 — nécessaire pour enregistrer tous les modèles avant create_tables()
from config.database import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.create_tables()
    yield


app = FastAPI(
    title="GreenCheck API",
    description="API de diagnostic intelligent de plantes pour AgroNovaTech",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS : sans cela, le navigateur bloque les appels du frontend (localhost:5173) vers l'API
# (localhost:8000), car ce sont deux « origines » différentes. Le jeton JWT voyage dans l'en-tête
# Authorization (pas dans un cookie) : allow_credentials reste donc à False, ce qui est plus sûr.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(history_router)

@app.get("/")
def read_root():
    return {"message": "GreenCheck API en ligne"}
