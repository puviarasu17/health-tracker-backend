from fastapi import APIRouter, HTTPException
from app.model.symptoms import VectorizeResponse, SymptomBatch, MultiSymptomResponse, MedicalNotesRequest
from datetime import datetime
from app.service.symptoms_service import process_symptom_batch, convert_medical_notes_to_symptoms


symptoms_router = APIRouter(
    prefix="/api/symptoms",
    tags=["Symptoms"],
)



@symptoms_router.post("/symptoms/vectorize", response_model=VectorizeResponse)
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


@symptoms_router.post("/symptoms/convert_notes_to_symptoms", response_model=MultiSymptomResponse)
async def convert_notes_to_symptoms(medical_notes: MedicalNotesRequest):
    """
    API endpoint to convert medical notes to symptoms
    """
    try:
        return await convert_medical_notes_to_symptoms(medical_notes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
