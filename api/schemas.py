# Modèles Pydantic

from pydantic import BaseModel

class TextInput(BaseModel):
    text: str

class LabelPrediction(BaseModel):
    label: str

class ScorePrediction(BaseModel):
    score: float
