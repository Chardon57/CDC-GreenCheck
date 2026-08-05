from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AnalysisContext(BaseModel):
    plant_type: str
    exposition: str | None = None
    location: str | None = None
    culture_type: str | None = None

@app.get("/")
def read_root():
    return {"message": "Hello GreenCheck"}

@app.post("/context")
def receive_context(context: AnalysisContext):
    return {"received": context}