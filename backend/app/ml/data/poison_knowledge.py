# Poison Knowledge Dataset for RAG
# This module implements the Poison Info RAG retriever for the PoisonSense AI

"""
Poison Knowledge RAG Dataset
=============================
Structured poison entries for retrieval-augmented generation.

Each entry contains:
- Basic identification
- Symptoms and danger signs
- Antidote existence info
- Safety do's and don'ts
- Source references

⚠️ This is INFORMATIONAL ONLY. No treatment procedures.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PoisonCategory(str, Enum):
    PESTICIDE = "pesticide"
    HOUSEHOLD = "household_cleaner"
    MEDICINE = "medicine_overdose"
    PLANT = "plant"
    ANIMAL = "animal_venom"
    GAS = "gas_inhalation"
    INDUSTRIAL = "industrial_chemical"
    FOOD = "food_poisoning"
    HEAVY_METAL = "heavy_metal"
    ALCOHOL = "alcohol"


class ExposureRoute(str, Enum):
    INGESTION = "ingestion"
    INHALATION = "inhalation"
    SKIN = "skin_contact"
    EYE = "eye_contact"
    INJECTION = "injection"
    BITE = "bite"


class RiskLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    LIFE_THREATENING = "Life-threatening"


@dataclass
class PoisonEntry:
    """Structured poison knowledge entry for RAG"""
    poison_id: str
    poison_name: str
    aliases: List[str]  # Local/common names
    category: PoisonCategory
    routes: List[ExposureRoute]
    risk_level: RiskLevel
    typical_symptoms_early: List[str]
    danger_signs_emergency: List[str]
    antidote_exists: str  # "Yes", "No", "Conditional"
    antidote_names: List[str]  # Names only, no dosing
    clinical_notes: str  # High-level info, no procedures
    do_not_do: List[str]  # Safety warnings
    source_refs: List[str]


# =============================================================================
# POISON KNOWLEDGE DATABASE (RAG Content)
# =============================================================================

POISON_KNOWLEDGE: Dict[str, dict] = {
    # =========================================================================
    # PESTICIDES / AGRICULTURAL
    # =========================================================================
    "organophosphate": {
        "poison_id": "organophosphate",
        "poison_name": "Organophosphate Compounds",
        "aliases": [
            "Malathion", "Parathion", "Chlorpyrifos", "Diazinon", "Monocrotophos",
            "Metacid", "Nuvan", "Dichlorvos", "DDVP", "Phorate",
            "Pesticide", "Insecticide", "Bug spray", "Farm chemical"
        ],
        "category": PoisonCategory.PESTICIDE,
        "routes": [ExposureRoute.INGESTION, ExposureRoute.INHALATION, ExposureRoute.SKIN],
        "risk_level": RiskLevel.LIFE_THREATENING,
        "typical_symptoms_early": [
            "Excessive salivation", "Tearing (lacrimation)", "Urination",
            "Diarrhea", "Nausea/vomiting", "Pinpoint pupils (miosis)",
            "Excessive sweating", "Muscle twitching", "Bradycardia"
        ],
        "danger_signs_emergency": [
            "Difficulty breathing", "Seizures", "Unconsciousness",
            "Respiratory failure", "Coma", "Cardiac arrest",
            "Blue lips (cyanosis)", "No pulse"
        ],
        "antidote_exists": "Yes",
        "antidote_names": ["Atropine", "Pralidoxime (2-PAM)"],
        "clinical_notes": "Organophosphates inhibit acetylcholinesterase enzyme. SLUDGE syndrome (Salivation, Lacrimation, Urination, Defecation, GI distress, Emesis) is characteristic. Blood cholinesterase levels confirm diagnosis.",
        "do_not_do": [
            "Do NOT induce vomiting - aspiration risk",
            "Do NOT give oil-based liquids",
            "Do NOT delay - this is a medical emergency",
            "Do NOT attempt home treatment",
            "Remove contaminated clothing carefully"
        ],
        "source_refs": ["WHO Pesticide Guidelines", "NPIC Treatment Protocol", "CDC Toxicology"]
    },
    
    "carbamate": {
        "poison_id": "carbamate",
        "poison_name": "Carbamate Insecticides",
        "aliases": [
            "Carbaryl", "Sevin", "Carbofuran", "Furadan", "Methomyl",
            "Aldicarb", "Propoxur", "Baygon"
        ],
        "category": PoisonCategory.PESTICIDE,
        "routes": [ExposureRoute.INGESTION, ExposureRoute.INHALATION, ExposureRoute.SKIN],
        "risk_level": RiskLevel.HIGH,
        "typical_symptoms_early": [
            "Similar to organophosphate (SLUDGE syndrome)",
            "Excessive secretions", "Pinpoint pupils",
            "Muscle weakness", "Nausea/vomiting"
        ],
        "danger_signs_emergency": [
            "Respiratory distress", "Seizures", "Coma",
            "Severe bronchospasm"
        ],
        "antidote_exists": "Yes",
        "antidote_names": ["Atropine"],
        "clinical_notes": "Similar to organophosphate but cholinesterase inhibition is reversible. Pralidoxime generally NOT used for carbamates. Recovery often faster than organophosphate poisoning.",
        "do_not_do": [
            "Do NOT induce vomiting",
            "Do NOT give pralidoxime (2-PAM) - may worsen in some carbamates",
            "Do NOT delay medical care"
        ],
        "source_refs": ["WHO Pesticide Guidelines", "Clinical Toxicology"]
    },
    
    "paraquat": {
        "poison_id": "paraquat",
        "poison_name": "Paraquat Herbicide",
        "aliases": [
            "Gramoxone", "Weedol", "Pathclear", "Herbicide"
        ],
        "category": PoisonCategory.PESTICIDE,
        "routes": [ExposureRoute.INGESTION, ExposureRoute.SKIN, ExposureRoute.INHALATION],
        "risk_level": RiskLevel.LIFE_THREATENING,
        "typical_symptoms_early": [
            "Oral/throat burns", "Severe mouth ulcers",
            "Nausea/vomiting", "Abdominal pain",
            "Diarrhea (may be bloody)"
        ],
        "danger_signs_emergency": [
            "Respiratory failure (may occur days later)",
            "Pulmonary fibrosis", "Multi-organ failure",
            "Kidney failure", "Liver failure"
        ],
        "antidote_exists": "No",
        "antidote_names": [],
        "clinical_notes": "Extremely toxic herbicide with NO specific antidote. Even small amounts can be fatal. Pulmonary toxicity may be delayed 2-14 days. High oxygen can worsen lung damage.",
        "do_not_do": [
            "Do NOT give high-flow oxygen initially (worsens lung damage)",
            "Do NOT induce vomiting",
            "Do NOT delay - extremely time-sensitive",
            "Activated charcoal helpful only within 1 hour"
        ],
        "source_refs": ["WHO Guidelines", "Paraquat Toxicity Literature"]
    },
    
    # =========================================================================
    # HOUSEHOLD CHEMICALS
    # =========================================================================
    "corrosive_acid": {
        "poison_id": "corrosive_acid",
        "poison_name": "Corrosive Acids",
        "aliases": [
            "Toilet cleaner", "Drain cleaner", "Battery acid",
            "Hydrochloric acid", "Sulfuric acid", "Muriatic acid",
            "Descaler", "Rust remover"
        ],
        "category": PoisonCategory.HOUSEHOLD,
        "routes": [ExposureRoute.INGESTION, ExposureRoute.SKIN, ExposureRoute.EYE],
        "risk_level": RiskLevel.HIGH,
        "typical_symptoms_early": [
            "Severe burning pain (mouth, throat, stomach)",
            "Drooling", "Difficulty swallowing",
            "Burns around mouth/lips", "Hoarseness"
        ],
        "danger_signs_emergency": [
            "Vomiting blood", "Airway compromise",
            "Respiratory distress", "Shock",
            "Perforation of GI tract"
        ],
        "antidote_exists": "No",
        "antidote_names": [],
        "clinical_notes": "Acids cause coagulation necrosis. Damage depends on concentration, amount, and contact time. Esophageal/gastric perforation is major risk. Endoscopy needed to assess damage.",
        "do_not_do": [
            "Do NOT induce vomiting - causes re-exposure and perforation risk",
            "Do NOT give neutralizing agents (alkali) - causes heat reaction",
            "Do NOT give activated charcoal",
            "Do NOT attempt to dilute with large amounts of liquid"
        ],
        "source_refs": ["Emergency Medicine Guidelines", "Poison Control Protocols"]
    },
    
    "corrosive_alkali": {
        "poison_id": "corrosive_alkali",
        "poison_name": "Corrosive Alkalis (Bases)",
        "aliases": [
            "Bleach", "Drain cleaner", "Oven cleaner", "Lye",
            "Sodium hydroxide", "Ammonia", "Caustic soda",
            "Toilet bowl cleaner"
        ],
        "category": PoisonCategory.HOUSEHOLD,
        "routes": [ExposureRoute.INGESTION, ExposureRoute.SKIN, ExposureRoute.EYE, ExposureRoute.INHALATION],
        "risk_level": RiskLevel.HIGH,
        "typical_symptoms_early": [
            "Severe burning pain", "Drooling",
            "Difficulty swallowing", "Soapy taste",
            "Burns with gray/white appearance"
        ],
        "danger_signs_emergency": [
            "Airway swelling", "Respiratory distress",
            "Esophageal perforation", "Shock",
            "Vomiting blood"
        ],
        "antidote_exists": "No",
        "antidote_names": [],
        "clinical_notes": "Alkalis cause liquefactive necrosis - deeper tissue penetration than acids. Higher risk of esophageal injury and stricture formation. Often more dangerous than acid ingestion.",
        "do_not_do": [
            "Do NOT induce vomiting",
            "Do NOT give acidic substances to neutralize",
            "Do NOT give activated charcoal",
            "Do NOT insert NG tube until endoscopy done"
        ],
        "source_refs": ["Emergency Medicine Guidelines", "Toxicology Literature"]
    },
    
    "hydrocarbon": {
        "poison_id": "hydrocarbon",
        "poison_name": "Hydrocarbons",
        "aliases": [
            "Kerosene", "Petrol", "Gasoline", "Diesel",
            "Lamp oil", "Paraffin", "Turpentine", "Paint thinner",
            "Lighter fluid", "Furniture polish"
        ],
        "category": PoisonCategory.HOUSEHOLD,
        "routes": [ExposureRoute.INGESTION, ExposureRoute.INHALATION],
        "risk_level": RiskLevel.HIGH,
        "typical_symptoms_early": [
            "Coughing", "Choking", "Gasping",
            "Petroleum smell on breath",
            "Nausea/vomiting", "Burning sensation in throat"
        ],
        "danger_signs_emergency": [
            "Respiratory distress", "Aspiration pneumonia",
            "Cyanosis (blue lips)", "Altered consciousness",
            "Chemical pneumonitis", "Respiratory failure"
        ],
        "antidote_exists": "No",
        "antidote_names": [],
        "clinical_notes": "Main danger is aspiration into lungs causing chemical pneumonitis. Low viscosity hydrocarbons (kerosene, gasoline) have highest aspiration risk. Even small amounts aspirated can cause severe lung injury.",
        "do_not_do": [
            "Do NOT induce vomiting - high aspiration risk",
            "Do NOT give activated charcoal - not effective, aspiration risk",
            "Do NOT give milk or oils",
            "Do NOT delay if respiratory symptoms develop"
        ],
        "source_refs": ["WHO Guidelines", "Pediatric Toxicology"]
    },
    
    # =========================================================================
    # MEDICATION OVERDOSES
    # =========================================================================
    "acetaminophen": {
        "poison_id": "acetaminophen",
        "poison_name": "Acetaminophen (Paracetamol)",
        "aliases": [
            "Paracetamol", "Tylenol", "Crocin", "Panadol",
            "Calpol", "Dolo", "Fever medicine", "Pain reliever"
        ],
        "category": PoisonCategory.MEDICINE,
        "routes": [ExposureRoute.INGESTION],
        "risk_level": RiskLevel.HIGH,
        "typical_symptoms_early": [
            "Often NO early symptoms (danger!)",
            "Nausea/vomiting", "Abdominal pain",
            "Loss of appetite", "Malaise",
            "Sweating"
        ],
        "danger_signs_emergency": [
            "Right upper quadrant pain (liver)",
            "Jaundice (yellow skin/eyes)",
            "Confusion", "Bleeding",
            "Liver failure", "Coma"
        ],
        "antidote_exists": "Yes",
        "antidote_names": ["N-Acetylcysteine (NAC)", "Acetylcysteine"],
        "clinical_notes": "Liver toxicity may not appear for 24-72 hours. Toxic dose: >150mg/kg in children, >7.5g in adults. Rumack-Matthew nomogram guides treatment. NAC most effective within 8 hours but still beneficial up to 24 hours.",
        "do_not_do": [
            "Do NOT assume safety if no early symptoms",
            "Do NOT delay treatment - liver damage may be delayed",
            "Do NOT exceed recommended doses",
            "Do NOT combine with alcohol"
        ],
        "source_refs": ["Rumack-Matthew Nomogram", "Acetaminophen Toxicity Guidelines"]
    },
    
    "opioid": {
        "poison_id": "opioid",
        "poison_name": "Opioid Overdose",
        "aliases": [
            "Morphine", "Heroin", "Fentanyl", "Codeine",
            "Tramadol", "Oxycodone", "Brown sugar", "Smack",
            "Pethidine", "Methadone", "Hydrocodone"
        ],
        "category": PoisonCategory.MEDICINE,
        "routes": [ExposureRoute.INGESTION, ExposureRoute.INJECTION, ExposureRoute.INHALATION],
        "risk_level": RiskLevel.LIFE_THREATENING,
        "typical_symptoms_early": [
            "Extreme drowsiness", "Pinpoint pupils",
            "Slurred speech", "Slow breathing",
            "Confusion", "Nausea"
        ],
        "danger_signs_emergency": [
            "Respiratory depression/arrest",
            "Unconsciousness", "Blue lips/nails",
            "No response to stimulation",
            "Cardiac arrest"
        ],
        "antidote_exists": "Yes",
        "antidote_names": ["Naloxone (Narcan)"],
        "clinical_notes": "Classic triad: respiratory depression, pinpoint pupils, altered consciousness. Naloxone reverses effects rapidly. May need repeated doses as naloxone wears off before opioid. Fentanyl may require higher naloxone doses.",
        "do_not_do": [
            "Do NOT leave person alone",
            "Do NOT put in bathtub or shower",
            "Do NOT inject with anything except naloxone",
            "Do NOT assume they will 'sleep it off'"
        ],
        "source_refs": ["CDC Opioid Guidelines", "WHO Opioid Overdose"]
    },
    
    "benzodiazepine": {
        "poison_id": "benzodiazepine",
        "poison_name": "Benzodiazepine Overdose",
        "aliases": [
            "Diazepam", "Valium", "Lorazepam", "Ativan",
            "Alprazolam", "Xanax", "Clonazepam", "Sleeping pills"
        ],
        "category": PoisonCategory.MEDICINE,
        "routes": [ExposureRoute.INGESTION],
        "risk_level": RiskLevel.MODERATE,
        "typical_symptoms_early": [
            "Drowsiness", "Confusion", "Slurred speech",
            "Unsteady gait", "Memory impairment",
            "Muscle weakness"
        ],
        "danger_signs_emergency": [
            "Respiratory depression (esp. with opioids/alcohol)",
            "Coma", "Severe hypotension",
            "Paradoxical excitation"
        ],
        "antidote_exists": "Conditional",
        "antidote_names": ["Flumazenil"],
        "clinical_notes": "Pure benzodiazepine overdose rarely fatal. Danger increases dramatically when combined with opioids or alcohol. Flumazenil use controversial - may precipitate seizures in dependent patients.",
        "do_not_do": [
            "Do NOT combine with alcohol or opioids",
            "Do NOT give flumazenil if seizure history",
            "Do NOT leave person unmonitored"
        ],
        "source_refs": ["Toxicology Guidelines", "Emergency Medicine Literature"]
    },
    
    # =========================================================================
    # SNAKE BITES
    # =========================================================================
    "snake_neurotoxic": {
        "poison_id": "snake_neurotoxic",
        "poison_name": "Neurotoxic Snake Bite (Elapidae)",
        "aliases": [
            "Cobra bite", "Krait bite", "Coral snake",
            "Nag", "Karait", "Snake bite"
        ],
        "category": PoisonCategory.ANIMAL,
        "routes": [ExposureRoute.BITE],
        "risk_level": RiskLevel.LIFE_THREATENING,
        "typical_symptoms_early": [
            "Minimal pain at bite site",
            "Drooping eyelids (ptosis)", "Double vision",
            "Difficulty swallowing", "Weakness",
            "Numbness around mouth"
        ],
        "danger_signs_emergency": [
            "Respiratory paralysis",
            "Complete muscle paralysis",
            "Inability to breathe",
            "Respiratory failure"
        ],
        "antidote_exists": "Yes",
        "antidote_names": ["Polyvalent Anti-Snake Venom (ASV)"],
        "clinical_notes": "Neurotoxic venoms affect nerve-muscle junction causing paralysis. Krait bites often occur at night during sleep. Respiratory failure is main cause of death. Neostigmine may help in some cobra bites.",
        "do_not_do": [
            "Do NOT cut the wound or try to suck venom",
            "Do NOT apply tourniquet tightly",
            "Do NOT apply ice or electric shock",
            "Do NOT give alcohol or medications",
            "Do NOT delay reaching hospital"
        ],
        "source_refs": ["WHO Snake Bite Guidelines", "NPIC Nepal Protocol"]
    },
    
    "snake_hemotoxic": {
        "poison_id": "snake_hemotoxic",
        "poison_name": "Hemotoxic Snake Bite (Viperidae)",
        "aliases": [
            "Viper bite", "Russell's viper", "Pit viper",
            "Daboia", "Green pit viper"
        ],
        "category": PoisonCategory.ANIMAL,
        "routes": [ExposureRoute.BITE],
        "risk_level": RiskLevel.LIFE_THREATENING,
        "typical_symptoms_early": [
            "Severe pain at bite site",
            "Rapid swelling", "Bleeding from bite",
            "Bruising", "Blistering"
        ],
        "danger_signs_emergency": [
            "Bleeding from gums, nose, wounds",
            "Blood in urine", "Shock",
            "Kidney failure", "Compartment syndrome",
            "DIC (disseminated intravascular coagulation)"
        ],
        "antidote_exists": "Yes",
        "antidote_names": ["Polyvalent Anti-Snake Venom (ASV)"],
        "clinical_notes": "Hemotoxic venoms cause coagulopathy and tissue destruction. 20-minute whole blood clotting test (20WBCT) useful for diagnosis. Swelling may progress for 24-48 hours. Fasciotomy may be needed for compartment syndrome.",
        "do_not_do": [
            "Do NOT cut or suck the wound",
            "Do NOT apply tight tourniquet",
            "Do NOT apply ice",
            "Do NOT give aspirin or blood thinners",
            "Do NOT delay hospital transport"
        ],
        "source_refs": ["WHO Snake Bite Guidelines", "NPIC Nepal Protocol"]
    },
    
    # =========================================================================
    # PLANTS & MUSHROOMS
    # =========================================================================
    "oleander": {
        "poison_id": "oleander",
        "poison_name": "Oleander Plant",
        "aliases": [
            "Kaner", "Yellow oleander", "Nerium oleander",
            "Thevetia peruviana", "Pila kaner"
        ],
        "category": PoisonCategory.PLANT,
        "routes": [ExposureRoute.INGESTION],
        "risk_level": RiskLevel.HIGH,
        "typical_symptoms_early": [
            "Nausea/vomiting", "Abdominal pain",
            "Diarrhea", "Dizziness",
            "Slow heart rate"
        ],
        "danger_signs_emergency": [
            "Cardiac arrhythmias", "Heart block",
            "Ventricular fibrillation", "Cardiac arrest",
            "Hyperkalemia"
        ],
        "antidote_exists": "Conditional",
        "antidote_names": ["Digoxin-specific Fab antibodies (Digibind)"],
        "clinical_notes": "Contains cardiac glycosides similar to digoxin. All parts of plant are toxic. Common suicide attempt method in South Asia. ECG monitoring essential. May need temporary pacemaker.",
        "do_not_do": [
            "Do NOT induce vomiting if cardiac symptoms present",
            "Do NOT delay if heart rhythm abnormalities",
            "Do NOT underestimate - small amounts can be fatal"
        ],
        "source_refs": ["Plant Toxicology Database", "Nepal Poison Data"]
    },
    
    "mushroom_amatoxin": {
        "poison_id": "mushroom_amatoxin",
        "poison_name": "Amatoxin Mushroom Poisoning",
        "aliases": [
            "Death cap", "Destroying angel", "Amanita phalloides",
            "Amanita virosa", "Wild mushroom"
        ],
        "category": PoisonCategory.PLANT,
        "routes": [ExposureRoute.INGESTION],
        "risk_level": RiskLevel.LIFE_THREATENING,
        "typical_symptoms_early": [
            "DELAYED onset (6-24 hours after eating)",
            "Severe watery diarrhea", "Vomiting",
            "Abdominal cramps", "Dehydration"
        ],
        "danger_signs_emergency": [
            "Liver failure (day 3-5)",
            "Jaundice", "Hepatic encephalopathy",
            "Bleeding", "Kidney failure",
            "Death (day 6-16)"
        ],
        "antidote_exists": "Conditional",
        "antidote_names": ["Silibinin (Milk thistle extract)", "N-Acetylcysteine"],
        "clinical_notes": "Amatoxins destroy liver cells. Key clue: delayed GI symptoms (6+ hours after eating). Initial GI symptoms may improve ('honeymoon phase') before liver failure. Liver transplant may be only option in severe cases.",
        "do_not_do": [
            "Do NOT assume recovery if symptoms improve",
            "Do NOT delay - early treatment critical",
            "Do NOT eat wild mushrooms unless expert identified"
        ],
        "source_refs": ["Mushroom Toxicology", "Hepatology Guidelines"]
    },
    
    # =========================================================================
    # ALCOHOLS
    # =========================================================================
    "methanol": {
        "poison_id": "methanol",
        "poison_name": "Methanol (Wood Alcohol)",
        "aliases": [
            "Wood alcohol", "Spurious liquor", "Hooch",
            "Country liquor", "Bootleg alcohol", "Methylated spirit"
        ],
        "category": PoisonCategory.ALCOHOL,
        "routes": [ExposureRoute.INGESTION],
        "risk_level": RiskLevel.LIFE_THREATENING,
        "typical_symptoms_early": [
            "Similar to ethanol intoxication initially",
            "Headache", "Dizziness", "Nausea",
            "Confusion (after 12-24 hour delay)"
        ],
        "danger_signs_emergency": [
            "Visual disturbances ('snowfield vision')",
            "Blindness", "Severe metabolic acidosis",
            "Coma", "Respiratory failure", "Death"
        ],
        "antidote_exists": "Yes",
        "antidote_names": ["Fomepizole", "Ethanol (IV)"],
        "clinical_notes": "Metabolized to formaldehyde and formic acid (toxic). Visual symptoms are characteristic. Hemodialysis indicated for severe cases. Ethanol blocks metabolism of methanol.",
        "do_not_do": [
            "Do NOT wait for symptoms - may be delayed 12-24 hours",
            "Do NOT drink unknown/cheap alcohol",
            "Do NOT delay if suspected - vision damage may be permanent"
        ],
        "source_refs": ["WHO Methanol Guidelines", "Toxicology Literature"]
    },
    
    "ethylene_glycol": {
        "poison_id": "ethylene_glycol",
        "poison_name": "Ethylene Glycol",
        "aliases": [
            "Antifreeze", "Coolant", "Brake fluid"
        ],
        "category": PoisonCategory.ALCOHOL,
        "routes": [ExposureRoute.INGESTION],
        "risk_level": RiskLevel.LIFE_THREATENING,
        "typical_symptoms_early": [
            "Appears drunk without alcohol smell",
            "Nausea/vomiting", "Confusion",
            "Slurred speech"
        ],
        "danger_signs_emergency": [
            "Severe metabolic acidosis",
            "Kidney failure", "Pulmonary edema",
            "Coma", "Cardiac failure"
        ],
        "antidote_exists": "Yes",
        "antidote_names": ["Fomepizole", "Ethanol (IV)"],
        "clinical_notes": "Metabolized to glycolic and oxalic acid. Calcium oxalate crystals damage kidneys. Three stages: neurological (1-12h), cardiopulmonary (12-24h), renal (24-72h). Hemodialysis for severe cases.",
        "do_not_do": [
            "Do NOT delay treatment - kidney damage may be permanent",
            "Do NOT assume safe because 'sweet taste'",
            "Store antifreeze safely away from children"
        ],
        "source_refs": ["Toxicology Guidelines", "Emergency Medicine Literature"]
    },
    
    # =========================================================================
    # RAT POISONS
    # =========================================================================
    "warfarin_rodenticide": {
        "poison_id": "warfarin_rodenticide",
        "poison_name": "Anticoagulant Rodenticides",
        "aliases": [
            "Rat poison", "Mouse poison", "Warfarin",
            "Brodifacoum", "Bromadiolone", "Ratol"
        ],
        "category": PoisonCategory.PESTICIDE,
        "routes": [ExposureRoute.INGESTION],
        "risk_level": RiskLevel.MODERATE,
        "typical_symptoms_early": [
            "Often NO early symptoms",
            "Easy bruising", "Nosebleeds",
            "Bleeding gums"
        ],
        "danger_signs_emergency": [
            "Spontaneous bleeding",
            "Blood in urine/stool",
            "Intracranial hemorrhage",
            "Severe anemia"
        ],
        "antidote_exists": "Yes",
        "antidote_names": ["Vitamin K1 (Phytonadione)"],
        "clinical_notes": "Superwarfarins (brodifacoum) have very long half-life - may need Vitamin K1 for weeks/months. INR/PT monitoring essential. Single small ingestion in children usually not significant.",
        "do_not_do": [
            "Do NOT ignore small ingestions in children",
            "Do NOT stop Vitamin K1 without medical guidance",
            "Do NOT use Vitamin K3 - must be K1"
        ],
        "source_refs": ["Poison Control Guidelines", "Toxicology Literature"]
    }
}


# =============================================================================
# RAG RETRIEVER FUNCTIONS
# =============================================================================

def retrieve_poison_by_name(query: str) -> Optional[dict]:
    """
    RAG Retriever: Find poison information by name or alias.
    
    Searches poison_name and aliases fields.
    """
    query_lower = query.lower()
    
    # Direct match first
    if query_lower in POISON_KNOWLEDGE:
        return POISON_KNOWLEDGE[query_lower]
    
    # Search in names and aliases
    best_match = None
    best_score = 0
    
    for poison_id, poison in POISON_KNOWLEDGE.items():
        score = 0
        
        # Check poison name
        if query_lower in poison["poison_name"].lower():
            score += 3
        
        # Check aliases
        for alias in poison["aliases"]:
            if query_lower in alias.lower():
                score += 2
                break
            if alias.lower() in query_lower:
                score += 1
                break
        
        if score > best_score:
            best_score = score
            best_match = poison
    
    return best_match if best_score > 0 else None


def retrieve_poison_by_symptoms(symptoms: List[str], limit: int = 3) -> List[dict]:
    """
    RAG Retriever: Find possible poisons based on symptoms.
    
    Searches typical_symptoms_early and danger_signs_emergency.
    """
    results = []
    
    for poison_id, poison in POISON_KNOWLEDGE.items():
        score = 0
        matched_symptoms = []
        
        all_symptoms = (
            poison.get("typical_symptoms_early", []) + 
            poison.get("danger_signs_emergency", [])
        )
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for poison_symptom in all_symptoms:
                if symptom_lower in poison_symptom.lower():
                    score += 1
                    matched_symptoms.append(poison_symptom)
                    break
        
        if score > 0:
            results.append({
                "poison_id": poison_id,
                "poison_name": poison["poison_name"],
                "category": poison["category"].value if isinstance(poison["category"], PoisonCategory) else poison["category"],
                "risk_level": poison["risk_level"].value if isinstance(poison["risk_level"], RiskLevel) else poison["risk_level"],
                "match_score": score,
                "matched_symptoms": matched_symptoms,
                "antidote_exists": poison["antidote_exists"]
            })
    
    # Sort by score
    results.sort(key=lambda x: -x["match_score"])
    return results[:limit]


def retrieve_poison_by_category(category: str, limit: int = 10) -> List[dict]:
    """
    RAG Retriever: Find poisons by category.
    
    Example categories: "pesticide", "household", "medicine", "plant", "animal"
    """
    results = []
    category_lower = category.lower()
    
    for poison_id, poison in POISON_KNOWLEDGE.items():
        poison_category = poison["category"]
        if isinstance(poison_category, PoisonCategory):
            poison_category = poison_category.value
        
        if category_lower in poison_category.lower():
            results.append({
                "poison_id": poison_id,
                "poison_name": poison["poison_name"],
                "aliases": poison["aliases"][:5],
                "risk_level": poison["risk_level"].value if isinstance(poison["risk_level"], RiskLevel) else poison["risk_level"],
                "antidote_exists": poison["antidote_exists"]
            })
    
    return results[:limit]


def get_poison_safety_info(poison_id: str) -> Optional[dict]:
    """
    Get safety do's and don'ts for a poison.
    """
    poison = POISON_KNOWLEDGE.get(poison_id)
    if not poison:
        return None
    
    return {
        "poison_name": poison["poison_name"],
        "do_not_do": poison["do_not_do"],
        "antidote_exists": poison["antidote_exists"],
        "antidote_names": poison["antidote_names"],
        "risk_level": poison["risk_level"].value if isinstance(poison["risk_level"], RiskLevel) else poison["risk_level"],
        "source_refs": poison["source_refs"]
    }


def get_antidote_info(poison_id: str) -> Optional[dict]:
    """
    Get antidote information for a poison (names only, no dosing).
    """
    poison = POISON_KNOWLEDGE.get(poison_id)
    if not poison:
        return None
    
    return {
        "poison_name": poison["poison_name"],
        "antidote_exists": poison["antidote_exists"],
        "antidote_names": poison["antidote_names"],
        "clinical_notes": poison["clinical_notes"],
        "note": "Antidote administration should be done by medical professionals only"
    }


def get_emergency_signs(poison_id: str) -> Optional[dict]:
    """
    Get emergency/danger signs for a poison.
    """
    poison = POISON_KNOWLEDGE.get(poison_id)
    if not poison:
        return None
    
    return {
        "poison_name": poison["poison_name"],
        "risk_level": poison["risk_level"].value if isinstance(poison["risk_level"], RiskLevel) else poison["risk_level"],
        "danger_signs_emergency": poison["danger_signs_emergency"],
        "typical_symptoms_early": poison["typical_symptoms_early"],
        "note": "If any danger signs present, seek emergency care immediately"
    }


def get_all_poisons_summary() -> List[dict]:
    """
    Get a summary of all poisons in the knowledge base.
    """
    return [
        {
            "poison_id": pid,
            "poison_name": p["poison_name"],
            "category": p["category"].value if isinstance(p["category"], PoisonCategory) else p["category"],
            "risk_level": p["risk_level"].value if isinstance(p["risk_level"], RiskLevel) else p["risk_level"],
            "antidote_exists": p["antidote_exists"]
        }
        for pid, p in POISON_KNOWLEDGE.items()
    ]
