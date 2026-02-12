import pandas as pd
import random
import uuid
import os

# -----------------------------
# 1. Poison master data (expanded to 15 poisons for better model coverage)
# -----------------------------
pois = [
    ("Carbon Monoxide", "Gas", "Oxygen Therapy", ["headache", "dizziness", "nausea", "confusion", "weakness", "chest pain", "drowsiness"], "Stabilize airway"),
    ("Cyanide", "Industrial", "Hydroxocobalamin", ["shortness of breath", "chest pain", "vomiting", "confusion", "seizures", "dizziness", "headache"], "Administer antidote immediately"),
    ("Methanol", "Alcohol", "Fomepizole", ["blurred vision", "nausea", "vomiting", "abdominal pain", "dizziness", "headache", "confusion"], "Supportive care and antidote"),
    ("Ethylene Glycol", "Household Chemical", "Fomepizole", ["vomiting", "abdominal pain", "confusion", "fatigue", "shortness of breath", "nausea", "drowsiness"], "Supportive care and antidote"),
    ("Arsenic", "Heavy Metal", "Dimercaprol", ["abdominal pain", "vomiting", "diarrhea", "skin changes", "confusion", "fatigue", "muscle weakness"], "Chelation therapy"),
    ("Lead", "Heavy Metal", "EDTA", ["abdominal pain", "constipation", "fatigue", "headache", "memory loss", "irritability", "nausea"], "Chelation therapy"),
    ("Mercury", "Heavy Metal", "Dimercaprol", ["tremors", "irritability", "memory loss", "fatigue", "muscle weakness", "headache", "nausea"], "Chelation therapy"),
    ("Organophosphate", "Pesticide", "Atropine", ["salivation", "sweating", "vomiting", "diarrhea", "muscle twitching", "confusion", "shortness of breath"], "Administer antidote and supportive care"),
    ("Acetaminophen", "Drug Overdose", "N-acetylcysteine", ["nausea", "vomiting", "loss of appetite", "abdominal pain", "fatigue", "drowsiness", "confusion"], "Antidote therapy"),
    ("Opioids", "Drug Overdose", "Naloxone", ["drowsiness", "pinpoint pupils", "respiratory depression", "confusion", "nausea", "dizziness", "weakness"], "Administer antidote and monitor"),
    ("Iron", "Drug Overdose", "Deferoxamine", ["vomiting", "diarrhea", "abdominal pain", "drowsiness", "nausea", "fatigue", "confusion"], "Chelation and supportive care"),
    ("Aluminium Phosphide", "Pesticide", "Supportive Care", ["vomiting", "abdominal pain", "shortness of breath", "dizziness", "chest pain", "confusion", "fatigue"], "Immediate gastric lavage and supportive care"),
    ("Benzodiazepines", "Drug Overdose", "Flumazenil", ["drowsiness", "confusion", "dizziness", "weakness", "respiratory depression", "blurred vision", "nausea"], "Antidote therapy and monitoring"),
    ("Corrosive Acids", "Household Chemical", "Supportive Care", ["abdominal pain", "vomiting", "chest pain", "shortness of breath", "skin changes", "diarrhea", "confusion"], "Do NOT induce vomiting, dilute and supportive care"),
    ("Mushroom Toxins", "Natural", "Supportive Care", ["nausea", "vomiting", "diarrhea", "abdominal pain", "confusion", "fatigue", "drowsiness"], "Aggressive hydration and hepatoprotection"),
]

exposure_routes = ["Ingestion", "Inhalation", "Dermal", "Injection", "Ocular"]
severity_levels = ["Low", "Moderate", "High"]
age_groups = ["Pediatric (0-12)", "Adolescent (13-18)", "Adult (19-60)", "Elderly (60+)"]
locations = [
    "Bir Hospital", "TUTH", "Civil Service Hospital",
    "Patan Hospital", "Nepal Medical College", "Central Store",
    "Bhaktapur Hospital", "Bharatpur Hospital", "Western Regional Hospital"
]

# -----------------------------
# 2. Generate dataset
# -----------------------------
def generate_dataset(num_rows_per_poison: int = 120, output_dir: str = None) -> pd.DataFrame:
    """
    Generate synthetic poison symptom dataset for NLP model training.
    
    Args:
        num_rows_per_poison: Number of rows to generate per poison type.
        output_dir: Directory to save CSV. If None, saves to current directory.
    
    Returns:
        DataFrame with generated data.
    """
    records = []
    
    for poison_name, category, antidote, symptoms_list, protocol in pois:
        for _ in range(num_rows_per_poison):
            # Randomly pick 3-5 symptoms for variation
            num_symptoms = random.randint(3, min(5, len(symptoms_list)))
            selected_symptoms = random.sample(symptoms_list, num_symptoms)
            
            # Randomly shuffle symptom order for training robustness
            random.shuffle(selected_symptoms)
            
            record = {
                "case_id": str(uuid.uuid4()),
                "poison_name": poison_name,
                "poison_category": category,
                "antidote": antidote,
                "antidote_availability_location": random.choice(locations),
                "symptoms": ", ".join(selected_symptoms),
                "management_protocol": protocol,
                "exposure_route": random.choice(exposure_routes),
                "severity_level": random.choice(severity_levels),
                "age_group": random.choice(age_groups),
                "city": "Kathmandu",
            }
            records.append(record)
    
    df = pd.DataFrame(records)
    df['input_text'] = df['symptoms']
    
    # Save to CSV
    filename = "symptom_based_poison_dataset_1200.csv"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
    else:
        filepath = filename
    
    df.to_csv(filepath, index=False)
    print(f"Dataset generated: {df.shape} -> {filepath}")
    print(f"  Poison types: {df['poison_name'].nunique()}")
    print(f"  Categories: {df['poison_category'].unique().tolist()}")
    
    return df


if __name__ == "__main__":
    df = generate_dataset(num_rows_per_poison=120)
    print(f"\nSample rows:\n{df.head()}")

