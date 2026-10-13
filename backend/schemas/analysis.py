from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from schemas.plant import PlantRead
from schemas.result import ResultRead


# Valeurs proposées par le formulaire d'analyse (stockées telles quelles en base).
Location = Literal["Intérieur", "Extérieur"]
Exposition = Literal["Soleil", "Mi-ombre", "Ombre"]
Cultivation = Literal["En pot", "Pleine terre"]


class AnalysisCreate(BaseModel):
    plant_location: Optional[Location] = None
    plant_exposition: Optional[Exposition] = None
    plant_cultivation: Optional[Cultivation] = None


class AnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_analysis: int
    date: datetime
    plant_location: Optional[str]
    plant_exposition: Optional[str]
    plant_cultivation: Optional[str] = None
    confidence: float
    id_user: int
    plant: PlantRead
    result: ResultRead

    @field_validator("date")
    @classmethod
    def _date_en_utc(cls, value: datetime) -> datetime:
        """La base stocke l'heure UTC sans fuseau. On l'indique explicitement (« ...Z » en JSON) :
        sans cela, le navigateur la prendrait pour l'heure locale et afficherait un décalage."""
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
