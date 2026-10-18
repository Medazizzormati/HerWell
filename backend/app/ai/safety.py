import re

CRISIS_PATTERNS = [
    r"\b(suicid|kill myself|want to die|end my life|self[- ]harm)\b",
    r"(نحب نموت|نقتل روحي|نأذي روحي|ما عادش نحب نعيش)",
    r"(je veux mourir|me suicider|mettre fin à mes jours)",
]

# Menstrual health safety patterns
MENSTRUAL_MEDICAL_DIAGNOSIS = [
    r"\b(endometriosis|pcos|polycystic|pmdd|premenstrual dysphoric disorder)\b",
    r"(endométriose|sopk|syndrome des ovaires polykystiques|trouble dysphorique prémenstruel)",
    r"\b(pregnant|pregnancy|conceive|infertility)\b",
    r"(enceinte|grossesse|concevoir|infertilité)",
]

# Severe symptoms requiring medical attention
SEVERE_SYMPTOM_PATTERNS = [
    r"(severe pain|unbearable pain|fainting|passing out|heavy bleeding|excessive bleeding)",
    r"(douleur sévère|douleur insupportable|évanouissement|saignements abondants|perte de connaissance)",
]

def safety_precheck(message: str) -> bool:
    text = message.lower()
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in CRISIS_PATTERNS)

def safety_postcheck(response: str) -> str:
    unsafe_claims = ["you definitely have depression", "you are diagnosed with"]
    if any(claim in response.lower() for claim in unsafe_claims):
        return ("Je ne peux pas poser de diagnostic. Je peux partager des informations générales, "
                "mais un professionnel qualifié peut vous accompagner.")
    return response

def menstrual_safety_precheck(message: str) -> dict:
    """
    Check menstrual health queries for safety concerns.
    Returns dict with 'routing' key: 'normal', 'medical_warning', or 'crisis'
    """
    text = message.lower()
    
    # Check for severe symptoms that need immediate medical attention
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in SEVERE_SYMPTOM_PATTERNS):
        return {
            "routing": "medical_warning",
            "message": "Ces symptômes peuvent nécessiter une évaluation médicale. Consultez un professionnel de santé si vous ressentez une douleur sévère, des saignements très abondants, ou des évanouissements."
        }
    
    # Check for medical diagnosis questions
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in MENSTRUAL_MEDICAL_DIAGNOSIS):
        return {
            "routing": "medical_warning",
            "message": "Je ne peux pas poser de diagnostic médical. Si vous pensez avoir un problème de santé comme l'endométriose, le SOPK, ou le trouble dysphorique prémenstruel, consultez un professionnel de santé. Je peux partager des informations générales sur ces sujets."
        }
    
    return {"routing": "normal"}

def menstrual_safety_postcheck(response: str) -> str:
    """
    Post-check to prevent the LLM from making medical claims or recommendations.
    """
    # Check for diagnostic claims
    diagnostic_claims = [
        "you have endometriosis",
        "you have pcos",
        "you are pregnant",
        "you definitely have",
        "diagnosis",
        "diagnosed with"
    ]
    
    response_lower = response.lower()
    if any(claim in response_lower for claim in diagnostic_claims):
        return ("Je ne peux pas poser de diagnostic. Ces informations sont générales et éducatives. "
                "Consultez un professionnel de santé pour un avis médical personnalisé.")
    
    # Check for prescription medicine recommendations
    prescription_warnings = [
        "take this medicine",
        "prescription",
        "pill for",
        "medication for"
    ]
    
    if any(warning in response_lower for warning in prescription_warnings):
        return ("Je ne peux pas recommander de médicaments sur ordonnance. Consultez un professionnel de santé "
                "pour un traitement approprié.")
    
    return response
