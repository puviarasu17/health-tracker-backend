from typing import List
from datetime import datetime
from app.model.symptoms import Symptom, SearchResponse, BatchedSymptomRequest, MultiSymptomResponse, MedicalNotesRequest
from app.utils.embedding import get_embedding
from app.utils.database_manager import db_manager
from app.utils.llm_response_parser import parse_llm_response
from app.utils.symptoms_extractor import extract_symptoms
import asyncio
import time
from bson import ObjectId


async def process_symptom_batch(symptoms: List[Symptom]) -> tuple:
    """Process a batch of symptoms"""
    success_count = 0
    errors = []

    for symptom in symptoms:
        try:
            # Get embedding for the symptom
            embedding = await get_embedding(symptom.symptom)

            string_id = str(ObjectId())

            # Prepare document
            document = {
                "_id": string_id,
                "symptom": symptom.symptom,
                "severity": symptom.severity,
                "symptomVector": embedding,
                "vectorized_at": datetime.utcnow()
            }

            db_manager.symptoms_collection.update_one(
                {"symptom": symptom.symptom},
                {"$set": document},
                upsert=True
            )

            success_count += 1

        except Exception as e:
            errors.append({
                "symptom": symptom.symptom,
                "error": str(e)
            })

    return success_count, errors


async def search_symptom(symptom: str) -> SearchResponse:
    """
    Search for a single symptom using vector similarity
    """
    try:
        # Get embedding for the input symptom
        symptom_vector = await get_embedding(symptom)

        # Perform vector search
        result = db_manager.symptoms_collection.aggregate([
            {
                "$vectorSearch": {
                    "index": "default",
                    "path": "symptomVector",
                    "queryVector": symptom_vector,
                    "numCandidates": 100,
                    "limit": 1
                }
            },
            {
                "$project": {
                    "symptom": 1,
                    "severity": 1,
                    "_id": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]).next()
        return SearchResponse(
            input_symptom=symptom,
            matched_symptom=result["symptom"],
            severity=result["severity"],
            id=result["_id"],
            score=result.get("score"),
            error=None
        )

    except Exception as e:
        return SearchResponse(
            input_symptom=symptom,
            matched_symptom=None,
            severity=None,
            id=None,
            score=None,
            error=str(e)
        )


async def search_multiple_symptoms(request: BatchedSymptomRequest):
    """
    API endpoint to search for multiple symptoms in parallel with batch control
    Parameters:
        - symptoms: List of symptoms to search
        - batch_size: Number of symptoms to process in parallel (default: 5)
    Returns:
        - List of search results
        - Total processing time
        - Number of symptoms processed
        - Error message if any
    """
    try:
        start_time = time.time()
        all_results = []

        # Validate input
        if not request.symptoms:
            raise ValueError("No symptoms provided")

        if len(request.symptoms) > 100:  # Optional: Add maximum limit
            raise ValueError("Too many symptoms. Maximum allowed: 100")

        # Process symptoms in batches
        for i in range(0, len(request.symptoms), request.batch_size):
            # Get current batch
            batch = request.symptoms[i:i + request.batch_size]

            # Create tasks for current batch
            tasks = [search_symptom(symptom) for symptom in batch]

            try:
                # Execute batch tasks concurrently
                batch_results = await asyncio.gather(*tasks)
                all_results.extend(batch_results)

                # Optional: Add delay between batches to prevent rate limiting
                if i + request.batch_size < len(request.symptoms):
                    await asyncio.sleep(0.1)  # 100ms delay between batches

            except Exception as batch_error:
                # Log batch error but continue processing
                print(f"Error processing batch {i // request.batch_size}: {str(batch_error)}")
                continue

        total_time = time.time() - start_time
        print(f"Total time {total_time}")
        # Check if we got any results
        if not all_results:
            raise ValueError("No results were obtained from the search")

        return MultiSymptomResponse(
            results=all_results,
            total_time=round(total_time, 3),
            processed_count=len(all_results),
            error=None
        )

    except Exception as e:
        return MultiSymptomResponse(
            results=[],
            total_time=time.time() - start_time,
            processed_count=0,
            error=str(e)
        )


async def convert_medical_notes_to_symptoms(medical_notes: MedicalNotesRequest):
    extracted_symptoms = extract_symptoms(medical_notes.notes)
    parsed_symptoms = parse_llm_response(extracted_symptoms)
    symptoms_list = [item["symptom"] for item in parsed_symptoms["symptoms"]]
    request = BatchedSymptomRequest(
        symptoms=symptoms_list,
        batch_size=10
    )
    return await search_multiple_symptoms(request)
