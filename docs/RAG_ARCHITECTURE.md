# PoisonSense AI - RAG Architecture Documentation

## Overview

The PoisonSense AI uses a **Retrieval-Augmented Generation (RAG)** architecture with two knowledge streams:

1. **Poison Knowledge RAG** - Poison information, symptoms, antidotes, safety guidelines
2. **Nepal Facilities RAG** - Hospitals, labs, poison centers with geolocation

## Architecture Diagram

```
                 ┌──────────────────────────────┐
                 │            USER              │
                 │  "My child drank bleach…"    │
                 └──────────────┬───────────────┘
                                │
                                v
                 ┌──────────────────────────────┐
                 │   INPUT & SAFETY TRIAGE      │
                 │ - extract poison/exposure    │
                 │ - detect emergency symptoms  │
                 │ - ask for location if needed │
                 └──────────────┬───────────────┘
                                │
             ┌──────────────────┴──────────────────┐
             │                                     │
             v                                     v
┌──────────────────────────────┐     ┌──────────────────────────────┐
│  RETRIEVER: Poison Knowledge  │     │ RETRIEVER: Nepal Facilities  │
│  - poison facts & symptoms    │     │ - hospitals & labs directory │
│  - antidote availability      │     │ - geolocation + services     │
│  - do/don't safety guidance   │     │ - emergency capability       │
└──────────────┬───────────────┘     └──────────────┬───────────────┘
               │                                      │
               └──────────────┬───────────────────────┘
                              v
                 ┌──────────────────────────────┐
                 │   CONTEXT BUILDER / RANKER   │
                 │ - pick most relevant chunks  │
                 │ - merge + de-duplicate       │
                 │ - prioritize verified sources│
                 └──────────────┬───────────────┘
                                │
                                v
                 ┌──────────────────────────────┐
                 │  LLM WITH STRICT SYSTEM PROMPT│
                 │ - answer ONLY from context    │
                 │ - no dosage / no procedures   │
                 │ - emergency-first messaging   │
                 └──────────────┬───────────────┘
                                │
                                v
                 ┌──────────────────────────────┐
                 │         FINAL RESPONSE        │
                 │ 1) Poison summary             │
                 │ 2) symptoms (info only)       │
                 │ 3) antidote exists? (no steps)│
                 │ 4) nearest hospital/lab list  │
                 │ 5) safety disclaimer          │
                 └──────────────────────────────┘
```

## Data Sources

### 1. Poison Knowledge (`/backend/app/ml/data/poison_knowledge.py`)

Structured poison entries with fields:
- `poison_id` - Unique identifier
- `poison_name` - Official name
- `aliases` - Local/common names
- `category` - pesticide, household, medicine, plant, animal, gas, etc.
- `routes` - ingestion, inhalation, skin, eye, bite
- `risk_level` - Low, Moderate, High, Life-threatening
- `typical_symptoms_early` - Early warning signs
- `danger_signs_emergency` - Critical symptoms requiring immediate action
- `antidote_exists` - Yes/No/Conditional
- `antidote_names` - Names only (no dosing)
- `clinical_notes` - High-level medical info
- `do_not_do` - Safety warnings
- `source_refs` - Citation sources

**Current Entries:** 15+ poisons including organophosphate, carbamate, paraquat, corrosive acid/alkali, hydrocarbon, acetaminophen, opioid, benzodiazepine, snake bites, oleander, mushroom, methanol, ethylene glycol, rodenticides

### 2. Nepal Facilities (`/backend/app/ml/data/nepal_facilities.py`)

Facility directory with fields:
- `facility_id` - Unique identifier
- `facility_name` - Official name
- `facility_type` - Hospital, Lab, Poison Center, Clinic
- `province`, `district`, `municipality`, `ward`
- `address_line`, `latitude`, `longitude`
- `has_emergency`, `open_24_7`, `has_icu`, `has_pediatrics`, `has_toxicology`
- `poison_case_ready_score` - 0-100 rating
- `services` - ER, ICU, Toxicology, Dialysis, etc.
- `lab_tests_available` - CBC, RFT, LFT, Cholinesterase, etc.
- `antidote_stock_notes` - What antidotes are typically available
- `phone_primary`, `phone_secondary`, `website`
- `ambulance_available`
- `source`, `last_verified_date`, `notes`

**Current Entries:**
- 12 Hospitals across Nepal (TUTH, Bir, Patan, Grande, Mediciti, Norvic, BPKIHS, Manipal, etc.)
- 1 National Poison Control Center (NPIC-TUTH)
- 1 Reference Laboratory (National Public Health Lab)

### 3. Comprehensive Toxicology Data (`/backend/app/ml/data/comprehensive_toxicology_data.py`)

Detailed medical information from verified sources:
- WHO Guidelines
- CDC Recommendations
- NPIC Protocols
- Clinical Toxicology Literature

## RAG Retriever Functions

### Poison Knowledge Retrievers

```python
# Find poison by name or alias
retrieve_poison_by_name(query: str) -> Optional[dict]

# Find possible poisons based on symptoms
retrieve_poison_by_symptoms(symptoms: List[str], limit: int = 3) -> List[dict]

# Find poisons by category
retrieve_poison_by_category(category: str, limit: int = 10) -> List[dict]

# Get safety do's and don'ts
get_poison_safety_info(poison_id: str) -> Optional[dict]

# Get antidote information (names only)
get_antidote_info(poison_id: str) -> Optional[dict]

# Get emergency danger signs
get_emergency_signs(poison_id: str) -> Optional[dict]
```

### Nepal Facilities Retrievers

```python
# Find nearest suitable facilities using location + capability scoring
retrieve_nearest_facilities(
    latitude: float,
    longitude: float,
    facility_type: Optional[FacilityType] = None,
    max_distance_km: float = 100,
    min_poison_score: int = 50,
    require_emergency: bool = True,
    require_24_7: bool = False,
    limit: int = 5
) -> List[Dict]

# Find facilities with specific antidote
retrieve_facilities_by_antidote(antidote_name: str, limit: int = 5) -> List[Dict]

# Find facilities offering specific service
retrieve_facilities_by_service(service: str, limit: int = 10) -> List[Dict]

# Get national poison control hotline
get_poison_control_hotline() -> Dict

# Get facility details
get_facility_details(facility_id: str) -> Optional[Dict]
```

## Agent Tools

The PoisonSenseAgent uses these RAG-powered tools:

| Tool | Description |
|------|-------------|
| `analyze_symptoms` | ML + RAG symptom analysis |
| `get_poison_info` | RAG poison knowledge retrieval |
| `get_first_aid` | First aid instructions |
| `get_antidote` | Antidote information |
| `find_nearby_hospitals` | RAG facilities search by location |
| `find_poison_centers` | RAG poison center search |
| `assess_severity` | Risk assessment |
| `search_poison_database` | Full-text poison search |
| `rag_retrieve_by_symptoms` | RAG symptom-based retrieval |
| `rag_find_facilities` | RAG facility search |

## Ranking Algorithm (Facilities)

When finding the "nearest + best suited" facility:

1. **Distance Filter** - Only facilities within max_distance_km
2. **Capability Filter** - has_emergency, open_24_7, min_poison_score
3. **Suitability Score Calculation:**
   - Base: `poison_case_ready_score` (0-100)
   - Proximity bonus: `max(0, 20 - distance/5)` (max 20 points)
   - Emergency bonus: +10 if has_emergency
   - Availability bonus: +5 if open_24_7
   - Toxicology bonus: +15 if has_toxicology

4. **Sort by:** suitability_score (descending), then distance (ascending)

## Safety Guidelines

The system follows a **comprehensive safety framework** with strict rules:

### What The System Covers (In Scope)
- ✅ Poison information (pesticides, household chemicals, medications, plants, bites, gases)
- ✅ Symptom recognition (early symptoms, danger signs)
- ✅ Antidote names (informational only - NO dosage)
- ✅ General safety guidance (do's and don'ts)
- ✅ Nearest facilities (hospitals, labs, poison centers)
- ✅ Emergency contact numbers

### What The System Does NOT Cover (Out of Scope)
- ❌ Specific dosage or dose amounts
- ❌ How to administer antidotes
- ❌ Treatment protocols or procedures
- ❌ Medical diagnosis
- ❌ Home treatment instructions
- ❌ IV/injection guidance

### Guardrail Implementation

When a user asks for prohibited information (dosage, administration, diagnosis):
1. The system detects prohibited patterns in the query
2. Politely refuses the request with explanation
3. Redirects to professional help (Poison Control, hospital)
4. Offers alternative assistance (general info, find hospital)

**Prohibited Pattern Examples:**
- "how much", "dosage", "dose"
- "how to give", "how to administer"
- "inject", "injection", "IV dose"
- "mg/kg", "milligrams"
- "treatment protocol"
- "home remedy", "home treatment"

## Emergency Override Rules

### Trigger Conditions
The emergency override activates when detecting:

1. **Severe Symptoms:**
   - Unconscious / unresponsive
   - Seizures / convulsions
   - Not breathing / difficulty breathing
   - Cardiac arrest / no pulse
   - Cyanosis (blue lips)
   - Collapse
   - Choking / gasping
   - Foaming at mouth

2. **Child Exposure:**
   - Any mention of child/baby/infant/toddler + poison context
   - Keywords: "my son", "my daughter", "2 year old", etc.

### Emergency Response Behavior
When triggered:
1. **Skip normal conversation flow**
2. **Display emergency banner first**
3. **Provide emergency numbers prominently**
4. **Show nearest hospitals with contact info**
5. **Include critical DO/DON'T instructions**
6. **Always recommend immediate ER visit**

## Strict Response Template

All poison-related responses follow this **6-section template**:

```
### 1️⃣ Summary
- Poison name and category
- Common sources
- Risk level

### 2️⃣ Symptoms
- Early symptoms list
- Danger signs (seek help immediately)
- Disclaimer: "informational only, not a diagnosis"

### 3️⃣ Antidote Information
- Antidote exists: Yes/No
- Antidote name: [name only, NO dosage]
- Warning: "Antidotes must only be administered by trained medical professionals"

### 4️⃣ What To Do Now
- ✅ DO: Call poison control, go to ER, bring container, note time
- ❌ DO NOT: Specific safety warnings for that poison

### 5️⃣ Nearest Medical Support
- Hospitals ranked by: (best for poison cases) + (nearest)
- Poison Control Centers with phone numbers
- Selection note: "based on proximity + poison case readiness"

### 6️⃣ Disclaimer
- "This information is for awareness only and does not replace professional medical care"
- Emergency contacts
```

## Ranking Algorithm (Facilities)

```
backend/app/ml/data/
├── __init__.py                     # Module exports
├── comprehensive_toxicology_data.py # Detailed poison data (1500+ lines)
├── poison_knowledge.py             # Structured RAG poison entries
├── nepal_facilities.py             # Hospital/lab/center directory
└── symptom_based_poison_dataset_1200.csv  # ML training data

backend/app/services/
└── agentic_ai_service.py           # Main agent with RAG tools
```

## Future Enhancements

1. **Vector Embeddings** - Add semantic search with FAISS/ChromaDB
2. **Real-time Updates** - API to update facility availability
3. **Crowd-sourced Data** - Allow verified users to update facility info
4. **Regional Expansion** - Add facilities for other countries
5. **Multi-language Support** - Nepali translations for local users
