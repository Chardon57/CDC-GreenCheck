from pydantic import BaseModel, ConfigDict

from schemas.disease import DiseaseRead


class ResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_result: int
    label: str
    disease: DiseaseRead
