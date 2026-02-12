# Nepal Facilities Dataset - Hospitals, Labs, Poison Centers
# This module implements the Facilities RAG retriever for the PoisonSense AI

"""
Nepal-Based Poison Hospital/Lab Dataset
========================================
Schema follows the RAG architecture design with:
- Identity & Location
- Emergency Capability
- Services (Searchable Tags)
- Contact Information
- Metadata

Sources: Government health directories, hospital websites, verified contacts
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class FacilityType(str, Enum):
    HOSPITAL = "Hospital"
    LAB = "Lab"
    POISON_CENTER = "Poison Center"
    CLINIC = "Clinic"


@dataclass
class Facility:
    """Structured facility data for RAG retrieval"""
    facility_id: str
    facility_name: str
    facility_type: FacilityType
    province: str
    district: str
    municipality: str
    ward: Optional[str]
    address_line: str
    latitude: float
    longitude: float
    
    # Emergency Capability
    has_emergency: bool
    open_24_7: bool
    has_icu: bool
    has_pediatrics: bool
    has_toxicology: bool
    poison_case_ready_score: int  # 0-100 rating
    
    # Services
    services: List[str]  # ["ER", "ICU", "Toxicology", "Dialysis", etc.]
    lab_tests_available: List[str]
    antidote_stock_notes: str
    
    # Contact
    phone_primary: str
    phone_secondary: Optional[str]
    website: Optional[str]
    ambulance_available: bool
    
    # Metadata
    source: str
    last_verified_date: str
    notes: str


# =============================================================================
# NEPAL FACILITIES DATABASE
# =============================================================================

NEPAL_FACILITIES: Dict[str, dict] = {
    # =========================================================================
    # HOSPITALS - KATHMANDU VALLEY
    # =========================================================================
    "H001": {
        "facility_id": "H001",
        "facility_name": "Tribhuvan University Teaching Hospital (TUTH)",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "3",
        "address_line": "Maharajgunj, Kathmandu",
        "latitude": 27.7356,
        "longitude": 85.3318,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": True,
        "poison_case_ready_score": 95,
        "services": ["ER", "ICU", "Pediatrics", "Toxicology", "Decontamination", "Dialysis", "NPIC"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG", "Cholinesterase", "Toxicology Screen", "Acetaminophen Level", "Heavy Metal Panel"],
        "antidote_stock_notes": "Full stock: Atropine, Pralidoxime, NAC, Anti-Snake Venom, Naloxone, Vitamin K1, Activated Charcoal",
        "phone_primary": "+977-1-4412505",
        "phone_secondary": "+977-1-4411141",
        "website": "https://www.tuth.org.np",
        "ambulance_available": True,
        "source": "TUTH Official Website, NPIC",
        "last_verified_date": "2025-12-15",
        "notes": "National Poison Information Centre (NPIC) is located here. Best equipped for poisoning cases in Nepal."
    },
    "H002": {
        "facility_id": "H002",
        "facility_name": "Bir Hospital",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "11",
        "address_line": "Kanti Path, Ratna Park, Kathmandu",
        "latitude": 27.7050,
        "longitude": 85.3140,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": True,
        "poison_case_ready_score": 90,
        "services": ["ER", "ICU", "Trauma Center", "Toxicology", "Dialysis", "Endoscopy"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG", "Cholinesterase", "Toxicology Screen"],
        "antidote_stock_notes": "Good stock: Atropine, Pralidoxime, Anti-Snake Venom, Naloxone, Activated Charcoal",
        "phone_primary": "+977-1-4221119",
        "phone_secondary": "+977-1-4221988",
        "website": "https://www.birhospital.gov.np",
        "ambulance_available": True,
        "source": "Bir Hospital Official, Nepal Government Health Directory",
        "last_verified_date": "2025-12-10",
        "notes": "Government referral hospital with extensive emergency care. High volume of poisoning cases."
    },
    "H003": {
        "facility_id": "H003",
        "facility_name": "Patan Hospital",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Bagmati",
        "district": "Lalitpur",
        "municipality": "Lalitpur Metropolitan City",
        "ward": "5",
        "address_line": "Lagankhel, Patan, Lalitpur",
        "latitude": 27.6682,
        "longitude": 85.3188,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": True,
        "poison_case_ready_score": 88,
        "services": ["ER", "ICU", "Pediatrics", "Toxicology", "Endoscopy"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG", "Cholinesterase", "Acetaminophen Level"],
        "antidote_stock_notes": "Good stock: Atropine, Pralidoxime, NAC, Activated Charcoal",
        "phone_primary": "+977-1-5522295",
        "phone_secondary": "+977-1-5522266",
        "website": "https://www.patanhospital.org.np",
        "ambulance_available": True,
        "source": "Patan Hospital Official",
        "last_verified_date": "2025-12-08",
        "notes": "Strong pediatric poisoning expertise. Community trust."
    },
    "H004": {
        "facility_id": "H004",
        "facility_name": "Grande International Hospital",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "2",
        "address_line": "Tokha Road, Dhapasi, Kathmandu",
        "latitude": 27.7408,
        "longitude": 85.3248,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": True,
        "poison_case_ready_score": 85,
        "services": ["ER", "ICU", "Pediatrics", "Toxicology", "Dialysis", "Multi-Specialty"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG", "Toxicology Screen"],
        "antidote_stock_notes": "Full stock available (private hospital)",
        "phone_primary": "+977-1-5159266",
        "phone_secondary": "+977-1-5159267",
        "website": "https://www.grandehospital.com",
        "ambulance_available": True,
        "source": "Grande Hospital Official",
        "last_verified_date": "2025-12-05",
        "notes": "Private multi-specialty hospital with good emergency services."
    },
    "H005": {
        "facility_id": "H005",
        "facility_name": "Nepal Mediciti Hospital",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Bagmati",
        "district": "Lalitpur",
        "municipality": "Lalitpur Metropolitan City",
        "ward": "8",
        "address_line": "Nakhkhu, Bhaisepati, Lalitpur",
        "latitude": 27.6550,
        "longitude": 85.3027,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": False,
        "poison_case_ready_score": 75,
        "services": ["ER", "ICU", "Pediatrics", "Multi-Specialty", "Dialysis"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG"],
        "antidote_stock_notes": "Basic antidotes: Atropine, Pralidoxime, NAC",
        "phone_primary": "+977-1-4217766",
        "phone_secondary": "+977-1-4217767",
        "website": "https://www.nepalmediciti.com",
        "ambulance_available": True,
        "source": "Nepal Mediciti Official",
        "last_verified_date": "2025-11-20",
        "notes": "Modern private hospital. Good for stabilization, may refer complex toxicology."
    },
    "H006": {
        "facility_id": "H006",
        "facility_name": "Norvic International Hospital",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "12",
        "address_line": "Thapathali, Kathmandu",
        "latitude": 27.6942,
        "longitude": 85.3195,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": False,
        "poison_case_ready_score": 70,
        "services": ["ER", "ICU", "Cardiac Care", "Multi-Specialty"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG"],
        "antidote_stock_notes": "Basic antidotes: Atropine, Anti-Snake Venom",
        "phone_primary": "+977-1-5970032",
        "phone_secondary": "+977-1-5970033",
        "website": "https://www.norvichospital.com",
        "ambulance_available": True,
        "source": "Norvic Hospital Official",
        "last_verified_date": "2025-11-15",
        "notes": "Known for cardiac care. Can handle poisoning emergencies."
    },
    "H007": {
        "facility_id": "H007",
        "facility_name": "Manmohan Memorial Teaching Hospital",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "15",
        "address_line": "Swoyambhu, Kathmandu",
        "latitude": 27.7175,
        "longitude": 85.2905,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": True,
        "poison_case_ready_score": 80,
        "services": ["ER", "ICU", "Pediatrics", "Teaching Hospital", "Toxicology"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG", "Cholinesterase"],
        "antidote_stock_notes": "Good stock: Atropine, Pralidoxime",
        "phone_primary": "+977-1-5537055",
        "phone_secondary": "+977-1-5537056",
        "website": "https://www.manmohanhospital.edu.np",
        "ambulance_available": True,
        "source": "Manmohan Hospital Official",
        "last_verified_date": "2025-11-10",
        "notes": "Teaching hospital with good toxicology experience."
    },
    
    # =========================================================================
    # HOSPITALS - OUTSIDE KATHMANDU
    # =========================================================================
    "H008": {
        "facility_id": "H008",
        "facility_name": "B.P. Koirala Institute of Health Sciences (BPKIHS)",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Province 1",
        "district": "Sunsari",
        "municipality": "Dharan Sub-Metropolitan City",
        "ward": "5",
        "address_line": "Ghopa, Dharan",
        "latitude": 26.8147,
        "longitude": 87.2769,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": True,
        "poison_case_ready_score": 90,
        "services": ["ER", "ICU", "Pediatrics", "Toxicology", "Dialysis", "Teaching Hospital", "Snake Bite Center"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG", "Cholinesterase", "Toxicology Screen"],
        "antidote_stock_notes": "Full stock including Anti-Snake Venom (regional snake bite center)",
        "phone_primary": "+977-25-525555",
        "phone_secondary": "+977-25-520141",
        "website": "https://www.bpkihs.edu",
        "ambulance_available": True,
        "source": "BPKIHS Official",
        "last_verified_date": "2025-12-01",
        "notes": "Major referral center for Eastern Nepal. Excellent snake bite and pesticide poisoning expertise."
    },
    "H009": {
        "facility_id": "H009",
        "facility_name": "Manipal Teaching Hospital",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Gandaki",
        "district": "Kaski",
        "municipality": "Pokhara Metropolitan City",
        "ward": "12",
        "address_line": "Phulbari, Pokhara",
        "latitude": 28.2096,
        "longitude": 83.9856,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": True,
        "poison_case_ready_score": 85,
        "services": ["ER", "ICU", "Pediatrics", "Toxicology", "Dialysis", "Teaching Hospital"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG", "Cholinesterase"],
        "antidote_stock_notes": "Good stock: Atropine, Pralidoxime, Anti-Snake Venom",
        "phone_primary": "+977-61-526416",
        "phone_secondary": "+977-61-530983",
        "website": "https://www.manipal.edu.np",
        "ambulance_available": True,
        "source": "Manipal Hospital Official",
        "last_verified_date": "2025-11-25",
        "notes": "Major hospital for Western Nepal. Good toxicology services."
    },
    "H010": {
        "facility_id": "H010",
        "facility_name": "Bheri Hospital",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Lumbini",
        "district": "Banke",
        "municipality": "Nepalgunj Sub-Metropolitan City",
        "ward": "13",
        "address_line": "Nepalgunj, Banke",
        "latitude": 28.0552,
        "longitude": 81.6100,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": True,
        "poison_case_ready_score": 80,
        "services": ["ER", "ICU", "Pediatrics", "Toxicology", "Regional Referral"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG", "Cholinesterase"],
        "antidote_stock_notes": "Good stock: Atropine, Pralidoxime, Anti-Snake Venom",
        "phone_primary": "+977-81-520111",
        "phone_secondary": "+977-81-520112",
        "website": None,
        "ambulance_available": True,
        "source": "Government Health Directory",
        "last_verified_date": "2025-11-20",
        "notes": "Major referral center for Mid-Western Nepal."
    },
    "H011": {
        "facility_id": "H011",
        "facility_name": "Lumbini Provincial Hospital",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Lumbini",
        "district": "Rupandehi",
        "municipality": "Butwal Sub-Metropolitan City",
        "ward": "11",
        "address_line": "Butwal, Rupandehi",
        "latitude": 27.7006,
        "longitude": 83.4486,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": True,
        "poison_case_ready_score": 78,
        "services": ["ER", "ICU", "Pediatrics", "Toxicology", "Provincial Referral"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG"],
        "antidote_stock_notes": "Basic stock: Atropine, Pralidoxime",
        "phone_primary": "+977-71-540200",
        "phone_secondary": "+977-71-540201",
        "website": None,
        "ambulance_available": True,
        "source": "Government Health Directory",
        "last_verified_date": "2025-11-15",
        "notes": "Provincial hospital with good emergency services."
    },
    "H012": {
        "facility_id": "H012",
        "facility_name": "Koshi Hospital",
        "facility_type": FacilityType.HOSPITAL,
        "province": "Province 1",
        "district": "Morang",
        "municipality": "Biratnagar Metropolitan City",
        "ward": "5",
        "address_line": "Biratnagar, Morang",
        "latitude": 26.4525,
        "longitude": 87.2718,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": True,
        "has_pediatrics": True,
        "has_toxicology": True,
        "poison_case_ready_score": 82,
        "services": ["ER", "ICU", "Pediatrics", "Toxicology", "Zonal Referral"],
        "lab_tests_available": ["CBC", "RFT", "LFT", "Electrolytes", "ABG", "Cholinesterase"],
        "antidote_stock_notes": "Good stock: Atropine, Pralidoxime, Anti-Snake Venom",
        "phone_primary": "+977-21-460833",
        "phone_secondary": "+977-21-461422",
        "website": None,
        "ambulance_available": True,
        "source": "Government Health Directory",
        "last_verified_date": "2025-11-10",
        "notes": "Major hospital for Biratnagar region. Good pesticide poisoning experience."
    },
    
    # =========================================================================
    # POISON CONTROL CENTERS
    # =========================================================================
    "PC001": {
        "facility_id": "PC001",
        "facility_name": "National Poison Information Centre (NPIC-TUTH)",
        "facility_type": FacilityType.POISON_CENTER,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "3",
        "address_line": "Maharajgunj, TUTH Campus, Kathmandu",
        "latitude": 27.7356,
        "longitude": 85.3318,
        "has_emergency": True,
        "open_24_7": True,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": True,
        "poison_case_ready_score": 100,
        "services": ["24/7 Poison Information", "Toxicology Consultation", "Treatment Protocol Guidance", "Antidote Information", "Case Management Support"],
        "lab_tests_available": [],
        "antidote_stock_notes": "Provides guidance on antidote availability across Nepal",
        "phone_primary": "+977-1-4412505",
        "phone_secondary": "1102",
        "website": "https://www.tuth.org.np/npic",
        "ambulance_available": False,
        "source": "NPIC Official",
        "last_verified_date": "2025-12-15",
        "notes": "NATIONAL HOTLINE. First point of contact for all poisoning cases in Nepal. Call 24/7."
    },
    
    # =========================================================================
    # DIAGNOSTIC LABS
    # =========================================================================
    "L001": {
        "facility_id": "L001",
        "facility_name": "National Public Health Laboratory",
        "facility_type": FacilityType.LAB,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "11",
        "address_line": "Teku, Kathmandu",
        "latitude": 27.6956,
        "longitude": 85.3029,
        "has_emergency": False,
        "open_24_7": False,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": True,
        "poison_case_ready_score": 60,
        "services": ["Toxicology Testing", "Heavy Metal Analysis", "Drug Screening"],
        "lab_tests_available": ["Heavy Metal Panel", "Drug Screen", "Pesticide Analysis", "Toxicology Confirmation"],
        "antidote_stock_notes": "No treatment - diagnostic lab only",
        "phone_primary": "+977-1-4253355",
        "phone_secondary": "+977-1-4253356",
        "website": "https://www.nphl.gov.np",
        "ambulance_available": False,
        "source": "NPHL Official",
        "last_verified_date": "2025-11-01",
        "notes": "Reference lab for confirmatory toxicology testing. Not for emergencies."
    },
    
    # =========================================================================
    # DIAGNOSTIC LABORATORIES - KATHMANDU
    # =========================================================================
    "L002": {
        "facility_id": "L002",
        "facility_name": "Niramaya Diagnostics",
        "facility_type": FacilityType.LAB,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "10",
        "address_line": "New Road, Kathmandu",
        "latitude": 27.7030,
        "longitude": 85.3135,
        "has_emergency": False,
        "open_24_7": False,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": True,
        "poison_case_ready_score": 55,
        "services": ["Urine Drug Screen", "Toxicology Panel", "Clinical Pathology", "Biochemistry"],
        "lab_tests_available": ["CBC", "LFT", "RFT", "Electrolytes", "Urine Drug Screen (6-panel)", "Urine Drug Screen (9-panel)", "Alcohol Screen"],
        "antidote_stock_notes": "No treatment - diagnostic lab only",
        "phone_primary": "+977-1-4222333",
        "phone_secondary": None,
        "website": "https://niramayadiagnostics.com",
        "ambulance_available": False,
        "source": "Niramaya Diagnostics Official Website",
        "last_verified_date": "2026-01-15",
        "notes": "Specialized in urine drug screens (6-drug and 9-drug panels). Good for suspected drug toxicity testing."
    },
    "L003": {
        "facility_id": "L003",
        "facility_name": "NITA Polyclinic & Diagnostic Center",
        "facility_type": FacilityType.LAB,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "14",
        "address_line": "Chabahil, Kathmandu",
        "latitude": 27.7180,
        "longitude": 85.3450,
        "has_emergency": False,
        "open_24_7": False,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": True,
        "poison_case_ready_score": 50,
        "services": ["Drug Screening", "Alcohol Screening", "Clinical Pathology", "Biochemistry"],
        "lab_tests_available": ["CBC", "LFT", "RFT", "Electrolytes", "Drug and Alcohol Screening Panel", "Amphetamines Screen", "Morphine Screen", "Benzodiazepines Screen"],
        "antidote_stock_notes": "No treatment - diagnostic lab only",
        "phone_primary": "+977-1-4464466",
        "phone_secondary": None,
        "website": "https://www.nitapolyclinic.com.np",
        "ambulance_available": False,
        "source": "NITA Polyclinic Official Website",
        "last_verified_date": "2026-01-15",
        "notes": "Provides drug and alcohol screening panels including amphetamines, morphine, benzodiazepines. Non-emergency diagnostic center."
    },
    "L004": {
        "facility_id": "L004",
        "facility_name": "Nepal Lab House",
        "facility_type": FacilityType.LAB,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "11",
        "address_line": "Putalisadak, Kathmandu",
        "latitude": 27.7040,
        "longitude": 85.3200,
        "has_emergency": False,
        "open_24_7": False,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": False,
        "poison_case_ready_score": 40,
        "services": ["Clinical Pathology", "Biochemistry", "Hematology"],
        "lab_tests_available": ["CBC", "LFT", "RFT", "Electrolytes", "Blood Sugar", "Lipid Profile"],
        "antidote_stock_notes": "No treatment - diagnostic lab only",
        "phone_primary": "+977-1-4418888",
        "phone_secondary": None,
        "website": None,
        "ambulance_available": False,
        "source": "NPHL Registered Laboratory List",
        "last_verified_date": "2026-01-10",
        "notes": "Accredited medical laboratory for routine blood and biochemistry tests. Not specialized in toxicology."
    },
    "L005": {
        "facility_id": "L005",
        "facility_name": "National Path Lab and Research Center",
        "facility_type": FacilityType.LAB,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "10",
        "address_line": "Bagbazar, Kathmandu",
        "latitude": 27.7050,
        "longitude": 85.3180,
        "has_emergency": False,
        "open_24_7": False,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": False,
        "poison_case_ready_score": 40,
        "services": ["Clinical Pathology", "Chemistry Panels", "Hematology"],
        "lab_tests_available": ["CBC", "LFT", "RFT", "Electrolytes", "Chemistry Panel"],
        "antidote_stock_notes": "No treatment - diagnostic lab only",
        "phone_primary": "+977-1-4244555",
        "phone_secondary": None,
        "website": None,
        "ambulance_available": False,
        "source": "NPHL Registered Laboratory List",
        "last_verified_date": "2026-01-10",
        "notes": "Clinical lab performing CBC and chemistry panels. Routine pathology services."
    },
    "L006": {
        "facility_id": "L006",
        "facility_name": "Central Diagnostic Laboratory and Research Center",
        "facility_type": FacilityType.LAB,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "13",
        "address_line": "Kalanki, Kathmandu",
        "latitude": 27.6940,
        "longitude": 85.2810,
        "has_emergency": False,
        "open_24_7": False,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": False,
        "poison_case_ready_score": 35,
        "services": ["Clinical Pathology", "Routine Blood Tests"],
        "lab_tests_available": ["CBC", "LFT", "RFT", "Electrolytes"],
        "antidote_stock_notes": "No treatment - diagnostic lab only",
        "phone_primary": "+977-1-4276666",
        "phone_secondary": None,
        "website": None,
        "ambulance_available": False,
        "source": "NPHL Registered Laboratory List",
        "last_verified_date": "2026-01-10",
        "notes": "Routine pathology services. Not specialized in toxicology."
    },
    "L007": {
        "facility_id": "L007",
        "facility_name": "Crystal Diagnostic Pvt. Ltd.",
        "facility_type": FacilityType.LAB,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "15",
        "address_line": "Balaju, Kathmandu",
        "latitude": 27.7280,
        "longitude": 85.3010,
        "has_emergency": False,
        "open_24_7": False,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": False,
        "poison_case_ready_score": 35,
        "services": ["Clinical Pathology", "Blood Tests"],
        "lab_tests_available": ["CBC", "LFT", "RFT", "Electrolytes", "Blood Sugar"],
        "antidote_stock_notes": "No treatment - diagnostic lab only",
        "phone_primary": "+977-1-4350555",
        "phone_secondary": None,
        "website": None,
        "ambulance_available": False,
        "source": "NPHL Registered Laboratory List",
        "last_verified_date": "2026-01-10",
        "notes": "Clinical pathology and blood tests. Routine services."
    },
    "L008": {
        "facility_id": "L008",
        "facility_name": "Reliable Diagnostic Laboratory Nepal Pvt Ltd",
        "facility_type": FacilityType.LAB,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "9",
        "address_line": "Tripureshwor, Kathmandu",
        "latitude": 27.6950,
        "longitude": 85.3100,
        "has_emergency": False,
        "open_24_7": False,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": False,
        "poison_case_ready_score": 45,
        "services": ["Clinical Pathology", "Biochemistry", "Broad Test Menu"],
        "lab_tests_available": ["CBC", "LFT", "RFT", "Electrolytes", "Lipid Profile", "Thyroid Panel", "HbA1c"],
        "antidote_stock_notes": "No treatment - diagnostic lab only",
        "phone_primary": "+977-1-4261111",
        "phone_secondary": None,
        "website": None,
        "ambulance_available": False,
        "source": "NPHL Registered Laboratory List",
        "last_verified_date": "2026-01-10",
        "notes": "Highly rated diagnostic center with broad test offerings. Not specialized in toxicology."
    },
    "L009": {
        "facility_id": "L009",
        "facility_name": "Dr. Lal PathLabs - Kathmandu",
        "facility_type": FacilityType.LAB,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "11",
        "address_line": "Putalisadak, Kathmandu",
        "latitude": 27.7055,
        "longitude": 85.3210,
        "has_emergency": False,
        "open_24_7": False,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": False,
        "poison_case_ready_score": 40,
        "services": ["Clinical Pathology", "Routine Blood Tests", "Lab Network"],
        "lab_tests_available": ["CBC", "LFT", "RFT", "Electrolytes", "Lipid Profile", "Thyroid Panel"],
        "antidote_stock_notes": "No treatment - diagnostic lab only",
        "phone_primary": "+977-1-4433000",
        "phone_secondary": None,
        "website": "https://www.lalpathlabs.com",
        "ambulance_available": False,
        "source": "Dr. Lal PathLabs Official",
        "last_verified_date": "2026-01-10",
        "notes": "Lab network offering routine blood tests. Multiple branches in Kathmandu."
    },
    "L010": {
        "facility_id": "L010",
        "facility_name": "Dr. Lal PathLabs - Kuleshwor",
        "facility_type": FacilityType.LAB,
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "Kathmandu Metropolitan City",
        "ward": "14",
        "address_line": "Kuleshwor, Kathmandu",
        "latitude": 27.6920,
        "longitude": 85.2980,
        "has_emergency": False,
        "open_24_7": False,
        "has_icu": False,
        "has_pediatrics": False,
        "has_toxicology": False,
        "poison_case_ready_score": 40,
        "services": ["Clinical Pathology", "Routine Blood Tests"],
        "lab_tests_available": ["CBC", "LFT", "RFT", "Electrolytes", "Lipid Profile"],
        "antidote_stock_notes": "No treatment - diagnostic lab only",
        "phone_primary": "+977-1-4288000",
        "phone_secondary": None,
        "website": "https://www.lalpathlabs.com",
        "ambulance_available": False,
        "source": "Dr. Lal PathLabs Official",
        "last_verified_date": "2026-01-10",
        "notes": "Branch of Dr. Lal PathLabs in Kuleshwor area."
    },
}


# =============================================================================
# RAG RETRIEVER FUNCTIONS
# =============================================================================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def retrieve_nearest_facilities(
    latitude: float,
    longitude: float,
    facility_type: Optional[FacilityType] = None,
    max_distance_km: float = 100,
    min_poison_score: int = 50,
    require_emergency: bool = True,
    require_24_7: bool = False,
    limit: int = 5
) -> List[Dict]:
    """
    RAG Retriever: Find nearest suitable facilities for poisoning cases.
    
    Ranking algorithm:
    1. Filter by distance
    2. Filter by facility type (if specified)
    3. Filter by emergency capability
    4. Rank by: poison_case_ready_score + proximity bonus
    
    Returns list of facilities with distance and suitability score.
    """
    results = []
    
    for facility_id, facility in NEPAL_FACILITIES.items():
        # Calculate distance
        distance = calculate_distance(
            latitude, longitude,
            facility["latitude"], facility["longitude"]
        )
        
        # Skip if too far
        if distance > max_distance_km:
            continue
        
        # Filter by facility type
        if facility_type and facility["facility_type"] != facility_type:
            continue
        
        # Filter by emergency capability
        if require_emergency and not facility["has_emergency"]:
            continue
        
        # Filter by 24/7 availability
        if require_24_7 and not facility["open_24_7"]:
            continue
        
        # Filter by poison readiness score
        if facility["poison_case_ready_score"] < min_poison_score:
            continue
        
        # Calculate suitability score
        # Base score from poison_case_ready_score
        base_score = facility["poison_case_ready_score"]
        
        # Proximity bonus (closer = higher bonus, max 20 points)
        proximity_bonus = max(0, 20 - (distance / 5))
        
        # Emergency bonus
        emergency_bonus = 10 if facility["has_emergency"] else 0
        
        # 24/7 bonus
        availability_bonus = 5 if facility["open_24_7"] else 0
        
        # Toxicology unit bonus
        toxicology_bonus = 15 if facility["has_toxicology"] else 0
        
        total_score = base_score + proximity_bonus + emergency_bonus + availability_bonus + toxicology_bonus
        
        results.append({
            "facility_id": facility_id,
            "facility_name": facility["facility_name"],
            "facility_type": facility["facility_type"].value if isinstance(facility["facility_type"], FacilityType) else facility["facility_type"],
            "distance_km": round(distance, 2),
            "suitability_score": round(total_score, 1),
            "poison_case_ready_score": facility["poison_case_ready_score"],
            "has_emergency": facility["has_emergency"],
            "open_24_7": facility["open_24_7"],
            "has_toxicology": facility["has_toxicology"],
            "services": facility["services"],
            "antidote_stock_notes": facility["antidote_stock_notes"],
            "phone_primary": facility["phone_primary"],
            "phone_secondary": facility["phone_secondary"],
            "address": f"{facility['address_line']}, {facility['district']}",
            "latitude": facility["latitude"],
            "longitude": facility["longitude"],
            "notes": facility["notes"]
        })
    
    # Sort by suitability score (highest first), then by distance
    results.sort(key=lambda x: (-x["suitability_score"], x["distance_km"]))
    
    return results[:limit]


def retrieve_facilities_by_antidote(antidote_name: str, limit: int = 5) -> List[Dict]:
    """
    RAG Retriever: Find facilities that likely have a specific antidote.
    
    Searches antidote_stock_notes field.
    """
    results = []
    antidote_lower = antidote_name.lower()
    
    for facility_id, facility in NEPAL_FACILITIES.items():
        stock_notes = facility.get("antidote_stock_notes", "").lower()
        
        if antidote_lower in stock_notes or "full stock" in stock_notes:
            results.append({
                "facility_id": facility_id,
                "facility_name": facility["facility_name"],
                "facility_type": facility["facility_type"].value if isinstance(facility["facility_type"], FacilityType) else facility["facility_type"],
                "antidote_stock_notes": facility["antidote_stock_notes"],
                "phone_primary": facility["phone_primary"],
                "address": f"{facility['address_line']}, {facility['district']}",
                "poison_case_ready_score": facility["poison_case_ready_score"],
                "has_emergency": facility["has_emergency"],
                "open_24_7": facility["open_24_7"]
            })
    
    # Sort by poison readiness score
    results.sort(key=lambda x: -x["poison_case_ready_score"])
    
    return results[:limit]


def retrieve_facilities_by_service(service: str, limit: int = 10) -> List[Dict]:
    """
    RAG Retriever: Find facilities offering a specific service.
    
    Example services: "ICU", "Dialysis", "Toxicology", "Snake Bite Center"
    """
    results = []
    service_lower = service.lower()
    
    for facility_id, facility in NEPAL_FACILITIES.items():
        services_lower = [s.lower() for s in facility.get("services", [])]
        
        if any(service_lower in s for s in services_lower):
            results.append({
                "facility_id": facility_id,
                "facility_name": facility["facility_name"],
                "facility_type": facility["facility_type"].value if isinstance(facility["facility_type"], FacilityType) else facility["facility_type"],
                "services": facility["services"],
                "phone_primary": facility["phone_primary"],
                "address": f"{facility['address_line']}, {facility['district']}",
                "poison_case_ready_score": facility["poison_case_ready_score"],
                "latitude": facility["latitude"],
                "longitude": facility["longitude"]
            })
    
    # Sort by poison readiness score
    results.sort(key=lambda x: -x["poison_case_ready_score"])
    
    return results[:limit]


def get_poison_control_hotline() -> Dict:
    """
    Get the national poison control hotline information.
    """
    npic = NEPAL_FACILITIES.get("PC001", {})
    return {
        "name": "National Poison Information Centre (NPIC-TUTH)",
        "hotline": "+977-1-4412505",
        "toll_free": "1102",
        "available": "24/7",
        "services": ["Poison Information", "Treatment Guidance", "Antidote Information"],
        "notes": "Call immediately for any poisoning emergency in Nepal"
    }


def get_facility_details(facility_id: str) -> Optional[Dict]:
    """
    Get detailed information about a specific facility.
    """
    return NEPAL_FACILITIES.get(facility_id)


def get_all_facilities_summary() -> List[Dict]:
    """
    Get a summary of all facilities in the database.
    """
    return [
        {
            "facility_id": fid,
            "facility_name": f["facility_name"],
            "facility_type": f["facility_type"].value if isinstance(f["facility_type"], FacilityType) else f["facility_type"],
            "district": f["district"],
            "poison_case_ready_score": f["poison_case_ready_score"],
            "has_emergency": f["has_emergency"],
            "phone_primary": f["phone_primary"]
        }
        for fid, f in NEPAL_FACILITIES.items()
    ]


def retrieve_diagnostic_labs(
    latitude: float = None,
    longitude: float = None,
    test_type: str = None,
    require_toxicology: bool = False,
    limit: int = 10
) -> List[Dict]:
    """
    RAG Retriever: Find diagnostic laboratories for clinical testing.
    
    Used for non-emergency cases where doctors need to refer patients
    for poison-related clinical testing (CBC, electrolytes, toxicology panels).
    
    Args:
        latitude, longitude: Optional location for proximity sorting
        test_type: Specific test to search for (e.g., "drug screen", "CBC")
        require_toxicology: Only return labs with toxicology capability
        limit: Maximum number of results
        
    Returns:
        List of diagnostic labs with test availability info
    """
    results = []
    test_type_lower = test_type.lower() if test_type else None
    
    for facility_id, facility in NEPAL_FACILITIES.items():
        # Only include labs
        if facility["facility_type"] != FacilityType.LAB:
            continue
        
        # Filter by toxicology capability
        if require_toxicology and not facility["has_toxicology"]:
            continue
        
        # Filter by test type if specified
        if test_type_lower:
            tests_lower = [t.lower() for t in facility.get("lab_tests_available", [])]
            services_lower = [s.lower() for s in facility.get("services", [])]
            if not any(test_type_lower in t for t in tests_lower + services_lower):
                continue
        
        # Calculate distance if location provided
        distance = None
        if latitude and longitude:
            distance = calculate_distance(
                latitude, longitude,
                facility["latitude"], facility["longitude"]
            )
        
        results.append({
            "facility_id": facility_id,
            "facility_name": facility["facility_name"],
            "facility_type": "Diagnostic Lab",
            "distance_km": round(distance, 2) if distance else None,
            "has_toxicology": facility["has_toxicology"],
            "services": facility["services"],
            "lab_tests_available": facility["lab_tests_available"],
            "phone_primary": facility["phone_primary"],
            "website": facility["website"],
            "address": f"{facility['address_line']}, {facility['district']}",
            "notes": facility["notes"]
        })
    
    # Sort by toxicology capability first, then by distance if available
    if latitude and longitude:
        results.sort(key=lambda x: (not x["has_toxicology"], x["distance_km"] or 999))
    else:
        results.sort(key=lambda x: not x["has_toxicology"])
    
    return results[:limit]


def retrieve_labs_for_drug_screening(limit: int = 5) -> List[Dict]:
    """
    RAG Retriever: Find labs that offer drug/toxicology screening panels.
    
    Specifically for urine drug screens, alcohol panels, and toxicology tests.
    """
    results = []
    drug_keywords = ["drug", "toxicology", "alcohol", "urine", "screen", "panel"]
    
    for facility_id, facility in NEPAL_FACILITIES.items():
        if facility["facility_type"] != FacilityType.LAB:
            continue
        
        # Check if lab offers drug screening
        tests_lower = [t.lower() for t in facility.get("lab_tests_available", [])]
        services_lower = [s.lower() for s in facility.get("services", [])]
        all_offerings = tests_lower + services_lower
        
        has_drug_screening = any(
            any(keyword in offering for keyword in drug_keywords)
            for offering in all_offerings
        )
        
        if has_drug_screening:
            results.append({
                "facility_id": facility_id,
                "facility_name": facility["facility_name"],
                "has_toxicology": facility["has_toxicology"],
                "drug_tests_available": [
                    t for t in facility.get("lab_tests_available", [])
                    if any(k in t.lower() for k in drug_keywords)
                ],
                "phone_primary": facility["phone_primary"],
                "website": facility["website"],
                "address": f"{facility['address_line']}, {facility['district']}",
                "notes": facility["notes"]
            })
    
    # Sort by toxicology capability
    results.sort(key=lambda x: not x["has_toxicology"])
    
    return results[:limit]


def get_testing_guidance(test_category: str) -> Dict:
    """
    Get guidance on where to get specific types of tests done.
    
    Categories:
    - "routine": CBC, LFT, RFT, Electrolytes
    - "drug_screen": Urine drug panels
    - "toxicology": Specialized toxicology testing
    - "emergency": ABG, cholinesterase (hospital only)
    """
    category_lower = test_category.lower()
    
    if category_lower in ["routine", "cbc", "lft", "rft", "electrolytes"]:
        return {
            "test_category": "Routine Blood Tests",
            "tests": ["CBC", "LFT", "RFT", "Electrolytes"],
            "where_to_go": "Any hospital or diagnostic lab",
            "recommended_facilities": [
                "All listed hospitals and diagnostic labs can perform these tests"
            ],
            "notes": "Widely available. Results typically within 24 hours."
        }
    
    elif category_lower in ["drug", "drug_screen", "urine", "toxicology_screen"]:
        drug_labs = retrieve_labs_for_drug_screening(limit=3)
        return {
            "test_category": "Drug/Toxicology Screening",
            "tests": ["Urine Drug Screen (6-panel)", "Urine Drug Screen (9-panel)", "Alcohol Screen"],
            "where_to_go": "Specialized diagnostic labs",
            "recommended_facilities": [
                {"name": lab["facility_name"], "phone": lab["phone_primary"]}
                for lab in drug_labs
            ],
            "notes": "For suspected drug toxicity. Niramaya Diagnostics and NITA Polyclinic specialize in these panels."
        }
    
    elif category_lower in ["toxicology", "heavy_metal", "pesticide"]:
        return {
            "test_category": "Specialized Toxicology Testing",
            "tests": ["Heavy Metal Panel", "Pesticide Analysis", "Toxicology Confirmation"],
            "where_to_go": "Hospital labs or National Public Health Laboratory",
            "recommended_facilities": [
                {"name": "National Public Health Laboratory", "phone": "+977-1-4253355"},
                {"name": "TUTH Hospital Lab", "phone": "+977-1-4412505"}
            ],
            "notes": "Confirmatory tests. May require physician referral. Results may take longer."
        }
    
    elif category_lower in ["emergency", "abg", "cholinesterase", "critical"]:
        return {
            "test_category": "Emergency/Critical Tests",
            "tests": ["ABG", "Cholinesterase", "Acetaminophen Level", "Real-time Monitoring"],
            "where_to_go": "Hospital laboratories ONLY",
            "recommended_facilities": [
                {"name": "TUTH", "phone": "+977-1-4412505"},
                {"name": "Bir Hospital", "phone": "+977-1-4221119"},
                {"name": "Patan Hospital", "phone": "+977-1-5522295"}
            ],
            "notes": "These tests require emergency department/hospital setting. Not available in standalone labs."
        }
    
    else:
        return {
            "test_category": "Unknown",
            "notes": "Please specify: routine, drug_screen, toxicology, or emergency"
        }
