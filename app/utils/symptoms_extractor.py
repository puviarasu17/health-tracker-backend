import logging
from langchain_core.output_parsers import StrOutputParser
from app.config.llm_config import get_llm
from app.config.prompts import symptom_extraction_prompt
from langchain.prompts import ChatPromptTemplate


def get_chain(template):
    llm = get_llm()
    return template | llm | StrOutputParser()


def extract_symptoms(medical_notes):
    try:
        symptoms_output = ""
        symptom_extraction_prompt_template = ChatPromptTemplate.from_messages(symptom_extraction_prompt)
        symptom_extraction_chain = get_chain(symptom_extraction_prompt_template)
        for tok in symptom_extraction_chain.stream({"patient_medical_notes": medical_notes}):
            print(tok, end="", flush=True)
            symptoms_output += tok
        return symptoms_output
    except Exception as e:
        logging.error(f"Failed to extract symptoms from medical notes: {e}")
        raise