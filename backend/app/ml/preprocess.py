# Preprocessing utilities for PoisonSense NLP Pipeline
import re
import string
from typing import List, Dict, Optional


# Common symptom synonyms for normalization
SYMPTOM_SYNONYMS = {
    "throwing up": "vomiting",
    "puking": "vomiting",
    "dizzy": "dizziness",
    "feel dizzy": "dizziness",
    "belly pain": "abdominal pain",
    "stomach pain": "abdominal pain",
    "stomach ache": "abdominal pain",
    "tummy pain": "abdominal pain",
    "can't breathe": "shortness of breath",
    "hard to breathe": "shortness of breath",
    "breathing difficulty": "shortness of breath",
    "breathing problems": "shortness of breath",
    "head hurts": "headache",
    "head pain": "headache",
    "feeling sick": "nausea",
    "feel nauseous": "nausea",
    "blurry vision": "blurred vision",
    "can't see clearly": "blurred vision",
    "shaking": "tremors",
    "shivering": "tremors",
    "tired": "fatigue",
    "exhaustion": "fatigue",
    "exhausted": "fatigue",
    "weak": "weakness",
    "feeling weak": "weakness",
    "muscle pain": "muscle weakness",
    "chest hurts": "chest pain",
    "chest tightness": "chest pain",
    "drooling": "salivation",
    "excess saliva": "salivation",
    "loose motion": "diarrhea",
    "loose motions": "diarrhea",
    "watery stool": "diarrhea",
    "fits": "seizures",
    "convulsions": "seizures",
    "skin rash": "skin changes",
    "skin irritation": "skin changes",
    "forgetful": "memory loss",
    "memory issues": "memory loss",
    "small pupils": "pinpoint pupils",
    "constricted pupils": "pinpoint pupils",
    "not hungry": "loss of appetite",
    "no appetite": "loss of appetite",
    "slow breathing": "respiratory depression",
    "shallow breathing": "respiratory depression",
    "sleepy": "drowsiness",
    "very sleepy": "drowsiness",
    "feeling sleepy": "drowsiness",
    "muscle jerks": "muscle twitching",
    "twitches": "muscle twitching",
    "angry": "irritability",
    "agitated": "irritability",
    "mixed up": "confusion",
    "confused": "confusion",
    "disoriented": "confusion",
}

# Known poison name aliases
POISON_ALIASES = {
    "rat poison": "Arsenic",
    "pesticide": "Organophosphate",
    "insecticide": "Organophosphate",
    "bug spray": "Organophosphate",
    "paracetamol": "Acetaminophen",
    "tylenol": "Acetaminophen",
    "celphos": "Aluminium Phosphide",
    "dhatura": "Natural Toxin",
    "bleach": "Household Chemical",
    "acid": "Industrial",
    "antifreeze": "Ethylene Glycol",
    "wood alcohol": "Methanol",
    "sleeping pills": "Drug Overdose",
    "heroin": "Opioids",
    "morphine": "Opioids",
    "opium": "Opioids",
}


def clean_text(text: str) -> str:
    """
    Clean and normalize input text for model prediction.
    - Lowercases text
    - Removes extra whitespace
    - Strips punctuation (except commas used as separators)
    - Removes numbers unless part of a word
    """
    if not text:
        return ""

    text = text.lower().strip()

    # Remove punctuation except commas (symptom separators)
    text = re.sub(r"[^\w\s,]", " ", text)

    # Collapse multiple whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_symptoms(text: str) -> str:
    """
    Replace common layperson symptom descriptions with
    medical terminology that the model was trained on.
    """
    text = clean_text(text)

    for informal, formal in SYMPTOM_SYNONYMS.items():
        # Word-boundary replacement to avoid partial matches
        pattern = r"\b" + re.escape(informal) + r"\b"
        text = re.sub(pattern, formal, text)

    return text


def extract_symptoms_list(text: str) -> List[str]:
    """
    Extract individual symptoms from a free-text description.
    Splits on commas, 'and', semicolons.
    """
    text = normalize_symptoms(text)

    # Split on comma, semicolon, or ' and '
    parts = re.split(r"[,;]|\band\b", text)

    symptoms = []
    for part in parts:
        cleaned = part.strip()
        if cleaned and len(cleaned) > 1:
            symptoms.append(cleaned)

    return symptoms


def detect_suspected_poison(text: str) -> Optional[str]:
    """
    Check if the user mentioned a known poison or alias
    in the symptom text. Useful for cross-referencing with
    ML model prediction.
    """
    text_lower = text.lower()
    for alias, poison in POISON_ALIASES.items():
        if alias in text_lower:
            return poison
    return None


def build_model_input(symptoms_text: str) -> Dict[str, any]:
    """
    Full preprocessing pipeline: clean → normalize → structure
    for the DistilBERT model.
    """
    normalized = normalize_symptoms(symptoms_text)
    symptoms_list = extract_symptoms_list(symptoms_text)
    suspected = detect_suspected_poison(symptoms_text)

    return {
        "model_input": normalized,
        "symptoms_list": symptoms_list,
        "suspected_poison": suspected,
        "original_text": symptoms_text,
    }
