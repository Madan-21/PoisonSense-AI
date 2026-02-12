# Comprehensive Toxicology Database - Real Medical Data
# Sources: WHO, CDC, NPIC, UpToDate, Toxinology databases, Medical literature

"""
This module contains comprehensive real toxicology data compiled from:
- World Health Organization (WHO) Guidelines
- Centers for Disease Control and Prevention (CDC)
- National Poison Information Centres
- Clinical Toxicology literature
- Emergency Medicine databases
"""

from typing import Dict, List

# =============================================================================
# COMPREHENSIVE POISON DATABASE WITH REAL MEDICAL DATA
# =============================================================================

COMPREHENSIVE_POISONS = {
    # =========================================================================
    # CATEGORY 1: PESTICIDES/AGRICULTURAL CHEMICALS
    # =========================================================================
    "organophosphate": {
        "name": "Organophosphate Compounds",
        "category": "agricultural",
        "common_names": [
            "Malathion", "Parathion", "Chlorpyrifos", "Diazinon", "Dimethoate",
            "Monocrotophos", "Quinalphos", "Methyl Parathion", "Fenthion",
            "Profenofos", "Dichlorvos", "DDVP", "Phorate", "Methamidophos"
        ],
        "common_sources": [
            "Agricultural pesticides", "Insecticides", "Farm chemicals",
            "Household bug sprays", "Flea control products", "Garden sprays",
            "Nerve agents (military)", "Veterinary products"
        ],
        "mechanism_of_action": "Irreversible inhibition of acetylcholinesterase enzyme, leading to accumulation of acetylcholine at synapses",
        "toxic_dose": {
            "malathion": "350mg/kg (low toxicity)",
            "parathion": "3-5mg/kg (high toxicity)",
            "chlorpyrifos": "50-500mg/kg",
            "general": "Varies widely; even small amounts of highly toxic compounds can be lethal"
        },
        "symptoms_immediate": [
            "Excessive salivation (SLUDGE syndrome)", "Lacrimation (tearing)",
            "Urination", "Defecation/Diarrhea", "GI distress", "Emesis (vomiting)",
            "Miosis (pinpoint pupils)", "Bradycardia", "Bronchorrhea",
            "Bronchospasm", "Muscle fasciculations", "Sweating (diaphoresis)"
        ],
        "symptoms_delayed": [
            "Respiratory failure", "Seizures", "Coma", "Intermediate syndrome (24-96h)",
            "Organophosphate-induced delayed neuropathy (OPIDN - 1-3 weeks)",
            "Paralysis of proximal muscles", "Cranial nerve palsies"
        ],
        "cholinergic_toxidrome": {
            "muscarinic": ["Salivation", "Lacrimation", "Urination", "Defecation", "GI cramps", "Emesis", "Miosis", "Bradycardia", "Bronchospasm", "Bronchorrhea"],
            "nicotinic": ["Muscle fasciculations", "Weakness", "Paralysis", "Tachycardia", "Hypertension", "Mydriasis"],
            "cns": ["Anxiety", "Restlessness", "Seizures", "Coma", "Respiratory depression"]
        },
        "antidote": {
            "primary": "Atropine + Pralidoxime (2-PAM)",
            "atropine_dose": {
                "adult": "2-4mg IV initially, double dose every 5-10 minutes until atropinization (dry secretions, tachycardia, mydriasis)",
                "pediatric": "0.02-0.05mg/kg IV, minimum 0.1mg",
                "maintenance": "May need 10-100mg/hour infusion in severe cases",
                "endpoint": "Drying of secretions (NOT heart rate or pupil size)"
            },
            "pralidoxime_dose": {
                "adult": "1-2g IV over 15-30 minutes, then 500mg/hr infusion",
                "pediatric": "25-50mg/kg IV over 15-30 minutes",
                "timing": "Most effective within 24-48 hours; may still help up to 7 days",
                "caution": "Rapid infusion can cause hypertension, rigidity"
            }
        },
        "first_aid": [
            "Remove from exposure immediately",
            "Remove ALL contaminated clothing (double-bag)",
            "Healthcare workers must use PPE (gloves, gown)",
            "Wash entire body with soap and water for 15-20 minutes",
            "Pay attention to hair, nails, skin folds",
            "Do NOT induce vomiting",
            "If eye exposure: irrigate with water for 20+ minutes",
            "Call poison control immediately"
        ],
        "decontamination": {
            "skin": "Remove clothing, wash with soap/water, alkaline soap better",
            "gi": "Gastric lavage if <1 hour and airway protected; Activated charcoal 1g/kg",
            "eyes": "Copious irrigation with saline/water for minimum 20 minutes"
        },
        "management_protocol": [
            "1. ABCs - Secure airway early (risk of respiratory failure)",
            "2. Establish IV access, continuous monitoring",
            "3. Decontamination with full PPE",
            "4. Atropine IV - titrate to dry secretions",
            "5. Pralidoxime IV within 24-48 hours",
            "6. Benzodiazepines for seizures (diazepam 5-10mg IV)",
            "7. Do NOT use succinylcholine for intubation",
            "8. Monitor for intermediate syndrome (days 2-4)",
            "9. Ventilatory support as needed (may be prolonged)"
        ],
        "contraindications": [
            "Morphine and other opioids (respiratory depression)",
            "Aminophylline (seizure risk)",
            "Succinylcholine (prolonged paralysis)",
            "Phenothiazines (may worsen toxicity)"
        ],
        "tests_required": [
            "Red blood cell cholinesterase level",
            "Plasma/serum cholinesterase (pseudocholinesterase)",
            "Arterial blood gas",
            "Serum electrolytes",
            "Blood glucose",
            "ECG (QTc prolongation)",
            "Chest X-ray (aspiration, pulmonary edema)"
        ],
        "monitoring_parameters": [
            "Respiratory rate and oxygen saturation",
            "Heart rate and blood pressure",
            "Pupil size (may be unreliable after atropine)",
            "Secretions (best indicator for atropine dosing)",
            "Muscle strength",
            "Level of consciousness",
            "Cholinesterase levels (serial)"
        ],
        "prognosis": {
            "favorable": "Early treatment with adequate atropine and pralidoxime",
            "poor_indicators": ["Respiratory failure", "Prolonged coma", "Intermediate syndrome"],
            "mortality": "5-25% depending on compound and treatment delay"
        },
        "data_sources": [
            {"name": "WHO Guidelines on Organophosphate Poisoning", "type": "international", "year": 2023},
            {"name": "Clinical Management of Poisoning (4th Ed)", "type": "textbook", "year": 2022},
            {"name": "Nepal NPIC Treatment Protocols", "type": "national", "year": 2023},
            {"name": "UpToDate: Organophosphate and Carbamate Poisoning", "type": "database", "year": 2024}
        ]
    },
    
    "carbamate": {
        "name": "Carbamate Insecticides",
        "category": "agricultural",
        "common_names": [
            "Carbofuran", "Carbaryl", "Propoxur", "Aldicarb", "Methomyl",
            "Carbosulfan", "Bendiocarb", "Pirimicarb"
        ],
        "common_sources": [
            "Insecticides", "Pest control", "Agricultural chemicals",
            "Home garden products", "Veterinary products"
        ],
        "mechanism_of_action": "Reversible inhibition of acetylcholinesterase (shorter duration than organophosphates)",
        "symptoms_immediate": [
            "Similar to organophosphates but shorter duration",
            "SLUDGE syndrome", "Miosis", "Bradycardia",
            "Muscle weakness", "Fasciculations"
        ],
        "symptoms_delayed": [
            "Usually resolves within 24-48 hours",
            "Intermediate syndrome is rare"
        ],
        "antidote": {
            "primary": "Atropine ONLY",
            "note": "Pralidoxime generally NOT recommended (may worsen in some carbamates)",
            "atropine_dose": "Same as organophosphate protocol"
        },
        "management_protocol": [
            "Similar to organophosphates",
            "Pralidoxime generally NOT indicated",
            "Recovery usually faster than OP poisoning"
        ],
        "data_sources": [
            {"name": "WHO Pesticide Poisoning Guidelines", "type": "international", "year": 2023}
        ]
    },

    "paraquat": {
        "name": "Paraquat",
        "category": "agricultural",
        "common_names": ["Paraquat dichloride", "Gramoxone", "Parazone", "Weedol"],
        "common_sources": ["Herbicides", "Weed killers", "Agricultural chemicals"],
        "mechanism_of_action": "Generates superoxide radicals causing lipid peroxidation and cell death, primarily in lungs",
        "toxic_dose": {
            "lethal": "20-40mg/kg (one mouthful of concentrate can be fatal)",
            "warning": "Extremely toxic - no effective antidote"
        },
        "symptoms_immediate": [
            "Oral/pharyngeal pain and ulceration",
            "Nausea, vomiting, diarrhea",
            "Difficulty swallowing",
            "Abdominal pain"
        ],
        "symptoms_delayed": [
            "Pulmonary fibrosis (2-14 days) - IRREVERSIBLE",
            "Renal failure",
            "Hepatic failure",
            "Cardiac failure",
            "Multi-organ failure"
        ],
        "antidote": {
            "primary": "NO SPECIFIC ANTIDOTE",
            "note": "Treatment is supportive and largely unsuccessful in significant ingestions"
        },
        "first_aid": [
            "Immediate gastric decontamination is CRITICAL",
            "Fuller's earth or bentonite clay if available",
            "Activated charcoal 1-2g/kg",
            "Do NOT give oxygen unless hypoxic (enhances toxicity)"
        ],
        "management_protocol": [
            "AVOID high-flow oxygen (paradoxically increases toxicity)",
            "Fuller's earth or activated charcoal immediately",
            "IV fluids",
            "Hemodialysis may help if started within 4 hours",
            "Immunosuppression (cyclophosphamide + steroids) controversial"
        ],
        "contraindications": [
            "High-flow oxygen (accelerates lung damage)",
            "Delays in decontamination"
        ],
        "prognosis": {
            "note": "Extremely poor for significant ingestions",
            "mortality": ">50% for ingestions >40mg/kg; nearly 100% for large ingestions"
        },
        "data_sources": [
            {"name": "WHO Paraquat Poisoning Guidelines", "type": "international", "year": 2022},
            {"name": "Clinical Toxicology Journal", "type": "research", "year": 2023}
        ]
    },
    
    # =========================================================================
    # CATEGORY 2: PHARMACEUTICALS/DRUG OVERDOSES
    # =========================================================================
    "acetaminophen": {
        "name": "Acetaminophen/Paracetamol Overdose",
        "category": "pharmaceutical",
        "common_names": [
            "Paracetamol", "Tylenol", "Panadol", "Crocin", "Calpol",
            "APAP", "Acetaminophen", "Dolo", "Metacin"
        ],
        "common_sources": [
            "OTC painkillers", "Fever medications", "Combination cold medicines",
            "Prescription pain medications (Vicodin, Percocet)"
        ],
        "mechanism_of_action": "Saturation of normal metabolic pathways leads to toxic NAPQI metabolite, causing hepatic necrosis",
        "toxic_dose": {
            "single_acute": ">150mg/kg or >7.5g in adults (whichever is less)",
            "pediatric": ">200mg/kg",
            "chronic/repeated": "Lower thresholds apply",
            "high_risk": "Alcoholics, malnourished, enzyme-inducing medications"
        },
        "clinical_phases": {
            "phase_1": {
                "time": "0-24 hours",
                "symptoms": ["Nausea", "Vomiting", "Anorexia", "Malaise", "Diaphoresis", "Pallor"],
                "labs": "Usually normal"
            },
            "phase_2": {
                "time": "24-72 hours",
                "symptoms": ["RUQ pain", "Hepatomegaly", "Elevated LFTs begin"],
                "labs": "Rising AST, ALT, INR, bilirubin"
            },
            "phase_3": {
                "time": "72-96 hours",
                "symptoms": ["Fulminant hepatic failure", "Jaundice", "Coagulopathy", "Encephalopathy", "Renal failure"],
                "labs": "Peak LFTs (can exceed 10,000), high INR, metabolic acidosis"
            },
            "phase_4": {
                "time": "4-14 days",
                "outcome": "Recovery or death; complete hepatic regeneration if survives"
            }
        },
        "symptoms_immediate": [
            "Often asymptomatic initially",
            "Nausea", "Vomiting", "Anorexia", "Pallor", "Diaphoresis"
        ],
        "symptoms_delayed": [
            "Right upper quadrant pain",
            "Tender hepatomegaly",
            "Jaundice",
            "Hepatic encephalopathy",
            "Coagulopathy/bleeding",
            "Hypoglycemia",
            "Metabolic acidosis",
            "Acute kidney injury"
        ],
        "antidote": {
            "primary": "N-Acetylcysteine (NAC)",
            "mechanism": "Repletes glutathione stores, detoxifies NAPQI",
            "iv_protocol": {
                "loading": "150mg/kg IV over 60 minutes",
                "second_dose": "50mg/kg IV over 4 hours",
                "third_dose": "100mg/kg IV over 16 hours",
                "total": "300mg/kg over 21 hours"
            },
            "oral_protocol": {
                "loading": "140mg/kg PO",
                "maintenance": "70mg/kg every 4 hours x 17 doses",
                "total": "1330mg/kg over 72 hours"
            },
            "timing": "Most effective within 8 hours; still beneficial up to 24+ hours"
        },
        "rumack_matthew_nomogram": {
            "use": "Plot 4-hour post-ingestion level to determine treatment need",
            "treatment_line": "150mcg/mL at 4 hours, declining to 4.7mcg/mL at 24 hours",
            "note": "Use lower line (100mcg/mL at 4h) for high-risk patients"
        },
        "first_aid": [
            "Do not induce vomiting",
            "Activated charcoal 1g/kg if within 1-2 hours",
            "Note exact time and amount ingested",
            "Seek immediate medical care even if asymptomatic"
        ],
        "management_protocol": [
            "1. Assess time of ingestion and amount",
            "2. Activated charcoal if within 1-2 hours",
            "3. Check serum acetaminophen level at 4 hours post-ingestion",
            "4. Plot on Rumack-Matthew nomogram",
            "5. Start NAC if above treatment line or unknown ingestion",
            "6. Monitor LFTs, INR, creatinine, blood glucose q12-24h",
            "7. Consider liver transplant if King's College Criteria met",
            "8. Continue NAC until INR <2 and LFTs trending down"
        ],
        "kings_college_criteria": {
            "arterial_pH": "<7.3 after resuscitation (regardless of grade)",
            "OR_all_three": [
                "INR >6.5 (PT >100 seconds)",
                "Creatinine >3.4 mg/dL",
                "Grade III-IV hepatic encephalopathy"
            ],
            "indicates": "Need for liver transplant evaluation"
        },
        "contraindications": [
            "Do NOT delay NAC waiting for levels if large ingestion suspected",
            "Do NOT rely on early asymptomatic presentation"
        ],
        "tests_required": [
            "Serum acetaminophen level at 4 hours",
            "AST, ALT",
            "PT/INR",
            "Serum creatinine",
            "Blood glucose",
            "Serum lactate",
            "Arterial blood gas (severe cases)"
        ],
        "prognosis": {
            "with_NAC_within_8h": "Excellent - hepatotoxicity rare",
            "NAC_8_24h": "Good - reduces hepatotoxicity",
            "NAC_after_24h": "Still beneficial but higher risk",
            "without_treatment": "20-50% mortality in severe cases"
        },
        "data_sources": [
            {"name": "Rumack-Matthew Nomogram", "type": "medical_standard", "year": 1981},
            {"name": "UpToDate: Acetaminophen Poisoning", "type": "database", "year": 2024},
            {"name": "NPIC Nepal Guidelines", "type": "national", "year": 2023}
        ]
    },
    
    "opioid": {
        "name": "Opioid Overdose",
        "category": "pharmaceutical",
        "common_names": [
            "Morphine", "Heroin", "Fentanyl", "Oxycodone", "Hydrocodone",
            "Codeine", "Tramadol", "Methadone", "Meperidine", "Buprenorphine",
            "Carfentanil", "Brown sugar"
        ],
        "common_sources": [
            "Prescription painkillers", "Illicit drugs (heroin)",
            "Synthetic opioids (fentanyl)", "Cough medications"
        ],
        "mechanism_of_action": "Agonism at mu-opioid receptors causing CNS depression, respiratory depression",
        "opioid_toxidrome": [
            "Altered mental status (sedation to coma)",
            "Respiratory depression/apnea",
            "Miosis (pinpoint pupils)",
            "Bradycardia",
            "Hypotension",
            "Hypothermia",
            "Decreased bowel sounds"
        ],
        "symptoms_immediate": [
            "Drowsiness", "Euphoria", "Pinpoint pupils (miosis)",
            "Respiratory depression", "Hypotension", "Bradycardia",
            "Decreased consciousness"
        ],
        "symptoms_delayed": [
            "Respiratory arrest", "Aspiration pneumonia",
            "Anoxic brain injury", "Rhabdomyolysis",
            "Acute kidney injury", "Non-cardiogenic pulmonary edema"
        ],
        "antidote": {
            "primary": "Naloxone (Narcan)",
            "mechanism": "Competitive opioid receptor antagonist",
            "dose": {
                "iv_im_sc": "0.4-2mg initially, repeat every 2-3 minutes if no response",
                "intranasal": "4mg (one spray per nostril)",
                "pediatric": "0.1mg/kg",
                "max_dose": "If no response after 10mg, consider other diagnoses"
            },
            "duration": "30-90 minutes (much shorter than most opioids)",
            "repeat_dosing": "May need repeated doses or infusion for long-acting opioids"
        },
        "first_aid": [
            "Call for emergency help immediately",
            "Check for responsiveness",
            "Open airway, provide rescue breathing if not breathing",
            "Administer naloxone if available",
            "Place in recovery position",
            "Stay with person until help arrives"
        ],
        "management_protocol": [
            "1. ABCs - ventilatory support is primary treatment",
            "2. Naloxone IV/IM/IN - titrate to adequate respiration",
            "3. Avoid full reversal in opioid-dependent patients (precipitates withdrawal)",
            "4. Monitor for renarcotization (naloxone wears off)",
            "5. Consider naloxone infusion for long-acting opioids",
            "6. Supportive care: IV fluids, warming"
        ],
        "cautions": [
            "Rapid reversal in dependent patients causes acute withdrawal",
            "Renarcotization risk with long-acting opioids",
            "Fentanyl may require higher naloxone doses"
        ],
        "data_sources": [
            {"name": "CDC Opioid Overdose Guidelines", "type": "government", "year": 2024},
            {"name": "SAMHSA Opioid Overdose Toolkit", "type": "government", "year": 2023}
        ]
    },
    
    "benzodiazepine": {
        "name": "Benzodiazepine Overdose",
        "category": "pharmaceutical",
        "common_names": [
            "Diazepam", "Alprazolam", "Lorazepam", "Clonazepam",
            "Midazolam", "Temazepam", "Nitrazepam", "Flurazepam"
        ],
        "common_sources": [
            "Prescription sedatives", "Anti-anxiety medications",
            "Sleep aids", "Muscle relaxants"
        ],
        "mechanism_of_action": "Enhancement of GABA-A receptor activity causing CNS depression",
        "symptoms_immediate": [
            "Sedation", "Slurred speech", "Ataxia",
            "Confusion", "Respiratory depression (mild unless combined)"
        ],
        "antidote": {
            "primary": "Flumazenil",
            "dose": "0.2mg IV over 30 seconds, repeat 0.3mg then 0.5mg every minute",
            "max_dose": "3-5mg total",
            "cautions": [
                "Risk of seizures in chronic users",
                "Risk of seizures if co-ingestion with seizure-inducing agents",
                "Short duration - may need repeat dosing"
            ]
        },
        "management_protocol": [
            "1. Supportive care is usually sufficient",
            "2. Flumazenil only if pure BZD overdose confirmed",
            "3. Avoid flumazenil if chronic BZD use, seizure history, or co-ingestions",
            "4. Monitor respiratory status"
        ],
        "data_sources": [
            {"name": "Toxicology Handbook", "type": "textbook", "year": 2023}
        ]
    },

    "tricyclic_antidepressant": {
        "name": "Tricyclic Antidepressant Overdose",
        "category": "pharmaceutical",
        "common_names": [
            "Amitriptyline", "Imipramine", "Desipramine", "Nortriptyline",
            "Doxepin", "Clomipramine"
        ],
        "mechanism_of_action": "Sodium channel blockade, anticholinergic effects, alpha-adrenergic blockade, norepinephrine/serotonin reuptake inhibition",
        "toxic_dose": {
            "therapeutic": "2-4mg/kg",
            "toxic": ">10mg/kg",
            "potentially_fatal": ">20-30mg/kg"
        },
        "symptoms_immediate": [
            "Anticholinergic toxidrome (hot, dry, red, blind, mad)",
            "Tachycardia", "Mydriasis", "Dry mucous membranes",
            "Urinary retention", "Decreased bowel sounds"
        ],
        "symptoms_delayed": [
            "Seizures", "Hypotension", "Cardiac arrhythmias",
            "Wide QRS complex", "Prolonged QTc", "Coma",
            "Ventricular tachycardia/fibrillation"
        ],
        "ecg_findings": [
            "QRS widening (>100ms concerning, >160ms life-threatening)",
            "Right axis deviation (terminal R wave in aVR >3mm)",
            "QTc prolongation",
            "Brugada pattern"
        ],
        "antidote": {
            "primary": "Sodium bicarbonate",
            "dose": "1-2 mEq/kg IV bolus, then infusion",
            "goal": "Serum pH 7.45-7.55, QRS narrowing",
            "mechanism": "Overcomes sodium channel blockade, protein binding"
        },
        "management_protocol": [
            "1. Secure airway early - rapid deterioration possible",
            "2. IV access, continuous cardiac monitoring",
            "3. Sodium bicarbonate for QRS >100ms or ventricular arrhythmias",
            "4. Benzodiazepines for seizures",
            "5. Avoid class IA/IC antiarrhythmics, beta-blockers",
            "6. Lipid emulsion for refractory cardiovascular toxicity",
            "7. Consider ECMO for refractory cases"
        ],
        "contraindications": [
            "Class IA antiarrhythmics (procainamide, quinidine)",
            "Class IC antiarrhythmics (flecainide)",
            "Beta-blockers",
            "Physostigmine (seizure risk)"
        ],
        "data_sources": [
            {"name": "ACMT TCA Guidelines", "type": "medical_society", "year": 2023}
        ]
    },

    # =========================================================================
    # CATEGORY 3: HEAVY METALS
    # =========================================================================
    "lead": {
        "name": "Lead Poisoning",
        "category": "heavy_metal",
        "common_names": ["Plumbism", "Lead toxicity"],
        "common_sources": [
            "Old paint (pre-1978)", "Contaminated soil", "Lead pipes",
            "Batteries", "Pottery glazes", "Ayurvedic medicines",
            "Cosmetics (kajal/surma)", "Industrial exposure"
        ],
        "mechanism_of_action": "Binds to sulfhydryl groups, inhibits delta-aminolevulinic acid dehydratase, interferes with heme synthesis",
        "toxic_levels": {
            "cdc_reference": "<5 mcg/dL (no safe level)",
            "elevated": "5-44 mcg/dL",
            "moderate": "45-69 mcg/dL",
            "severe": "≥70 mcg/dL (encephalopathy risk)"
        },
        "symptoms_acute": [
            "Abdominal pain (lead colic)", "Vomiting", "Constipation",
            "Encephalopathy", "Seizures"
        ],
        "symptoms_chronic": [
            "Abdominal pain", "Constipation", "Fatigue", "Irritability",
            "Cognitive impairment", "Learning difficulties (children)",
            "Peripheral neuropathy (wrist drop)", "Gingival lead line",
            "Anemia", "Nephropathy"
        ],
        "pediatric_concerns": [
            "Developmental delay", "Learning disabilities",
            "Behavioral problems", "Lower IQ",
            "Hearing impairment"
        ],
        "antidote": {
            "chelation_agents": {
                "severe_with_encephalopathy": "BAL (dimercaprol) + CaNa2EDTA",
                "severe_without_encephalopathy": "CaNa2EDTA or Succimer (DMSA)",
                "moderate": "Succimer (DMSA) oral",
                "mild": "Source removal, nutritional support"
            },
            "bal_dose": "75mg/m² IM every 4 hours",
            "edta_dose": "1000-1500 mg/m²/day IV (start 4 hours after BAL)",
            "succimer_dose": "10mg/kg every 8 hours x 5 days, then every 12 hours x 14 days"
        },
        "management_protocol": [
            "1. Source identification and removal",
            "2. Nutritional support (iron, calcium, vitamin C)",
            "3. Chelation therapy based on blood lead level",
            "4. Repeat blood lead levels",
            "5. Environmental investigation"
        ],
        "tests_required": [
            "Blood lead level (venous, not capillary)",
            "CBC with peripheral smear (basophilic stippling)",
            "Erythrocyte protoporphyrin",
            "BUN, creatinine",
            "Abdominal X-ray (if recent ingestion)"
        ],
        "data_sources": [
            {"name": "CDC Lead Poisoning Guidelines", "type": "government", "year": 2024},
            {"name": "AAP Lead Exposure Statement", "type": "medical_society", "year": 2023}
        ]
    },
    
    "arsenic": {
        "name": "Arsenic Poisoning",
        "category": "heavy_metal",
        "common_names": ["Arsenicosis", "Arsenic toxicity"],
        "common_sources": [
            "Contaminated groundwater", "Pesticides", "Wood preservatives",
            "Herbicides", "Industrial processes", "Traditional medicines",
            "Contaminated rice/seafood"
        ],
        "mechanism_of_action": "Binds to sulfhydryl groups, inhibits pyruvate dehydrogenase, disrupts ATP production",
        "symptoms_acute": [
            "Severe gastroenteritis (rice-water diarrhea)",
            "Abdominal pain", "Vomiting", "Hypotension",
            "Garlic breath odor", "QT prolongation"
        ],
        "symptoms_chronic": [
            "Skin changes (hyperpigmentation, hyperkeratosis)",
            "Mees lines on nails", "Peripheral neuropathy",
            "Anemia", "Hepatomegaly",
            "Increased cancer risk (skin, lung, bladder)"
        ],
        "antidote": {
            "primary": "BAL (dimercaprol) for acute severe poisoning",
            "alternative": "Succimer (DMSA) for chronic/moderate cases",
            "bal_dose": "3-5 mg/kg IM every 4-6 hours",
            "succimer_dose": "10mg/kg every 8 hours"
        },
        "management_protocol": [
            "1. Remove from source",
            "2. Supportive care, IV fluids",
            "3. Chelation therapy",
            "4. Monitor for cardiac arrhythmias",
            "5. Long-term surveillance for malignancy"
        ],
        "tests_required": [
            "24-hour urine arsenic",
            "Blood arsenic level",
            "CBC",
            "Liver function tests",
            "ECG (QT interval)"
        ],
        "data_sources": [
            {"name": "WHO Arsenic Guidelines", "type": "international", "year": 2022},
            {"name": "ATSDR Toxicological Profile", "type": "government", "year": 2023}
        ]
    },

    "mercury": {
        "name": "Mercury Poisoning",
        "category": "heavy_metal",
        "common_names": ["Mercurialism", "Mercury toxicity"],
        "common_sources": [
            "Thermometers", "Dental amalgams", "Contaminated fish",
            "Industrial processes", "Artisanal gold mining",
            "Traditional medicines", "Batteries"
        ],
        "forms": {
            "elemental": "Liquid metal, inhalation toxicity",
            "inorganic": "Mercury salts, GI toxicity",
            "organic": "Methylmercury, neurotoxicity"
        },
        "symptoms_acute": [
            "Metal fume fever (elemental)", "Corrosive gastroenteritis (inorganic)",
            "Tremor", "Gingivostomatitis", "Pneumonitis"
        ],
        "symptoms_chronic": [
            "Erethism (irritability, memory loss, insomnia)",
            "Intention tremor", "Peripheral neuropathy",
            "Nephrotic syndrome", "Gingivitis",
            "Acrodynia (pink disease) in children"
        ],
        "antidote": {
            "elemental_inorganic": "DMSA (succimer) or BAL",
            "organic": "No proven chelation benefit",
            "succimer_dose": "10mg/kg every 8 hours",
            "bal_dose": "3-5mg/kg IM for severe cases"
        },
        "data_sources": [
            {"name": "ATSDR Mercury Toxicological Profile", "type": "government", "year": 2023}
        ]
    },

    # =========================================================================
    # CATEGORY 4: HOUSEHOLD/INDUSTRIAL CHEMICALS
    # =========================================================================
    "corrosive_acid": {
        "name": "Corrosive Acid Ingestion",
        "category": "household",
        "common_names": [
            "Sulfuric acid", "Hydrochloric acid", "Battery acid",
            "Toilet bowl cleaner", "Drain cleaner"
        ],
        "common_sources": [
            "Toilet cleaners", "Drain cleaners", "Battery acid",
            "Industrial chemicals", "Pool chemicals"
        ],
        "mechanism_of_action": "Coagulation necrosis, causing tissue damage",
        "symptoms_immediate": [
            "Severe oropharyngeal pain", "Drooling", "Dysphagia",
            "Stridor (if laryngeal edema)", "Vomiting",
            "Chest/abdominal pain"
        ],
        "symptoms_delayed": [
            "Esophageal/gastric perforation", "Mediastinitis",
            "Peritonitis", "Esophageal stricture",
            "Gastric outlet obstruction"
        ],
        "zargar_classification": {
            "grade_0": "Normal",
            "grade_1": "Edema, erythema",
            "grade_2a": "Superficial ulcers, friability",
            "grade_2b": "Deep or circumferential ulcers",
            "grade_3a": "Focal necrosis",
            "grade_3b": "Extensive necrosis"
        },
        "antidote": "NO SPECIFIC ANTIDOTE - Supportive care",
        "first_aid": [
            "DO NOT induce vomiting",
            "DO NOT attempt neutralization",
            "Small sips of water/milk controversial",
            "Immediate hospital transport",
            "Protect airway"
        ],
        "management_protocol": [
            "1. Secure airway early (may need emergency cricothyrotomy)",
            "2. NPO - nothing by mouth",
            "3. IV fluids, analgesia",
            "4. Endoscopy within 12-24 hours to grade injury",
            "5. Surgery consultation for perforation",
            "6. PPI therapy",
            "7. Stricture prevention (controversial)"
        ],
        "contraindications": [
            "Do NOT induce vomiting",
            "Do NOT attempt neutralization (heat generation)",
            "Do NOT place NG tube blindly",
            "Do NOT delay endoscopy"
        ],
        "data_sources": [
            {"name": "WGO Caustic Ingestion Guidelines", "type": "international", "year": 2022}
        ]
    },
    
    "corrosive_alkali": {
        "name": "Corrosive Alkali Ingestion",
        "category": "household",
        "common_names": [
            "Sodium hydroxide", "Potassium hydroxide", "Lye",
            "Caustic soda", "Drain cleaners", "Oven cleaners"
        ],
        "mechanism_of_action": "Liquefactive necrosis - deeper penetration than acids",
        "symptoms_immediate": [
            "Severe oropharyngeal burns", "Drooling", "Dysphagia",
            "May have less pain than injury suggests (nerve destruction)"
        ],
        "management_protocol": [
            "Same as acid ingestion",
            "NOTE: Alkalis cause deeper tissue damage",
            "Higher risk of esophageal perforation"
        ],
        "data_sources": [
            {"name": "WGO Guidelines", "type": "international", "year": 2022}
        ]
    },

    "methanol": {
        "name": "Methanol Poisoning",
        "category": "industrial",
        "common_names": [
            "Wood alcohol", "Methylated spirit", "Industrial alcohol",
            "Antifreeze", "Spurious liquor"
        ],
        "common_sources": [
            "Illicit alcohol", "Antifreeze", "Windshield washer fluid",
            "Industrial solvents", "Contaminated alcohol"
        ],
        "mechanism_of_action": "Metabolized to formaldehyde and formic acid, causing metabolic acidosis and retinal toxicity",
        "toxic_dose": {
            "lethal": "30-240mL (1-2mL/kg)",
            "toxic": "As little as 10mL can cause blindness"
        },
        "symptoms_immediate": [
            "Inebriation (similar to ethanol)", "Nausea", "Headache"
        ],
        "symptoms_delayed": [
            "Visual disturbances (blurred vision, scotoma)",
            "Complete blindness", "Severe metabolic acidosis",
            "Seizures", "Coma", "Death"
        ],
        "classic_triad": ["Visual impairment", "Metabolic acidosis", "Elevated osmolar gap"],
        "antidote": {
            "primary": "Fomepizole (4-methylpyrazole)",
            "alternative": "Ethanol",
            "fomepizole_dose": {
                "loading": "15mg/kg IV",
                "maintenance": "10mg/kg every 12 hours",
                "during_dialysis": "Increase to every 4 hours"
            },
            "ethanol_dose": {
                "loading": "0.8g/kg IV or PO",
                "maintenance": "80-130mg/kg/hr IV",
                "target_level": "100-150mg/dL"
            },
            "mechanism": "Inhibits alcohol dehydrogenase, prevents toxic metabolite formation"
        },
        "hemodialysis_indications": [
            "Metabolic acidosis (pH <7.25-7.30)",
            "Visual impairment",
            "Renal failure",
            "Serum methanol >50mg/dL",
            "Electrolyte abnormalities refractory to treatment"
        ],
        "management_protocol": [
            "1. Stabilize, check glucose and ABG",
            "2. Fomepizole or Ethanol to block ADH",
            "3. Folinic acid 1mg/kg IV q4-6h (enhances formate metabolism)",
            "4. Sodium bicarbonate for acidosis",
            "5. Hemodialysis for severe cases",
            "6. Ophthalmology consult"
        ],
        "data_sources": [
            {"name": "EXTRIP Workgroup Guidelines", "type": "international", "year": 2022},
            {"name": "Clinical Toxicology Journal", "type": "research", "year": 2023}
        ]
    },

    "ethylene_glycol": {
        "name": "Ethylene Glycol Poisoning",
        "category": "industrial",
        "common_names": ["Antifreeze", "Coolant", "Brake fluid"],
        "common_sources": [
            "Automotive antifreeze", "Brake fluid", "De-icing agents"
        ],
        "mechanism_of_action": "Metabolized to glycolic acid, glyoxylic acid, and oxalic acid causing metabolic acidosis and calcium oxalate crystals",
        "toxic_dose": "1-1.5mL/kg potentially lethal",
        "clinical_stages": {
            "stage_1": {
                "time": "0-12 hours",
                "symptoms": ["Inebriation", "Nausea", "Vomiting", "Ataxia"]
            },
            "stage_2": {
                "time": "12-24 hours",
                "symptoms": ["Cardiopulmonary failure", "Tachypnea", "Pulmonary edema", "Metabolic acidosis"]
            },
            "stage_3": {
                "time": "24-72 hours",
                "symptoms": ["Acute kidney injury", "Flank pain", "Oliguria/anuria"]
            }
        },
        "antidote": {
            "primary": "Fomepizole or Ethanol (same as methanol)",
            "mechanism": "Blocks alcohol dehydrogenase"
        },
        "classic_findings": [
            "High anion gap metabolic acidosis",
            "Elevated osmolar gap",
            "Calcium oxalate crystals in urine (envelope-shaped)"
        ],
        "management_protocol": [
            "1. Fomepizole or Ethanol",
            "2. Thiamine 100mg IV + Pyridoxine 50mg IV (enhance metabolism to non-toxic compounds)",
            "3. Sodium bicarbonate for acidosis",
            "4. Hemodialysis for severe cases",
            "5. Monitor renal function closely"
        ],
        "data_sources": [
            {"name": "EXTRIP Guidelines", "type": "international", "year": 2022}
        ]
    },

    "carbon_monoxide": {
        "name": "Carbon Monoxide Poisoning",
        "category": "gas",
        "common_names": ["CO poisoning", "Silent killer"],
        "common_sources": [
            "Car exhaust", "Faulty heaters", "Gas stoves",
            "Charcoal burning", "House fires", "Generators"
        ],
        "mechanism_of_action": "Binds hemoglobin with 240x affinity of oxygen, shifts oxyhemoglobin dissociation curve left, impairs cellular respiration",
        "symptoms_by_level": {
            "10-20%": ["Headache", "Nausea", "Dizziness"],
            "20-30%": ["Confusion", "Impaired judgment", "Syncope"],
            "30-40%": ["Tachycardia", "Tachypnea", "Chest pain"],
            "40-60%": ["Seizures", "Coma", "Cardiovascular collapse"],
            ">60%": ["Death"]
        },
        "symptoms_immediate": [
            "Headache", "Dizziness", "Nausea", "Confusion",
            "Cherry red skin (rare, late finding)", "Syncope"
        ],
        "symptoms_delayed": [
            "Delayed neuropsychiatric syndrome (DNS)",
            "Memory impairment", "Parkinsonism",
            "Personality changes", "Cognitive deficits"
        ],
        "antidote": {
            "primary": "100% Oxygen",
            "normobaric": "100% O2 via non-rebreather mask",
            "hyperbaric": "2.5-3 ATA for severe cases",
            "half_life": {
                "room_air": "4-5 hours",
                "100%_O2": "60-90 minutes",
                "hyperbaric": "20-30 minutes"
            }
        },
        "hyperbaric_indications": [
            "Loss of consciousness",
            "Neurological symptoms",
            "COHb >25% (or >15% in pregnancy)",
            "Cardiac ischemia",
            "Persistent symptoms despite normobaric O2"
        ],
        "management_protocol": [
            "1. Remove from exposure",
            "2. 100% oxygen via NRB mask immediately",
            "3. Check COHb level (but treat based on symptoms)",
            "4. Consider hyperbaric oxygen therapy",
            "5. Cardiac monitoring",
            "6. Treat concurrent cyanide poisoning in fire victims"
        ],
        "tests_required": [
            "Carboxyhemoglobin level (COHb)",
            "ABG (with co-oximetry)",
            "ECG",
            "Lactate",
            "Troponin"
        ],
        "data_sources": [
            {"name": "UHMS Hyperbaric Oxygen Guidelines", "type": "medical_society", "year": 2023},
            {"name": "Clinical Toxicology - CO Poisoning", "type": "research", "year": 2024}
        ]
    },

    "cyanide": {
        "name": "Cyanide Poisoning",
        "category": "industrial",
        "common_names": ["Hydrocyanic acid", "Prussic acid", "HCN"],
        "common_sources": [
            "House fires (burning plastics/synthetics)", "Industrial chemicals",
            "Fumigants", "Bitter almonds/apricot pits", "Cassava",
            "Sodium nitroprusside infusion"
        ],
        "mechanism_of_action": "Inhibits cytochrome c oxidase, blocks mitochondrial electron transport chain, causes cellular hypoxia",
        "symptoms_immediate": [
            "Headache", "Confusion", "Dyspnea", "Seizures",
            "Bitter almond odor (only 40-60% can detect)",
            "Cardiovascular collapse"
        ],
        "classic_findings": [
            "High lactate (>10 mmol/L in fire victims)",
            "Narrow arteriovenous O2 difference",
            "Bright red venous blood"
        ],
        "antidote": {
            "primary": "Hydroxocobalamin (Cyanokit)",
            "dose": "5g IV over 15 minutes (can repeat)",
            "alternative": "Cyanide Antidote Kit (amyl nitrite, sodium nitrite, sodium thiosulfate)",
            "nitrite_dose": "Sodium nitrite 300mg IV over 5 minutes",
            "thiosulfate_dose": "Sodium thiosulfate 12.5g IV"
        },
        "management_protocol": [
            "1. Remove from exposure, 100% oxygen",
            "2. Hydroxocobalamin IV immediately",
            "3. Supportive care for cardiovascular collapse",
            "4. Consider HBO if CO co-poisoning",
            "5. Sodium bicarbonate for acidosis"
        ],
        "data_sources": [
            {"name": "ACMT Cyanide Guidelines", "type": "medical_society", "year": 2023}
        ]
    },

    # =========================================================================
    # CATEGORY 5: NATURAL TOXINS
    # =========================================================================
    "snake_neurotoxic": {
        "name": "Neurotoxic Snake Envenomation",
        "category": "natural",
        "common_names": [
            "Cobra bite (Naja naja)", "Krait bite (Bungarus)",
            "Sea snake bite", "Elapid envenomation"
        ],
        "common_species_nepal": [
            "Common Cobra (Naja naja)", "Monocled Cobra (Naja kaouthia)",
            "Common Krait (Bungarus caeruleus)", "Banded Krait (Bungarus fasciatus)"
        ],
        "mechanism_of_action": "Alpha-neurotoxins block postsynaptic nicotinic receptors; Beta-bungarotoxin causes presynaptic neurotoxicity",
        "symptoms_immediate": [
            "Minimal local symptoms", "Fang marks",
            "Ptosis (first sign)", "Diplopia"
        ],
        "symptoms_delayed": [
            "Progressive descending paralysis", "Ptosis", "Ophthalmoplegia",
            "Dysphagia", "Dysarthria", "Respiratory paralysis",
            "Complete flaccid paralysis"
        ],
        "antidote": {
            "primary": "Polyvalent Anti-Snake Venom (ASV)",
            "dose": "10 vials (100mL) IV initially",
            "dilution": "Dilute in 200-400mL NS, infuse over 1 hour",
            "repeat": "May repeat based on clinical response",
            "adjunct": "Neostigmine trial for neurotoxic signs"
        },
        "neostigmine_trial": {
            "dose": "Atropine 0.6mg IV + Neostigmine 1.5-2mg IV",
            "timing": "Every 30 minutes",
            "response": "Improvement in ptosis and respiratory function suggests postsynaptic toxin"
        },
        "first_aid": [
            "Keep patient calm and immobile",
            "Immobilize bitten limb at heart level",
            "Remove jewelry/tight clothing",
            "DO NOT cut wound, suck venom, apply tourniquet",
            "Transport immediately to hospital"
        ],
        "management_protocol": [
            "1. Assess for envenomation (20WBCT, clinical signs)",
            "2. Premedicate: Adrenaline 0.25-0.5mg IM + Antihistamine",
            "3. ASV if systemic envenomation signs",
            "4. Neostigmine trial for neurotoxic signs",
            "5. Ventilatory support for respiratory failure",
            "6. Wound care, tetanus prophylaxis"
        ],
        "asv_indications": [
            "Ptosis or other neurotoxic signs",
            "Non-clotting blood (20WBCT)",
            "Active bleeding",
            "Cardiovascular abnormalities",
            "AKI"
        ],
        "data_sources": [
            {"name": "WHO Guidelines for Snake Bite Management - Southeast Asia", "type": "international", "year": 2023},
            {"name": "BPKIHS Snake Bite Protocol", "type": "national", "year": 2023},
            {"name": "Nepal Ministry of Health Snake Bite Guidelines", "type": "government", "year": 2022}
        ]
    },
    
    "snake_hemotoxic": {
        "name": "Hemotoxic Snake Envenomation",
        "category": "natural",
        "common_names": [
            "Viper bite", "Russell's Viper", "Pit viper",
            "Green pit viper"
        ],
        "common_species_nepal": [
            "Russell's Viper (Daboia russelii)",
            "Saw-scaled Viper (Echis carinatus)",
            "Himalayan Pit Viper", "Green Pit Viper"
        ],
        "mechanism_of_action": "Venom contains procoagulants causing consumption coagulopathy, hemorrhagins causing bleeding",
        "symptoms_immediate": [
            "Severe local pain", "Rapid swelling", "Ecchymosis",
            "Fang marks", "Local necrosis"
        ],
        "symptoms_delayed": [
            "Coagulopathy (non-clotting blood)", "Bleeding from gums, injection sites",
            "Hematemesis", "Hematuria", "Intracranial hemorrhage",
            "DIC", "Acute kidney injury", "Compartment syndrome"
        ],
        "20wbct": {
            "procedure": "Place 2mL venous blood in clean glass tube, leave for 20 minutes",
            "interpretation": "If blood does not clot = coagulopathy present",
            "significance": "Simple bedside test for coagulopathy"
        },
        "antidote": {
            "primary": "Polyvalent ASV",
            "dose": "10 vials initially, may need more for vipers",
            "repeat": "If blood still non-clotting after 6 hours"
        },
        "management_protocol": [
            "1. 20WBCT on admission and serially",
            "2. ASV for non-clotting blood or systemic bleeding",
            "3. Blood products for active bleeding",
            "4. Dialysis for AKI",
            "5. Fasciotomy for compartment syndrome",
            "6. Avoid IM injections, surgery until coagulopathy corrected"
        ],
        "data_sources": [
            {"name": "WHO Regional Guidelines", "type": "international", "year": 2023}
        ]
    },

    "scorpion": {
        "name": "Scorpion Envenomation",
        "category": "natural",
        "common_names": ["Scorpion sting", "Scorpion bite"],
        "mechanism_of_action": "Neurotoxins cause sodium channel dysfunction leading to autonomic storm",
        "symptoms_immediate": [
            "Severe local pain", "Paresthesias", "Numbness"
        ],
        "symptoms_delayed": [
            "Autonomic storm", "Hypertension", "Tachycardia",
            "Pulmonary edema", "Myocardial dysfunction",
            "Muscle fasciculations", "Hypersalivation"
        ],
        "antidote": {
            "primary": "Scorpion antivenom (where available)",
            "alternative": "Prazosin for autonomic storm"
        },
        "management_protocol": [
            "1. Pain control",
            "2. Prazosin 0.5mg PO for autonomic effects",
            "3. Antivenom if available and severe",
            "4. Supportive care for cardiopulmonary complications"
        ],
        "data_sources": [
            {"name": "Clinical Toxicology Journal", "type": "research", "year": 2023}
        ]
    },

    "mushroom_amatoxin": {
        "name": "Amatoxin Mushroom Poisoning",
        "category": "natural",
        "common_names": [
            "Death Cap", "Destroying Angel", "Amanita phalloides",
            "Amanita virosa", "Wild mushroom poisoning"
        ],
        "mechanism_of_action": "Amatoxins inhibit RNA polymerase II, causing hepatocyte death and hepatic failure",
        "toxic_dose": "Single mushroom cap can be lethal (0.1mg/kg amatoxin)",
        "clinical_phases": {
            "lag_phase": {
                "time": "6-12 hours (up to 24 hours)",
                "symptoms": ["Asymptomatic - DELAYED ONSET IS KEY FEATURE"]
            },
            "gi_phase": {
                "time": "6-24 hours",
                "symptoms": ["Profuse watery diarrhea", "Severe vomiting", "Abdominal cramps", "Dehydration"]
            },
            "apparent_recovery": {
                "time": "24-48 hours",
                "symptoms": ["Symptoms improve - FALSE REASSURANCE"]
            },
            "hepatic_phase": {
                "time": "2-4 days",
                "symptoms": ["Hepatic failure", "Jaundice", "Coagulopathy", "Hypoglycemia", "Encephalopathy", "Renal failure"]
            }
        },
        "symptoms_immediate": [
            "Delayed onset (6-12 hours) - key distinguishing feature",
            "Then severe GI symptoms"
        ],
        "symptoms_delayed": [
            "Fulminant hepatic failure", "Coagulopathy",
            "Hepatic encephalopathy", "Multi-organ failure"
        ],
        "antidote": {
            "primary": "Silibinin/Silymarin (Milk Thistle)",
            "dose": "20-50mg/kg/day IV in 4 divided doses",
            "alternatives": ["N-Acetylcysteine", "High-dose Penicillin G (controversial)"],
            "nac_dose": "150mg/kg IV protocol (same as acetaminophen)"
        },
        "management_protocol": [
            "1. Aggressive fluid resuscitation",
            "2. Multiple-dose activated charcoal (interrupts enterohepatic circulation)",
            "3. Silibinin IV if available",
            "4. N-Acetylcysteine IV",
            "5. Penicillin G 300,000-1,000,000 U/kg/day (controversial)",
            "6. Correct coagulopathy",
            "7. EARLY liver transplant evaluation",
            "8. MARS/liver support if available"
        ],
        "liver_transplant_criteria": [
            "Prothrombin time <10% of normal",
            "Serum creatinine >1.2mg/dL within 3-10 days",
            "Encephalopathy grade III-IV",
            "Factor V <20% in patients <30 years"
        ],
        "data_sources": [
            {"name": "AACT Mushroom Poisoning Guidelines", "type": "medical_society", "year": 2023},
            {"name": "Hepatology Journal - Amatoxin", "type": "research", "year": 2022}
        ]
    },

    "oleander": {
        "name": "Oleander Poisoning",
        "category": "natural",
        "common_names": [
            "Nerium oleander", "Kaner", "Yellow oleander",
            "Thevetia peruviana", "Be-still tree"
        ],
        "mechanism_of_action": "Cardiac glycosides (oleandrin) inhibit Na-K-ATPase pump similar to digoxin",
        "symptoms_immediate": [
            "Nausea", "Vomiting", "Abdominal pain",
            "Hypersalivation"
        ],
        "symptoms_delayed": [
            "Bradycardia", "Heart block", "Ventricular arrhythmias",
            "Hyperkalemia", "Visual disturbances (yellow halos)",
            "Altered mental status"
        ],
        "ecg_findings": [
            "Bradycardia", "AV block (any degree)", "ST depression (scooped)",
            "Bidirectional VT", "Ventricular fibrillation"
        ],
        "antidote": {
            "primary": "Digoxin-specific Fab fragments (DigiFab/Digibind)",
            "dose": "Empirically 10-20 vials for unknown ingestion",
            "alternatives": ["Atropine for bradycardia", "Temporary pacing"]
        },
        "management_protocol": [
            "1. Continuous cardiac monitoring",
            "2. Multiple-dose activated charcoal",
            "3. Correct hyperkalemia (avoid calcium - arrhythmia risk)",
            "4. DigiFab for significant arrhythmias or hyperkalemia",
            "5. Atropine for symptomatic bradycardia",
            "6. Temporary pacing if needed"
        ],
        "contraindications": [
            "AVOID calcium chloride/gluconate for hyperkalemia",
            "May worsen cardiac toxicity"
        ],
        "data_sources": [
            {"name": "Indian Journal of Critical Care - Oleander", "type": "research", "year": 2023}
        ]
    },

    # =========================================================================
    # CATEGORY 6: SUBSTANCES OF ABUSE
    # =========================================================================
    "alcohol_ethanol": {
        "name": "Acute Alcohol (Ethanol) Intoxication",
        "category": "substance_abuse",
        "common_names": ["Alcohol poisoning", "Acute intoxication", "Drunk"],
        "common_sources": [
            "Beer", "Wine", "Spirits", "Hand sanitizers", "Mouthwash"
        ],
        "mechanism_of_action": "GABA-A agonism, NMDA antagonism causing CNS depression",
        "blood_alcohol_levels": {
            "legal_limit": "0.08% (80mg/dL)",
            "impairment": "0.05-0.10% (50-100mg/dL)",
            "severe_intoxication": "0.3-0.4% (300-400mg/dL)",
            "potentially_lethal": ">0.4% (>400mg/dL)"
        },
        "symptoms_immediate": [
            "Euphoria", "Disinhibition", "Slurred speech",
            "Ataxia", "Nystagmus", "Confusion"
        ],
        "symptoms_severe": [
            "Respiratory depression", "Aspiration", "Coma",
            "Hypoglycemia", "Hypothermia", "Death"
        ],
        "antidote": "NO SPECIFIC ANTIDOTE - Supportive care",
        "management_protocol": [
            "1. Protect airway (recovery position or intubation)",
            "2. Check blood glucose - treat hypoglycemia",
            "3. Thiamine 100mg IV BEFORE glucose",
            "4. IV fluids for dehydration",
            "5. Warming for hypothermia",
            "6. Monitor for withdrawal in chronic users"
        ],
        "cautions": [
            "Always give Thiamine before glucose (prevent Wernicke)",
            "Aspiration pneumonia risk",
            "Co-ingestion common"
        ],
        "data_sources": [
            {"name": "ACEP Clinical Policy - Alcohol", "type": "medical_society", "year": 2023}
        ]
    },

    # =========================================================================
    # CATEGORY 7: ANTICOAGULANT RODENTICIDES
    # =========================================================================
    "warfarin_rodenticide": {
        "name": "Anticoagulant Rodenticide Poisoning",
        "category": "household",
        "common_names": [
            "Warfarin", "Brodifacoum", "Bromadiolone", "Difethialone",
            "Superwarfarins", "Rat poison", "Mouse poison"
        ],
        "mechanism_of_action": "Inhibits vitamin K epoxide reductase, depleting clotting factors II, VII, IX, X",
        "superwarfarin_note": "Second-generation compounds have very long half-lives (weeks to months)",
        "symptoms_immediate": [
            "Usually none for first 24-48 hours"
        ],
        "symptoms_delayed": [
            "Bleeding gums", "Epistaxis", "Easy bruising",
            "Hematuria", "Melena", "Hemoptysis",
            "Intracranial hemorrhage"
        ],
        "antidote": {
            "primary": "Vitamin K1 (Phytonadione)",
            "dose": {
                "oral": "10-25mg PO every 6-12 hours",
                "iv": "10mg IV for severe bleeding (slow infusion)",
                "duration": "May need for weeks to months for superwarfarins"
            },
            "for_active_bleeding": ["Fresh Frozen Plasma (FFP)", "Prothrombin Complex Concentrate (PCC)", "Factor VIIa"]
        },
        "management_protocol": [
            "1. Check INR at 24, 48, 72 hours",
            "2. Vitamin K1 if INR elevated or prophylactically if large ingestion",
            "3. FFP or PCC for active bleeding",
            "4. Continue Vitamin K1 - may need months",
            "5. Monitor INR weekly during treatment"
        ],
        "contraindications": [
            "Avoid aspirin, NSAIDs",
            "Avoid IM injections",
            "Avoid trauma"
        ],
        "data_sources": [
            {"name": "Clinical Toxicology - Superwarfarin", "type": "research", "year": 2023}
        ]
    },

    # =========================================================================
    # CATEGORY 8: HYDROCARBONS
    # =========================================================================
    "hydrocarbon": {
        "name": "Hydrocarbon Poisoning",
        "category": "household",
        "common_names": [
            "Kerosene", "Petrol/Gasoline", "Diesel", "Turpentine",
            "Lighter fluid", "Lamp oil", "Furniture polish"
        ],
        "common_sources": [
            "Fuels", "Solvents", "Cleaning products", "Lighter fluid"
        ],
        "mechanism_of_action": "Aspiration causes chemical pneumonitis; CNS depression; cardiac sensitization to catecholamines",
        "aspiration_risk": "High volatility, low viscosity compounds (gasoline, lighter fluid) - HIGH RISK",
        "symptoms_immediate": [
            "Coughing", "Choking", "Burning sensation",
            "Nausea", "Vomiting"
        ],
        "symptoms_delayed": [
            "Chemical pneumonitis", "Hypoxia", "Respiratory distress",
            "CNS depression", "Cardiac arrhythmias"
        ],
        "antidote": "NO SPECIFIC ANTIDOTE - Supportive care",
        "first_aid": [
            "DO NOT induce vomiting (aspiration risk)",
            "Remove from fumes",
            "Remove contaminated clothing",
            "Wash skin with soap and water",
            "Seek medical attention if symptomatic"
        ],
        "management_protocol": [
            "1. Do NOT perform gastric lavage",
            "2. Do NOT give activated charcoal (not adsorbed)",
            "3. Observe for respiratory symptoms 4-6 hours",
            "4. Chest X-ray at 4-6 hours if symptomatic",
            "5. Oxygen for hypoxia",
            "6. Bronchodilators for bronchospasm",
            "7. No prophylactic antibiotics or steroids"
        ],
        "contraindications": [
            "DO NOT induce vomiting",
            "DO NOT perform gastric lavage",
            "DO NOT give activated charcoal"
        ],
        "data_sources": [
            {"name": "Pediatric Toxicology Handbook", "type": "textbook", "year": 2023}
        ]
    }
}

# =============================================================================
# SYMPTOM-TO-POISON MAPPING FOR ML TRAINING
# =============================================================================

SYMPTOM_POISON_MAPPING = {
    # Organophosphate/Carbamate symptoms
    "salivation": ["organophosphate", "carbamate", "mushroom_amatoxin"],
    "excessive salivation": ["organophosphate", "carbamate"],
    "lacrimation": ["organophosphate", "carbamate"],
    "tearing": ["organophosphate", "carbamate"],
    "urination": ["organophosphate", "carbamate"],
    "defecation": ["organophosphate", "carbamate"],
    "diarrhea": ["organophosphate", "carbamate", "arsenic", "mushroom_amatoxin", "corrosive_acid"],
    "miosis": ["organophosphate", "carbamate", "opioid"],
    "pinpoint pupils": ["organophosphate", "carbamate", "opioid"],
    "bradycardia": ["organophosphate", "carbamate", "oleander", "digoxin"],
    "muscle fasciculations": ["organophosphate", "carbamate", "scorpion"],
    "sweating": ["organophosphate", "carbamate", "hypoglycemia"],
    "bronchospasm": ["organophosphate", "carbamate"],
    "wheezing": ["organophosphate", "carbamate", "anaphylaxis"],
    
    # Opioid symptoms
    "drowsiness": ["opioid", "benzodiazepine", "alcohol_ethanol"],
    "respiratory depression": ["opioid", "benzodiazepine", "alcohol_ethanol"],
    "pinpoint pupils": ["opioid"],
    "constipation": ["opioid", "lead"],
    
    # Anticholinergic symptoms
    "mydriasis": ["tricyclic_antidepressant", "antihistamine", "atropine"],
    "dilated pupils": ["tricyclic_antidepressant", "cocaine", "amphetamine"],
    "dry mouth": ["tricyclic_antidepressant", "antihistamine"],
    "urinary retention": ["tricyclic_antidepressant", "antihistamine"],
    "tachycardia": ["tricyclic_antidepressant", "cocaine", "amphetamine", "theophylline"],
    "hyperthermia": ["tricyclic_antidepressant", "cocaine", "amphetamine", "serotonin_syndrome"],
    "flushed skin": ["tricyclic_antidepressant", "antihistamine"],
    
    # Heavy metal symptoms
    "abdominal pain": ["lead", "arsenic", "iron", "acetaminophen", "corrosive_acid", "mushroom_amatoxin"],
    "lead line": ["lead"],
    "wrist drop": ["lead"],
    "peripheral neuropathy": ["lead", "arsenic", "mercury"],
    "memory loss": ["lead", "mercury", "carbon_monoxide"],
    "rice water diarrhea": ["arsenic"],
    "mees lines": ["arsenic"],
    "tremor": ["mercury", "lithium", "alcohol_withdrawal"],
    "erethism": ["mercury"],
    
    # Hepatotoxicity symptoms
    "jaundice": ["acetaminophen", "mushroom_amatoxin", "carbon_tetrachloride"],
    "right upper quadrant pain": ["acetaminophen", "mushroom_amatoxin"],
    "hepatomegaly": ["acetaminophen", "mushroom_amatoxin", "arsenic"],
    "coagulopathy": ["acetaminophen", "mushroom_amatoxin", "warfarin_rodenticide"],
    "encephalopathy": ["acetaminophen", "mushroom_amatoxin", "alcohol_ethanol"],
    
    # Cardiac symptoms
    "qrs widening": ["tricyclic_antidepressant", "sodium_channel_blockers"],
    "qt prolongation": ["organophosphate", "tricyclic_antidepressant", "arsenic"],
    "heart block": ["oleander", "digoxin", "beta_blockers", "calcium_channel_blockers"],
    "ventricular arrhythmia": ["tricyclic_antidepressant", "oleander", "cocaine"],
    
    # Snake envenomation symptoms
    "ptosis": ["snake_neurotoxic", "botulism"],
    "diplopia": ["snake_neurotoxic", "botulism", "methanol"],
    "dysphagia": ["snake_neurotoxic", "botulism", "corrosive_acid"],
    "respiratory paralysis": ["snake_neurotoxic", "botulism"],
    "local swelling": ["snake_hemotoxic", "scorpion", "bee_sting"],
    "non clotting blood": ["snake_hemotoxic"],
    "bleeding gums": ["snake_hemotoxic", "warfarin_rodenticide"],
    
    # Methanol/toxic alcohol symptoms
    "visual disturbances": ["methanol", "quinine"],
    "blindness": ["methanol"],
    "metabolic acidosis": ["methanol", "ethylene_glycol", "aspirin", "cyanide"],
    "high anion gap": ["methanol", "ethylene_glycol", "aspirin", "cyanide", "iron"],
    "osmolar gap": ["methanol", "ethylene_glycol", "alcohol_ethanol"],
    
    # Carbon monoxide symptoms
    "headache": ["carbon_monoxide", "organophosphate", "lead"],
    "cherry red skin": ["carbon_monoxide", "cyanide"],
    "confusion": ["carbon_monoxide", "organophosphate", "opioid", "hypoglycemia"],
    
    # Corrosive symptoms
    "oral burns": ["corrosive_acid", "corrosive_alkali"],
    "drooling": ["corrosive_acid", "corrosive_alkali", "organophosphate"],
    "stridor": ["corrosive_acid", "corrosive_alkali", "anaphylaxis"],
    
    # General symptoms
    "nausea": ["acetaminophen", "iron", "arsenic", "mushroom_amatoxin", "carbon_monoxide"],
    "vomiting": ["acetaminophen", "iron", "arsenic", "mushroom_amatoxin", "organophosphate"],
    "seizures": ["organophosphate", "tricyclic_antidepressant", "isoniazid", "theophylline"],
    "coma": ["opioid", "benzodiazepine", "carbon_monoxide", "methanol"]
}

# =============================================================================
# EMERGENCY NUMBERS BY REGION
# =============================================================================

EMERGENCY_NUMBERS = {
    "nepal": {
        "emergency": "102",
        "poison_control": "+977-1-4412505",
        "toll_free": "1102",
        "ambulance": "102",
        "centers": [
            {"name": "NPIC - TUTH", "phone": "+977-1-4412505", "city": "Kathmandu"},
            {"name": "Bir Hospital", "phone": "+977-1-4221119", "city": "Kathmandu"},
            {"name": "BPKIHS", "phone": "+977-25-525555", "city": "Dharan"}
        ]
    },
    "india": {
        "emergency": "112",
        "poison_control": "+91-44-28190099",
        "centers": [
            {"name": "AIIMS Poison Control", "phone": "+91-11-26589391", "city": "New Delhi"},
            {"name": "NIMHANS", "phone": "+91-80-26995000", "city": "Bangalore"}
        ]
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_poison_by_symptoms(symptoms: List[str]) -> List[Dict]:
    """Match symptoms to possible poisons"""
    matches = {}
    symptoms_lower = [s.lower().strip() for s in symptoms]
    
    for symptom in symptoms_lower:
        for mapped_symptom, poisons in SYMPTOM_POISON_MAPPING.items():
            if symptom in mapped_symptom or mapped_symptom in symptom:
                for poison in poisons:
                    if poison in matches:
                        matches[poison]["score"] += 1
                        matches[poison]["matched_symptoms"].append(mapped_symptom)
                    else:
                        matches[poison] = {
                            "score": 1,
                            "matched_symptoms": [mapped_symptom],
                            "data": COMPREHENSIVE_POISONS.get(poison, {})
                        }
    
    # Sort by score
    sorted_matches = sorted(matches.items(), key=lambda x: x[1]["score"], reverse=True)
    return [{"poison_id": k, **v} for k, v in sorted_matches]


def get_poison_details(poison_id: str) -> Dict:
    """Get comprehensive details for a poison"""
    return COMPREHENSIVE_POISONS.get(poison_id, {})


def get_antidote_info(poison_id: str) -> Dict:
    """Get antidote information for a poison"""
    poison = COMPREHENSIVE_POISONS.get(poison_id, {})
    return poison.get("antidote", {})


def get_first_aid(poison_id: str) -> List[str]:
    """Get first aid instructions for a poison"""
    poison = COMPREHENSIVE_POISONS.get(poison_id, {})
    return poison.get("first_aid", [])


def get_management_protocol(poison_id: str) -> List[str]:
    """Get management protocol for a poison"""
    poison = COMPREHENSIVE_POISONS.get(poison_id, {})
    return poison.get("management_protocol", [])
