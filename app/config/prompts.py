symptom_template_str = """
Your are provided with the task to extract the symptoms from the medical notes taken by a nurse from a patient. Here’s what to do:
<patient_medical_notes>
{patient_medical_notes}
</patient_medical_notes>
1. **Analyze the medical notes**: Carefully analyze the medical notes for extracting the symptoms:
   - Identify any misspellings, typos in the medical notes and correct them
   - Identify the symptoms mentioned by the patient 
   - Identify the core symptom. This should not have any severity associated with it. Also, this should be the root word. 
     Example:
        Wrong core symptoms: High acute cough, feverish
        Correct core symptom: cough, fever
2. **Identify the severity**
    - With your Health care experience, give a severity to each symptom
    - Severity should be one of the below 4 
        1. mild
        2. moderate
        3. severe
        4. critical
    - Always prefix the core_symptom with one of the above 4 severity levels. Example: severe fever, mild cough
    - Strictly add only one of these 4 prefixes. Do not add any synonyms
3. **Prioritize the symptoms**
    - With your Health care experience, give a priority to each symptom
    - Priority should be between 1 and 3 with 1 being high priority and 3 being low priority
3. **Provide the Output in Strict JSON format**: Below is the format
   {{
        "symptoms" : [
            {{
                "symptom": "severe fever",
                "priority": "2"
            }},
            {{
                "symptom": "mild cough",
                "priority": "3"
            }}
        ]
   }}
   
Example: 
Input: Patient having high fever for past 3 days, experiencing light cough for past 2 days along with severe head ache for past 4 days
Output: {{
        "symptoms" : [
            {{
                "symptom": "severe fever",
                "priority": "1"
            }},
            {{
                "symptom": "mild cough",
                "priority": "3"
            }},
            {{
                "symptom": "severe headache", 
                "priority": "2"
            }}
        ]
   }}
"""

symptom_extraction_prompt = [
    ("system", "You are a Health care expert"
               "Please follow the instructions below to extract the symptoms from the patient medical notes."),
    ("user", symptom_template_str)
]