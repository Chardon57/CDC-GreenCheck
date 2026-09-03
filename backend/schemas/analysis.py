from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from schemas.plant import PlantRead
from schemas.result import ResultRead


class AnalysisCreate(BaseModel):
    plant_location: Optional[str] = Field(default=None, max_length=255)
    plant_exposition: Optional[str] = Field(default=None, max_length=255)


class AnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_analysis: int
    date: datetime
    plant_location: Optional[str]
    plant_exposition: Optional[str]
    confidence: float
    id_user: int
    plant: PlantRead
    result: ResultRead