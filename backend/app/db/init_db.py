# Initialize database - Database initialization and seed data
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User, UserRole, EmergencyContact
from app.models.doctor import Doctor, VerificationStatus
from app.models.hospital import Hospital, ToxicologyLab, HospitalType
from app.models.poison_center import PoisonCenter, AntidoteInventory
from app.models.poison import Poison, ManagementProtocol, PoisonCategory, SeverityLevel
from app.models.ai_log import AIModelVersion
from app.core.security import get_password_hash

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ All database tables created")

def seed_admin_user(db: Session):
    """Create default admin user"""
    admin = db.query(User).filter(User.email == "admin@poisonsense.ai").first()
    if not admin:
        admin = User(
            email="admin@poisonsense.ai",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            phone="+91-9999999999",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin)
        db.commit()
        print("✅ Admin user created (admin@poisonsense.ai / admin123)")
    return admin

def seed_poison_centers(db: Session):
    """Seed Poison Control Centers - Nepal"""
    centers_data = [
        # ============ NEPAL POISON CENTERS ============
        {
            "name": "National Poison Information Centre, Nepal (TUTH)",
            "code": "NPIC-NEPAL",
            "phone_primary": "+977-1-4412505",
            "phone_secondary": "+977-1-4411141",
            "toll_free_number": "1102",
            "email": "npic@tuth.gov.np",
            "website": "https://www.tuth.org.np",
            "address": "Maharajgunj, Tribhuvan University Teaching Hospital",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.7356,
            "longitude": 85.3318,
            "coverage_area": "National - Nepal",
            "coverage_districts": ["Kathmandu", "Lalitpur", "Bhaktapur", "All Nepal"],
            "services": ["24/7 Poison Information", "Emergency Toxicology Consultation", "Treatment Protocols", "Antidote Information"],
            "specializations": ["Organophosphate Poisoning", "Snake Bites", "Drug Overdose", "Pesticide Poisoning"],
            "is_24_hours": True,
            "is_verified": True,
            "government_affiliated": True
        },
        {
            "name": "Bir Hospital Emergency & Poison Center",
            "code": "PCC-BIR",
            "phone_primary": "+977-1-4221119",
            "phone_secondary": "+977-1-4221988",
            "email": "info@birhospital.gov.np",
            "address": "Kanti Path, Ratna Park",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.7050,
            "longitude": 85.3140,
            "coverage_area": "Central Nepal",
            "coverage_districts": ["Kathmandu", "Lalitpur", "Bhaktapur"],
            "services": ["Emergency Toxicology", "ICU Care", "Poison Treatment"],
            "specializations": ["General Poisoning", "Drug Overdose"],
            "is_24_hours": True,
            "is_verified": True,
            "government_affiliated": True
        },
        {
            "name": "Patan Hospital Emergency Department",
            "code": "PCC-PATAN",
            "phone_primary": "+977-1-5522295",
            "phone_secondary": "+977-1-5522278",
            "email": "info@patanhospital.org.np",
            "address": "Lagankhel, Patan",
            "city": "Lalitpur",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.6682,
            "longitude": 85.3188,
            "coverage_area": "Lalitpur Valley",
            "coverage_districts": ["Lalitpur", "Kathmandu"],
            "services": ["Emergency Services", "Toxicology", "Pediatric Poisoning"],
            "is_24_hours": True,
            "is_verified": True,
            "government_affiliated": True
        },
        {
            "name": "B.P. Koirala Institute of Health Sciences (BPKIHS)",
            "code": "PCC-BPKIHS",
            "phone_primary": "+977-25-525555",
            "phone_secondary": "+977-25-521017",
            "email": "info@bpkihs.edu",
            "address": "Ghopa, Dharan",
            "city": "Dharan",
            "state": "Province 1",
            "country": "Nepal",
            "latitude": 26.8127,
            "longitude": 87.2832,
            "coverage_area": "Eastern Nepal",
            "coverage_districts": ["Sunsari", "Morang", "Jhapa"],
            "services": ["Emergency Toxicology", "Snake Bite Treatment", "Research"],
            "specializations": ["Snake Envenomation", "Organophosphate Poisoning"],
            "is_24_hours": True,
            "is_verified": True,
            "government_affiliated": True
        },
        {
            "name": "Kanti Children's Hospital Poison Center",
            "code": "PCC-KANTI",
            "phone_primary": "+977-1-4411550",
            "phone_secondary": "+977-1-4414798",
            "email": "info@kantihospital.gov.np",
            "address": "Maharajgunj",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.7341,
            "longitude": 85.3310,
            "coverage_area": "Kathmandu Valley",
            "coverage_districts": ["Kathmandu", "Lalitpur", "Bhaktapur"],
            "services": ["Pediatric Emergency", "Pediatric Poisoning", "ICU"],
            "specializations": ["Pediatric Poisoning", "Accidental Ingestion"],
            "is_24_hours": True,
            "is_verified": True,
            "government_affiliated": True
        }
    ]
    
    for center_data in centers_data:
        existing = db.query(PoisonCenter).filter(
            PoisonCenter.code == center_data["code"]
        ).first()
        if not existing:
            center = PoisonCenter(**center_data)
            db.add(center)
    
    db.commit()
    print(f"✅ Seeded {len(centers_data)} poison control centers")

def seed_hospitals(db: Session):
    """Seed major hospitals with toxicology units - Nepal"""
    hospitals_data = [
        # ============ NEPAL HOSPITALS ============
        {
            "name": "Tribhuvan University Teaching Hospital (TUTH)",
            "hospital_type": HospitalType.GOVERNMENT,
            "phone": "+977-1-4412505",
            "emergency_phone": "1102",
            "address": "Maharajgunj",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.7356,
            "longitude": 85.3318,
            "facilities": ["ICU", "Emergency", "Toxicology Unit", "NPIC", "Toxicology Lab"],
            "antidotes_available": ["Atropine", "Pralidoxime", "N-Acetylcysteine", "Anti-Snake Venom", "Activated Charcoal", "Naloxone", "Vitamin K1"],
            "toxicology_tests": [
                {"name": "Blood Toxicology Screen", "price": "NPR 2,500", "duration": "2-4 hours"},
                {"name": "Urine Drug Screen", "price": "NPR 1,000", "duration": "1-2 hours"},
                {"name": "Cholinesterase Level", "price": "NPR 800", "duration": "2 hours"},
                {"name": "Acetaminophen Level", "price": "NPR 600", "duration": "1 hour"},
                {"name": "Heavy Metal Panel", "price": "NPR 3,500", "duration": "24-48 hours"}
            ],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "Bir Hospital",
            "hospital_type": HospitalType.GOVERNMENT,
            "phone": "+977-1-4221119",
            "emergency_phone": "102",
            "address": "Kanti Path, Ratna Park",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.7050,
            "longitude": 85.3140,
            "facilities": ["ICU", "Emergency", "Trauma Center", "Toxicology", "Toxicology Lab"],
            "antidotes_available": ["Atropine", "Anti-Snake Venom", "Pralidoxime", "Naloxone", "Activated Charcoal"],
            "toxicology_tests": [
                {"name": "Blood Toxicology Screen", "price": "NPR 2,000", "duration": "3 hours"},
                {"name": "Urine Drug Screen", "price": "NPR 800", "duration": "2 hours"},
                {"name": "Cholinesterase Level", "price": "NPR 700", "duration": "2 hours"}
            ],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "Patan Hospital",
            "hospital_type": HospitalType.GOVERNMENT,
            "phone": "+977-1-5522295",
            "emergency_phone": "+977-1-5522266",
            "address": "Lagankhel, Patan",
            "city": "Lalitpur",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.6682,
            "longitude": 85.3188,
            "facilities": ["ICU", "Emergency", "Pediatrics", "Toxicology", "Toxicology Lab"],
            "antidotes_available": ["Atropine", "Pralidoxime", "Activated Charcoal", "N-Acetylcysteine"],
            "toxicology_tests": [
                {"name": "Blood Toxicology Screen", "price": "NPR 2,200", "duration": "3 hours"},
                {"name": "Urine Drug Screen", "price": "NPR 900", "duration": "2 hours"},
                {"name": "Acetaminophen Level", "price": "NPR 550", "duration": "1 hour"}
            ],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "Grande International Hospital",
            "hospital_type": HospitalType.PRIVATE,
            "phone": "+977-1-5159266",
            "emergency_phone": "+977-1-5159266",
            "address": "Tokha Road, Dhapasi",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.7408,
            "longitude": 85.3248,
            "facilities": ["ICU", "Emergency", "Full Services", "Toxicology Unit"],
            "antidotes_available": ["Full Antidote Stock", "Anti-Snake Venom"],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "Nepal Mediciti Hospital",
            "hospital_type": HospitalType.PRIVATE,
            "phone": "+977-1-4217766",
            "emergency_phone": "+977-1-4217766",
            "address": "Nakhkhu, Bhaisepati",
            "city": "Lalitpur",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.6550,
            "longitude": 85.3027,
            "facilities": ["ICU", "Emergency", "Multi-Specialty"],
            "antidotes_available": ["Atropine", "Pralidoxime", "N-Acetylcysteine"],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "Norvic International Hospital",
            "hospital_type": HospitalType.PRIVATE,
            "phone": "+977-1-5970032",
            "emergency_phone": "+977-1-5970032",
            "address": "Thapathali",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.6942,
            "longitude": 85.3195,
            "facilities": ["ICU", "Emergency", "Cardiac Care"],
            "antidotes_available": ["Atropine", "Anti-Snake Venom"],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "Manmohan Memorial Teaching Hospital",
            "hospital_type": HospitalType.TEACHING,
            "phone": "+977-1-5537055",
            "emergency_phone": "+977-1-5537055",
            "address": "Swoyambhu",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.7175,
            "longitude": 85.2905,
            "facilities": ["ICU", "Emergency", "Teaching Hospital"],
            "antidotes_available": ["Atropine", "Pralidoxime"],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "B.P. Koirala Institute of Health Sciences (BPKIHS)",
            "hospital_type": HospitalType.GOVERNMENT,
            "phone": "+977-25-525555",
            "emergency_phone": "+977-25-520141",
            "address": "Ghopa, Dharan",
            "city": "Dharan",
            "state": "Province 1",
            "country": "Nepal",
            "latitude": 26.8127,
            "longitude": 87.2832,
            "facilities": ["ICU", "Emergency", "Snake Bite Center", "Toxicology Research"],
            "antidotes_available": ["Anti-Snake Venom", "Atropine", "Pralidoxime", "All Major Antidotes"],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "Kanti Children's Hospital",
            "hospital_type": HospitalType.GOVERNMENT,
            "phone": "+977-1-4411550",
            "emergency_phone": "+977-1-4414798",
            "address": "Maharajgunj",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.7341,
            "longitude": 85.3310,
            "facilities": ["Pediatric ICU", "Emergency", "Pediatric Toxicology"],
            "antidotes_available": ["Atropine", "Activated Charcoal", "N-Acetylcysteine"],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "Kathmandu Medical College Teaching Hospital",
            "hospital_type": HospitalType.TEACHING,
            "phone": "+977-1-4476225",
            "emergency_phone": "+977-1-4476225",
            "address": "Sinamangal",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.6958,
            "longitude": 85.3494,
            "facilities": ["ICU", "Emergency", "Teaching Hospital"],
            "antidotes_available": ["Atropine", "Pralidoxime"],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "Civil Service Hospital",
            "hospital_type": HospitalType.GOVERNMENT,
            "phone": "+977-1-4107000",
            "emergency_phone": "+977-1-4107000",
            "address": "Minbhawan, New Baneshwor",
            "city": "Kathmandu",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.6898,
            "longitude": 85.3428,
            "facilities": ["ICU", "Emergency", "General Medicine"],
            "antidotes_available": ["Atropine", "Pralidoxime"],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        },
        {
            "name": "Chitwan Medical College Teaching Hospital",
            "hospital_type": HospitalType.TEACHING,
            "phone": "+977-56-524222",
            "emergency_phone": "+977-56-524222",
            "address": "Bharatpur",
            "city": "Bharatpur",
            "state": "Bagmati",
            "country": "Nepal",
            "latitude": 27.6834,
            "longitude": 84.4296,
            "facilities": ["ICU", "Emergency", "Snake Bite Treatment"],
            "antidotes_available": ["Anti-Snake Venom", "Atropine", "Pralidoxime"],
            "is_24_hours": True,
            "is_verified": True,
            "is_active": True
        }
    ]
    
    for hospital_data in hospitals_data:
        existing = db.query(Hospital).filter(
            Hospital.name == hospital_data["name"]
        ).first()
        if not existing:
            hospital = Hospital(**hospital_data)
            db.add(hospital)
    
    db.commit()
    print(f"✅ Seeded {len(hospitals_data)} hospitals")

def seed_poisons(db: Session):
    """Seed common poisons with comprehensive management protocols"""
    poisons_data = [
        {
            "name": "Organophosphate",
            "category": PoisonCategory.AGRICULTURAL,
            "common_names": ["Malathion", "Parathion", "Chlorpyrifos", "Diazinon", "Dimethoate"],
            "common_sources": ["Pesticide sprays", "Insecticides", "Farm chemicals", "Agricultural runoff"],
            "symptoms_immediate": ["Excessive salivation (SLUDGE)", "Lacrimation", "Urination", "Diarrhea", "Emesis"],
            "symptoms_delayed": ["Miosis (pinpoint pupils)", "Bradycardia", "Respiratory depression", "Muscle fasciculations", "Seizures"],
            "typical_severity": SeverityLevel.SEVERE,
            "antidote": "Atropine + Pralidoxime (2-PAM)",
            "antidote_alternatives": ["Atropine alone if Pralidoxime unavailable"],
            "antidote_dosage": "Atropine: 2-4mg IV, repeat q5-10min until secretions dry. Pralidoxime: 1-2g IV over 30min, may repeat",
            "first_aid": "1. Remove from exposure immediately\n2. Remove contaminated clothing\n3. Wash skin with soap and water\n4. Do NOT induce vomiting\n5. Call emergency services",
            "decontamination": "Full skin decontamination with soap and water. Gastric lavage if <1 hour and airway protected.",
            "management_protocol": "1. Secure airway\n2. Atropine IV until secretions dry (may need large doses)\n3. Pralidoxime within 24-48 hours\n4. Benzodiazepines for seizures\n5. Ventilatory support as needed",
            "supportive_care": "ICU monitoring, ventilatory support, seizure precautions, avoid succinylcholine",
            "contraindications": "Do NOT use morphine, aminophylline, or phenothiazines. Avoid succinylcholine for intubation.",
            "tests_required": ["Cholinesterase level (RBC and plasma)", "ABG", "Electrolytes", "ECG"],
            "monitoring_parameters": ["Pupil size", "Secretions", "Heart rate", "Respiratory status", "Muscle fasciculations"],
            "data_sources": [
                {"source": "Nepal NPIC Guidelines", "type": "government", "year": 2023},
                {"source": "WHO Guidelines on Organophosphate Poisoning", "type": "international"}
            ],
            "prognosis": "Good if treated early. Delayed treatment increases mortality.",
            "recovery_time": "1-3 weeks for full recovery"
        },
        {
            "name": "Paracetamol Overdose",
            "category": PoisonCategory.PHARMACEUTICAL,
            "common_names": ["Acetaminophen", "Tylenol", "Crocin", "Panadol", "APAP"],
            "common_sources": ["Over-the-counter painkillers", "Fever medications", "Combination cold medicines"],
            "symptoms_immediate": ["Nausea", "Vomiting", "Abdominal pain", "Anorexia", "Pallor"],
            "symptoms_delayed": ["Right upper quadrant pain (24-72h)", "Jaundice", "Liver failure", "Hepatic encephalopathy", "Coagulopathy"],
            "typical_severity": SeverityLevel.MODERATE,
            "antidote": "N-Acetylcysteine (NAC)",
            "antidote_alternatives": ["Methionine (oral, if NAC unavailable)"],
            "antidote_dosage": "NAC: 150mg/kg IV over 1h, then 50mg/kg over 4h, then 100mg/kg over 16h (21-hour protocol)",
            "first_aid": "1. Do not induce vomiting\n2. Activated charcoal if within 1-2 hours\n3. Note time and amount ingested\n4. Seek immediate medical care",
            "decontamination": "Activated charcoal 1g/kg if within 1-2 hours of ingestion",
            "management_protocol": "1. Check paracetamol level at 4h post-ingestion\n2. Plot on Rumack-Matthew nomogram\n3. Start NAC if above treatment line\n4. Monitor LFTs, INR, creatinine\n5. Consider liver transplant if fulminant failure",
            "supportive_care": "IV fluids, antiemetics, monitor for liver failure, correct coagulopathy with FFP/Vitamin K",
            "contraindications": "Do NOT delay NAC if level unavailable and large ingestion suspected",
            "tests_required": ["Paracetamol level at 4h", "LFTs (AST, ALT)", "INR/PT", "Creatinine", "Blood glucose"],
            "monitoring_parameters": ["Liver function tests", "INR", "Mental status", "Blood glucose"],
            "data_sources": [
                {"source": "Rumack-Matthew Nomogram", "type": "medical_standard"},
                {"source": "NPIC Nepal Treatment Guidelines", "type": "government"}
            ],
            "prognosis": "Excellent if NAC given within 8 hours. Worse with delayed treatment.",
            "recovery_time": "3-5 days if treated early; weeks if hepatotoxicity develops"
        },
        {
            "name": "Rat Poison (Anticoagulant)",
            "category": PoisonCategory.HOUSEHOLD,
            "common_names": ["Warfarin", "Brodifacoum", "Bromadiolone", "Superwarfarins", "Ratol"],
            "common_sources": ["Rodenticides", "Pest control products", "Industrial rat poison"],
            "symptoms_immediate": ["Usually none for 24-48 hours"],
            "symptoms_delayed": ["Bleeding gums", "Bruising", "Hematuria", "Epistaxis", "Melena", "Hemoptysis", "Intracranial hemorrhage"],
            "typical_severity": SeverityLevel.SEVERE,
            "antidote": "Vitamin K1 (Phytonadione)",
            "antidote_alternatives": ["Fresh Frozen Plasma (FFP) for active bleeding", "Prothrombin Complex Concentrate (PCC)"],
            "antidote_dosage": "Vitamin K1: 10-25mg oral/IV. May need for weeks to months for superwarfarins.",
            "first_aid": "1. Do not induce vomiting\n2. Note product name and amount\n3. Seek medical attention\n4. Watch for bleeding signs over 24-72 hours",
            "decontamination": "Activated charcoal if within 1 hour",
            "management_protocol": "1. Check INR at 24, 48, 72 hours\n2. Vitamin K1 if INR elevated\n3. FFP or PCC for active bleeding\n4. Continue Vitamin K1 for weeks-months (superwarfarins)",
            "supportive_care": "Blood transfusion if severe bleeding, avoid trauma, monitor for occult bleeding",
            "contraindications": "Avoid aspirin, NSAIDs, and other anticoagulants. No IM injections.",
            "tests_required": ["INR/PT (serial)", "CBC", "Type and screen"],
            "monitoring_parameters": ["INR", "Signs of bleeding", "Hemoglobin"],
            "data_sources": [
                {"source": "Toxicology Reference Guidelines", "type": "medical"},
                {"source": "NPIC Nepal", "type": "government"}
            ],
            "prognosis": "Excellent with appropriate Vitamin K therapy",
            "recovery_time": "Weeks to months for superwarfarins"
        },
        {
            "name": "Snake Venom (Neurotoxic)",
            "category": PoisonCategory.NATURAL,
            "common_names": ["Cobra venom", "Krait venom", "Elapid venom", "Naja naja", "Bungarus"],
            "common_sources": ["Snake bites - Cobra", "Snake bites - Krait", "Common in Nepal Terai region"],
            "symptoms_immediate": ["Local pain", "Swelling", "Fang marks", "Anxiety"],
            "symptoms_delayed": ["Ptosis (drooping eyelids)", "Dysphagia", "Dysarthria", "Respiratory paralysis", "Bulbar palsy"],
            "typical_severity": SeverityLevel.CRITICAL,
            "antidote": "Polyvalent Anti-Snake Venom (ASV)",
            "antidote_alternatives": ["Neostigmine for neurotoxic envenomation (adjunct)"],
            "antidote_dosage": "ASV: 10 vials (100ml) IV in NS, may repeat based on response. Watch for anaphylaxis.",
            "first_aid": "1. Keep patient calm and immobile\n2. Immobilize bitten limb below heart level\n3. Remove jewelry/tight clothing\n4. Do NOT cut, suck, or apply tourniquet\n5. Transport immediately to hospital",
            "decontamination": "Not applicable - venom already in tissue",
            "management_protocol": "1. Assess for envenomation signs\n2. ASV early if systemic signs\n3. Premedicate with adrenaline/antihistamines\n4. Neostigmine trial for neurotoxic signs\n5. Ventilatory support if respiratory failure",
            "supportive_care": "Airway management, mechanical ventilation, wound care, tetanus prophylaxis",
            "contraindications": "Do NOT apply tourniquet, cut wound, apply ice, or give oral medications if vomiting",
            "tests_required": ["20-minute whole blood clotting test (20WBCT)", "CBC", "PT/INR", "Creatinine"],
            "monitoring_parameters": ["Respiratory function", "Ptosis progression", "20WBCT", "Urine output"],
            "data_sources": [
                {"source": "WHO Guidelines for Snake Bite Management", "type": "international"},
                {"source": "BPKIHS Snake Bite Protocol", "type": "nepal_medical"},
                {"source": "Nepal Ministry of Health Guidelines", "type": "government"}
            ],
            "prognosis": "Good if ASV given early. Mortality increases with delayed treatment.",
            "recovery_time": "Days to weeks depending on severity"
        },
        {
            "name": "Oleander",
            "category": PoisonCategory.NATURAL,
            "common_names": ["Nerium oleander", "Kaner", "Arali", "Yellow oleander", "Thevetia"],
            "common_sources": ["Ornamental plant ingestion", "Herbal preparations", "Intentional ingestion"],
            "symptoms_immediate": ["Nausea", "Vomiting", "Abdominal pain", "Diarrhea"],
            "symptoms_delayed": ["Bradycardia", "Heart block", "Arrhythmias", "Hyperkalemia", "Visual disturbances"],
            "typical_severity": SeverityLevel.SEVERE,
            "antidote": "Digoxin-specific Fab fragments (DigiFab)",
            "antidote_alternatives": ["Atropine for bradycardia", "Temporary pacing"],
            "antidote_dosage": "DigiFab: Dose based on estimated digoxin equivalents or empirically 10-20 vials",
            "first_aid": "1. Do not induce vomiting\n2. Call Poison Control\n3. Note plant and amount ingested\n4. Seek immediate cardiac monitoring",
            "decontamination": "Multiple-dose activated charcoal may be helpful",
            "management_protocol": "1. Continuous cardiac monitoring\n2. Correct hyperkalemia\n3. DigiFab for significant arrhythmias\n4. Atropine for bradycardia\n5. Temporary pacing if needed",
            "supportive_care": "Cardiac monitoring, electrolyte correction, avoid calcium for hyperkalemia",
            "contraindications": "Avoid calcium chloride/gluconate for hyperkalemia (may worsen cardiac toxicity)",
            "tests_required": ["ECG", "Potassium", "Digoxin level (may be elevated)", "Magnesium"],
            "monitoring_parameters": ["Cardiac rhythm", "Potassium levels", "Heart rate"],
            "data_sources": [
                {"source": "Clinical Toxicology Guidelines", "type": "medical"},
                {"source": "Cardiac glycoside poisoning literature", "type": "research"}
            ],
            "prognosis": "Variable. Can be fatal without treatment.",
            "recovery_time": "1-3 days with appropriate treatment"
        },
        {
            "name": "Corrosive Acid",
            "category": PoisonCategory.INDUSTRIAL,
            "common_names": ["Sulfuric Acid", "Battery Acid", "Hydrochloric Acid", "Toilet Cleaner", "Drain Cleaner"],
            "common_sources": ["Toilet cleaners", "Battery acid", "Industrial chemicals", "Drain cleaners"],
            "symptoms_immediate": ["Severe burning pain", "Oral burns", "Drooling", "Dysphagia", "Stridor"],
            "symptoms_delayed": ["Dysphagia", "Hematemesis", "Esophageal perforation", "Esophageal stricture", "Mediastinitis"],
            "typical_severity": SeverityLevel.CRITICAL,
            "antidote": "No specific antidote - supportive care",
            "antidote_alternatives": [],
            "antidote_dosage": "Not applicable",
            "first_aid": "1. Do NOT induce vomiting\n2. Do NOT give activated charcoal\n3. Small sips of water/milk to dilute (controversial)\n4. Immediate hospital transport\n5. Protect airway",
            "decontamination": "External: copious water irrigation. Internal: do NOT neutralize or dilute extensively",
            "management_protocol": "1. Secure airway early\n2. NPO\n3. IV fluids\n4. Endoscopy within 24 hours to assess damage\n5. Surgery if perforation suspected",
            "supportive_care": "Pain management, PPI therapy, nutritional support, stricture prevention",
            "contraindications": "Do NOT induce vomiting. Do NOT give neutralizing agents. Do NOT use NG tube blindly.",
            "tests_required": ["Chest/Abdominal X-ray", "Endoscopy", "CBC", "Electrolytes"],
            "monitoring_parameters": ["Airway patency", "Signs of perforation", "Hemodynamic stability"],
            "data_sources": [
                {"source": "Emergency Medicine Guidelines", "type": "medical"},
                {"source": "GI Toxicology References", "type": "medical"}
            ],
            "prognosis": "Depends on extent of injury. Strictures common.",
            "recovery_time": "Weeks to months; may need multiple dilations"
        },
        {
            "name": "Alcohol (Ethanol)",
            "category": PoisonCategory.SUBSTANCE_ABUSE,
            "common_names": ["Ethanol", "Alcohol", "Liquor", "Beer", "Wine", "Spirits"],
            "common_sources": ["Alcoholic beverages", "Hand sanitizers", "Mouthwash"],
            "symptoms_immediate": ["Confusion", "Slurred speech", "Ataxia", "Nystagmus"],
            "symptoms_delayed": ["Respiratory depression", "Aspiration", "Hypoglycemia", "Hypothermia", "Coma"],
            "typical_severity": SeverityLevel.MODERATE,
            "antidote": "No specific antidote - supportive care",
            "antidote_alternatives": ["Thiamine for chronic alcoholics", "Glucose for hypoglycemia"],
            "antidote_dosage": "Thiamine 100mg IV before glucose",
            "first_aid": "1. Place in recovery position\n2. Monitor breathing\n3. Keep warm\n4. Do NOT leave alone\n5. Seek medical help if unresponsive",
            "decontamination": "Generally not indicated",
            "management_protocol": "1. Protect airway\n2. Check blood glucose\n3. Thiamine before glucose\n4. IV fluids\n5. Monitor for withdrawal",
            "supportive_care": "Warming, IV fluids, electrolyte correction, aspiration precautions",
            "contraindications": "Do NOT give glucose before thiamine in chronic alcoholics (risk of Wernicke's)",
            "tests_required": ["Blood glucose", "Blood alcohol level", "Electrolytes", "Osmolar gap"],
            "monitoring_parameters": ["Level of consciousness", "Respiratory rate", "Blood glucose"],
            "data_sources": [
                {"source": "Emergency Medicine Protocols", "type": "medical"},
                {"source": "Addiction Medicine Guidelines", "type": "medical"}
            ],
            "prognosis": "Generally good with supportive care",
            "recovery_time": "Hours to days"
        },
        {
            "name": "Methanol",
            "category": PoisonCategory.INDUSTRIAL,
            "common_names": ["Wood Alcohol", "Spurious Liquor", "Methylated spirit", "Industrial alcohol"],
            "common_sources": ["Illicit alcohol", "Antifreeze", "Industrial solvents", "Windshield washer fluid"],
            "symptoms_immediate": ["Nausea", "Headache", "Inebriation similar to ethanol"],
            "symptoms_delayed": ["Visual disturbances", "Blindness", "Metabolic acidosis", "Seizures", "Coma"],
            "typical_severity": SeverityLevel.CRITICAL,
            "antidote": "Fomepizole or Ethanol",
            "antidote_alternatives": ["Ethanol if Fomepizole unavailable"],
            "antidote_dosage": "Fomepizole: 15mg/kg loading, then 10mg/kg q12h. Ethanol: target blood level 100-150mg/dL",
            "first_aid": "1. Call emergency services immediately\n2. Do not induce vomiting\n3. If ethanol available, it may be given\n4. Note time and amount ingested",
            "decontamination": "Gastric lavage if <1 hour",
            "management_protocol": "1. Fomepizole or Ethanol to block ADH\n2. Hemodialysis for severe cases (pH <7.25, visual symptoms, renal failure)\n3. Folinic acid\n4. Correct acidosis with bicarbonate",
            "supportive_care": "ICU care, seizure management, ophthalmology consult",
            "contraindications": "Do NOT delay treatment waiting for methanol level",
            "tests_required": ["Methanol level", "ABG", "Osmolar gap", "Anion gap", "Formate level if available"],
            "monitoring_parameters": ["pH", "Visual acuity", "Osmolar gap", "Methanol level"],
            "data_sources": [
                {"source": "Toxicology Emergency Guidelines", "type": "medical"},
                {"source": "Methanol Poisoning Protocols", "type": "medical"}
            ],
            "prognosis": "Can be fatal. Blindness permanent if treatment delayed.",
            "recovery_time": "Days with dialysis; visual damage may be permanent"
        },
        {
            "name": "Kerosene/Petroleum",
            "category": PoisonCategory.HOUSEHOLD,
            "common_names": ["Kerosene", "Paraffin", "Petrol", "Diesel", "Turpentine"],
            "common_sources": ["Fuel storage", "Lamps", "Cleaning solvents", "Accidental ingestion by children"],
            "symptoms_immediate": ["Coughing", "Choking", "Burning sensation", "Nausea"],
            "symptoms_delayed": ["Chemical pneumonitis", "Respiratory distress", "CNS depression", "Cardiac arrhythmias"],
            "typical_severity": SeverityLevel.MODERATE,
            "antidote": "No specific antidote - supportive care",
            "antidote_alternatives": [],
            "antidote_dosage": "Not applicable",
            "first_aid": "1. Do NOT induce vomiting (aspiration risk)\n2. Keep calm\n3. Remove from fumes\n4. Do not give anything by mouth\n5. Seek medical attention",
            "decontamination": "External: wash skin with soap and water. Do NOT perform gastric lavage (aspiration risk).",
            "management_protocol": "1. Observe for respiratory symptoms\n2. Chest X-ray at 4-6 hours\n3. Oxygen if needed\n4. Bronchodilators for bronchospasm\n5. No prophylactic antibiotics or steroids",
            "supportive_care": "Respiratory support, observation for pneumonitis",
            "contraindications": "Do NOT induce vomiting. Do NOT perform gastric lavage. No activated charcoal.",
            "tests_required": ["Chest X-ray", "Pulse oximetry", "ABG if symptomatic"],
            "monitoring_parameters": ["Respiratory rate", "Oxygen saturation", "Chest symptoms"],
            "data_sources": [
                {"source": "Pediatric Toxicology Guidelines", "type": "medical"},
                {"source": "Hydrocarbon Poisoning Protocols", "type": "medical"}
            ],
            "prognosis": "Good if no aspiration. Chemical pneumonitis may develop.",
            "recovery_time": "Days to weeks if pneumonitis develops"
        },
        {
            "name": "Mushroom Poisoning (Amatoxin)",
            "category": PoisonCategory.NATURAL,
            "common_names": ["Death Cap", "Destroying Angel", "Amanita phalloides", "Wild mushroom"],
            "common_sources": ["Wild mushroom foraging", "Misidentified edible mushrooms"],
            "symptoms_immediate": ["Delayed onset 6-12 hours", "Then severe GI symptoms"],
            "symptoms_delayed": ["Profuse diarrhea", "Vomiting", "Hepatic failure", "Renal failure", "Coagulopathy"],
            "typical_severity": SeverityLevel.CRITICAL,
            "antidote": "Silibinin (Milk Thistle) + N-Acetylcysteine",
            "antidote_alternatives": ["Penicillin G (high dose)", "NAC"],
            "antidote_dosage": "Silibinin: 20-50mg/kg/day IV. NAC: 150mg/kg protocol.",
            "first_aid": "1. Seek immediate medical attention\n2. Bring sample of mushroom if possible\n3. Note time of ingestion\n4. Do not rely on home remedies",
            "decontamination": "Multiple-dose activated charcoal",
            "management_protocol": "1. Aggressive IV fluids\n2. Multiple-dose activated charcoal\n3. Silibinin + NAC\n4. Monitor for liver failure\n5. Consider liver transplant if fulminant failure",
            "supportive_care": "ICU care, correction of coagulopathy, liver transplant evaluation",
            "contraindications": "Do NOT delay treatment based on initial mild symptoms",
            "tests_required": ["LFTs (serial)", "INR", "Creatinine", "Blood glucose", "Ammonia"],
            "monitoring_parameters": ["Liver function", "INR", "Mental status", "Urine output"],
            "data_sources": [
                {"source": "Mycotoxin Poisoning Guidelines", "type": "medical"},
                {"source": "Amatoxin Poisoning Research", "type": "research"}
            ],
            "prognosis": "30-50% mortality without liver transplant in severe cases",
            "recovery_time": "Weeks; may need liver transplant"
        }
    ]
    
    for poison_data in poisons_data:
        existing = db.query(Poison).filter(
            Poison.name == poison_data["name"]
        ).first()
        if not existing:
            poison = Poison(**poison_data)
            db.add(poison)
    
    db.commit()
    print(f"✅ Seeded {len(poisons_data)} common poisons")

def seed_antidote_inventory(db: Session):
    """Seed antidote inventory for hospitals"""
    hospitals = db.query(Hospital).all()
    
    antidotes = [
        {"name": "Atropine Sulfate", "generic": "Atropine", "for": ["Organophosphate", "Carbamate"]},
        {"name": "Pralidoxime (2-PAM)", "generic": "Pralidoxime", "for": ["Organophosphate"]},
        {"name": "N-Acetylcysteine (NAC)", "generic": "Acetylcysteine", "for": ["Paracetamol"]},
        {"name": "Polyvalent ASV", "generic": "Anti-Snake Venom", "for": ["Snake Envenomation"]},
        {"name": "Naloxone", "generic": "Naloxone", "for": ["Opioid Overdose"]},
        {"name": "Vitamin K1", "generic": "Phytonadione", "for": ["Anticoagulant Rodenticide"]},
        {"name": "Activated Charcoal", "generic": "Charcoal", "for": ["General Decontamination"]},
    ]
    
    for hospital in hospitals[:3]:  # Add to first 3 hospitals
        for antidote in antidotes:
            existing = db.query(AntidoteInventory).filter(
                AntidoteInventory.hospital_id == hospital.id,
                AntidoteInventory.antidote_name == antidote["name"]
            ).first()
            if not existing:
                inventory = AntidoteInventory(
                    hospital_id=hospital.id,
                    antidote_name=antidote["name"],
                    generic_name=antidote["generic"],
                    effective_for=antidote["for"],
                    quantity_available=100,
                    is_available=True
                )
                db.add(inventory)
    
    db.commit()
    print("✅ Seeded antidote inventory")

def seed_ai_model_version(db: Session):
    """Record AI model version"""
    existing = db.query(AIModelVersion).filter(
        AIModelVersion.version == "1.0.0"
    ).first()
    
    if not existing:
        model = AIModelVersion(
            version="1.0.0",
            model_type="DistilBERT",
            notes="DistilBERT fine-tuned for poison classification from symptoms",
            accuracy=0.85,
            precision=0.84,
            recall=0.86,
            f1_score=0.85,
            training_data_size=1200,
            is_active=True
        )
        db.add(model)
        db.commit()
        print("✅ AI model version recorded")

def init_database():
    """Initialize database with tables and seed data"""
    print("\n🚀 Initializing PoisonSense-AI Database...\n")
    
    # Create tables
    create_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_admin_user(db)
        seed_poison_centers(db)
        seed_hospitals(db)
        seed_poisons(db)
        seed_antidote_inventory(db)
        seed_ai_model_version(db)
        
        print("\n✅ Database initialization complete!")
        print("=" * 50)
        print("Admin Login: admin@poisonsense.ai / admin123")
        print("API Docs: http://localhost:8000/docs")
        print("=" * 50)
        
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
