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
    id: Optional[str] = None
    score: Optional[float]
    error: Optional[str] = None


class BatchedSymptomRequest(BaseModel):
    symptoms: List[str]
    batch_size: int = Field(default=5, ge=1, le=20, description="Number of symptoms to process in each batch")


class MedicalNotesRequest(BaseModel):
    notes: str


class MultiSymptomResponse(BaseModel):
    results: List[SearchResponse]
    total_time: float
    processed_count: int
    error: Optional[str] = None