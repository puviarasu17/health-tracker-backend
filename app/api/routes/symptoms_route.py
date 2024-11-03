from fastapi import APIRouter, HTTPException
from app.model.symptoms import VectorizeResponse, SymptomBatch, SearchResponse
from datetime import datetime
from app.service.symptoms_service import process_symptom_batch, search_symptom

router = APIRouter(
    prefix="/api",
    tags=["ISO 20022 Message Generator"],
)


@router.post("/vectorize", response_model=VectorizeResponse)
async def vectorize_symptoms(request: SymptomBatch):
    """
    Vectorize multiple symptoms and store in MongoDB
    """
    start_time = datetime.utcnow()

    try:
        # Process symptoms in batches
        total_success = 0
        all_errors = []

        # Split symptoms into batches
        for i in range(0, len(request.symptoms), request.batch_size):
            batch = request.symptoms[i:i + request.batch_size]
            success_count, errors = await process_symptom_batch(batch)
            total_success += success_count
            all_errors.extend(errors)

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        return VectorizeResponse(
            success_count=total_success,
            failed_count=len(all_errors),
            errors=all_errors,
            processing_time=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_symptom/{symptom}", response_model=SearchResponse)
async def search_symptom_endpoint(symptom: str):
    """
    API endpoint to search for a single symptom
    """
    return await search_symptom(symptom)