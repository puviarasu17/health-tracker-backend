from typing import List
from datetime import datetime
from app.model.symptoms import Symptom, SearchResponse
from app.utils.embedding import get_embedding
from app.utils.database_manager import db_manager


async def process_symptom_batch(symptoms: List[Symptom]) -> tuple:
    """Process a batch of symptoms"""
    success_count = 0
    errors = []

    for symptom in symptoms:
        try:
            # Get embedding for the symptom
            embedding = await get_embedding(symptom.symptom)

            # Prepare document
            document = {
                "symptom": symptom.symptom,
                "severity": symptom.severity,
                "symptomVector": embedding,
                "vectorized_at": datetime.utcnow()
            }

            # Add _id if provided
            if symptom._id:
                document["_id"] = symptom._id

            # Update or insert document
            db_manager.collection.update_one(
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
        result = db_manager.collection.aggregate([
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
                    "_id": 0,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]).next()

        return SearchResponse(
            input_symptom=symptom,
            matched_symptom=result["symptom"],
            severity=result["severity"],
            score=result.get("score"),
            error=None
        )

    except Exception as e:
        return SearchResponse(
            input_symptom=symptom,
            matched_symptom=None,
            severity=None,
            score=None,
            error=str(e)
        )