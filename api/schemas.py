# Modèles Pydantic

from pydantic import BaseModel, Field

class PredictText(BaseModel):
    text: str = Field(..., min_length=3)

class PredictLabelResponse(BaseModel):
    label: str
    model_version: str | None = None

class PredictScoreResponse(BaseModel):
    score: float
    model_version: str | None = None
