from typing import List

from pydantic import BaseModel, ConfigDict

from schemas.treatment import TreatmentRead

class ResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_result: int
    label: str
    treatments: List[TreatmentRead] = []