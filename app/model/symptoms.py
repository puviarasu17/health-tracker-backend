from pydantic import BaseModel, Field
from typing import List, Optional


class Symptom(BaseModel):
    symptom: str
    severity: str
    _id: Optional[str] = None


class SymptomBatch(BaseModel):
    symptoms: List[Symptom]
    batch_size: int = Field(default=100, le=1000, description="Number of symptoms to process in each batch")


class VectorizeResponse(BaseModel):
    success_count: int
    failed_count: int
    errors: List[dict]
    processing_time: float


class SearchResponse(BaseModel):
    input_symptom: str
    matched_symptom: Optional[str]
    severity: Optional[str]
    score: Optional[float]
    error: Optional[str] = None