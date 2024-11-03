from typing import List
from openai import AzureOpenAI
from fastapi import HTTPException
from app.config.config import AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME, AZURE_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_ENDPOINT


client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT
)


async def get_embedding(text: str) -> List[float]:
    """Get embedding from Azure OpenAI API"""
    try:
        response = client.embeddings.create(
            input=text,
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting embedding: {str(e)}")