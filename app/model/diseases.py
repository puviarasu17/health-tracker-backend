from pydantic import BaseModel, Field
from typing import List, Optional


class Disease(BaseModel):
    name: str
    description: str
    symptoms: List[str]  # Symptom names
    _id: Optional[str] = None


class DiseaseBatch(BaseModel):
    diseases: List[Disease]
    batch_size: int = Field(default=100, le=1000)


class DiseaseError(BaseModel):
    disease: Optional[str] = None
    error: str


class BatchResponse(BaseModel):  # Changed from DiseaseResponse to BatchResponse
    success_count: int
    failed_count: int
    errors: List[DiseaseError]
    processing_time: float


class DiseaseResponse(BaseModel):
    name: str
    description: str
    _id: str


class DiseasesMatchResponse(BaseModel):
    diseases: List[DiseaseResponse]
    count: int
    error: Optional[str] = None
