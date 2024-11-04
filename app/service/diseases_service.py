from typing import List, Dict
from app.model.diseases import DiseasesMatchResponse, DiseaseResponse, Disease, DiseaseError
from app.utils.database_manager import db_manager
from datetime import datetime
from bson import ObjectId


def find_exact_matching_diseases(symptom_ids: List[str]) -> DiseasesMatchResponse:
    """
    Find diseases that have all the given symptoms
    """
    try:
        # Find diseases where all symptom_ids are present
        query = {
            "symptoms": {
                "$all": symptom_ids
            }
        }

        # Execute query
        cursor = db_manager.diseases_collection.find(
            query,
            {
                "name": 1,
                "description": 1,
                "_id": 1
            }
        )

        # Convert cursor to list
        diseases = cursor.to_list(length=None)

        return DiseasesMatchResponse(
            diseases=[
                DiseaseResponse(
                    name=d["name"],
                    description=d["description"],
                    _id=str(d["_id"])
                ) for d in diseases
            ],
            count=len(diseases)
        )

    except Exception as e:
        return DiseasesMatchResponse(
            diseases=[],
            count=0,
            error=str(e)
        )


def get_symptom_ids(symptom_names: List[str]) -> Dict[str, str]:
    """Get symptom IDs from symptom names"""
    try:
        cursor = db_manager.symptoms_collection.find(
            {"symptom": {"$in": symptom_names}},
            {"_id": 1, "symptom": 1}
        )

        # Create mapping of symptom name to ID
        symptom_map = {doc["symptom"]: str(doc["_id"]) for doc in cursor}
        return symptom_map
    except Exception as e:
        raise Exception(f"Error fetching symptom IDs: {str(e)}")


async def process_disease_batch(diseases: List[Disease]) -> tuple:
    """Process a batch of diseases"""
    success_count = 0
    errors = []

    for disease in diseases:
        try:
            # Get symptom IDs
            symptom_map = get_symptom_ids(disease.symptoms)

            # Check for missing symptoms
            missing_symptoms = [s for s in disease.symptoms if s not in symptom_map]
            if missing_symptoms:
                raise Exception(f"Symptoms not found: {', '.join(missing_symptoms)}")

            # Convert to IDs
            symptom_ids = [symptom_map[symptom] for symptom in disease.symptoms]
            symptom_names = disease.symptoms

            # Generate ID if needed
            string_id = str(ObjectId())

            # Prepare document
            document = {
                "_id": string_id,
                "name": disease.name,
                "description": disease.description,
                "symptom_ids": symptom_ids,
                "symptoms": symptom_names,
                "created_at": datetime.utcnow()
            }

            # Insert/update
            db_manager.diseases_collection.update_one(
                {"name": disease.name},
                {"$set": document},
                upsert=True
            )

            success_count += 1

        except Exception as e:
            errors.append(DiseaseError(
                disease=disease.name,
                error=str(e)
            ))

    return success_count, errors
