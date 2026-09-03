from pydantic import BaseModel, ConfigDict


class TreatmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_treatmentt: int
    advice: str