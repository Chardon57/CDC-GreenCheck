from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_plant: int
    vernacular_name: str
    official_name: Optional[str]