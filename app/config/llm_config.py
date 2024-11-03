import openai
from langchain_openai import AzureChatOpenAI
from app.config.config import AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,AZURE_OPENAI_API_VERSION, AZURE_OPENAI_TEMPERATURE, MAX_TOKENS, AZURE_ENDPOINT, AZURE_API_KEY

openai.api_type = "azure"
openai.api_key = AZURE_API_KEY
openai.api_base = AZURE_ENDPOINT
openai.api_version = AZURE_OPENAI_API_VERSION
def get_llm():
    return AzureChatOpenAI(
        azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        temperature=float(AZURE_OPENAI_TEMPERATURE),
        max_tokens=int(MAX_TOKENS),
        openai_api_key=AZURE_API_KEY,
        azure_endpoint=AZURE_ENDPOINT,
    )
