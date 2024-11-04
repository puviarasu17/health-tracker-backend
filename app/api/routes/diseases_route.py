from fastapi import APIRouter, HTTPException
from app.model.diseases import DiseasesMatchResponse, BatchResponse, DiseaseBatch, DiseaseError
from app.service.diseases_service import find_exact_matching_diseases, process_disease_batch
from typing import List
import time

diseases_router = APIRouter(
    prefix="/api/diseases",
    tags=["Diseases"],
)


@diseases_router.post("/find-diseases", response_model=DiseasesMatchResponse)
async def find_diseases(symptom_ids: List[str]):
    """
    Find diseases that match all given symptoms exactly
    """
    if not symptom_ids:
        raise HTTPException(status_code=400, detail="No symptoms provided")
    return find_exact_matching_diseases(symptom_ids)


@diseases_router.post("/batch", response_model=BatchResponse)
async def create_diseases(request: DiseaseBatch):
    """API endpoint to create multiple diseases in batch"""
    try:
        start_time = time.time()
        total_success = 0
        all_errors = []

        for i in range(0, len(request.diseases), request.batch_size):
            batch = request.diseases[i:i + request.batch_size]
            success_count, errors = await process_disease_batch(batch)
            total_success += success_count
            all_errors.extend(errors)

        return BatchResponse(  # Using BatchResponse here
            success_count=total_success,
            failed_count=len(all_errors),
            errors=all_errors,
            processing_time=round(time.time() - start_time, 3)
        )

    except Exception as e:
        return BatchResponse(  # Using BatchResponse here
            success_count=0,
            failed_count=len(request.diseases),
            errors=[DiseaseError(error=str(e))],
            processing_time=0
        )
