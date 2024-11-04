import json
import re


def parse_llm_response(llm_response: str) -> dict:
    """
    Parse LLM response string that contains JSON with markdown code blocks
    """
    try:
        # Remove ```json prefix and ``` suffix using regex
        json_str = re.sub(r'^```json\n|```$', '', llm_response.strip())

        # Parse the JSON string
        parsed_data = json.loads(json_str)

        return parsed_data
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return None