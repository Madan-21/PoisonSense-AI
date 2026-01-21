import pandas as pd
import random
import uuid

# -----------------------------
# 1. Poison master data
# -----------------------------
pois = [
    ("Carbon Monoxide", "Gas", "Oxygen Therapy", ["headache", "dizziness", "nausea", "confusion", "weakness"], "Stabilize airway"),
    ("Cyanide", "Industrial", "Hydroxocobalamin", ["shortness of breath", "chest pain", "vomiting", "confusion", "seizures"], "Administer antidote immediately"),
    ("Methanol", "Alcohol", "Fomepizole", ["blurred vision", "nausea", "vomiting", "abdominal pain", "dizziness"], "Supportive care and antidote"),
    ("Ethylene Glycol", "Household Chemical", "Fomepizole", ["vomiting", "abdominal pain", "confusion", "fatigue", "shortness of breath"], "Supportive care and antidote"),
    ("Arsenic", "Heavy Metal", "Dimercaprol", ["abdominal pain", "vomiting", "diarrhea", "skin changes", "confusion"], "Chelation therapy"),
    ("Lead", "Heavy Metal", "EDTA", ["abdominal pain", "constipation", "fatigue", "headache", "memory loss"], "Chelation therapy"),
    ("Mercury", "Heavy Metal", "Dimercaprol", ["tremors", "irritability", "memory loss", "fatigue", "muscle weakness"], "Chelation therapy"),
    ("Organophosphate", "Pesticide", "Atropine", ["salivation", "sweating", "vomiting", "diarrhea", "muscle twitching"], "Administer antidote and supportive care"),
    ("Acetaminophen", "Drug Overdose", "N-acetylcysteine", ["nausea", "vomiting", "loss of appetite", "abdominal pain", "fatigue"], "Antidote therapy"),
    ("Opioids", "Drug Overdose", "Naloxone", ["drowsiness", "pinpoint pupils", "respiratory depression", "confusion", "nausea"], "Administer antidote and monitor")
]

exposure_routes = ["Ingestion", "Inhalation", "Dermal"]
severity_levels = ["Low", "Moderate", "High"]
locations = ["Bir Hospital", "TUTH", "Civil Service Hospital", "Private Hospital", "Central Store"]

# -----------------------------
# 2. Generate dataset
# -----------------------------
records = []
num_rows_per_poison = 120  # 10 poisons x 120 = 1200 rows

for poison_name, category, antidote, symptoms_list, protocol in pois:
    for _ in range(num_rows_per_poison):
        record = {
            "case_id": str(uuid.uuid4()),
            "poison_name": poison_name,
            "poison_category": category,
            "antidote": antidote,
            "antidote_availability_location": random.choice(locations),
            "symptoms": ", ".join(random.sample(symptoms_list, 3)),  # pick 3 symptoms
            "management_protocol": protocol,
            "exposure_route": random.choice(exposure_routes),
            "severity_level": random.choice(severity_levels),
            "city": "Kathmandu",
        }
        records.append(record)

df = pd.DataFrame(records)
df['input_text'] = df['symptoms']

# Save to CSV
df.to_csv("symptom_based_poison_dataset_1200.csv", index=False)
print("Dataset generated:", df.shape)
