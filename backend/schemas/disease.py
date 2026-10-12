from typing import List

from pydantic import BaseModel, ConfigDict

from schemas.treatment import TreatmentRead


class DiseaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_disease: int
    name: str
    treatments: List[TreatmentRead] = []
