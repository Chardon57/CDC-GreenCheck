from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes.auth import router as auth_router

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

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "GreenCheck API en ligne"}