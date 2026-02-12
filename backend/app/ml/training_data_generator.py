# Enhanced Training Data Generator
# Generates comprehensive training dataset from real toxicology data

import pandas as pd
import numpy as np
import random
import uuid
import json
from typing import List, Dict, Tuple
from pathlib import Path
import os

# Import comprehensive toxicology data
from app.ml.data.comprehensive_toxicology_data import (
    COMPREHENSIVE_POISONS,
    SYMPTOM_POISON_MAPPING,
    EMERGENCY_NUMBERS
)


class ToxicologyDatasetGenerator:
    """
    Generates training dataset for poison classification model
    using comprehensive real medical data.
    """
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.dirname(os.path.abspath(__file__))
        self.poisons = COMPREHENSIVE_POISONS
        self.symptom_mapping = SYMPTOM_POISON_MAPPING
        
    def _get_symptom_variations(self, symptoms: List[str]) -> List[str]:
        """Generate natural language variations of symptoms"""
        variations = []
        
        # Patient description templates
        templates = [
            "Patient presents with {}",
            "Symptoms include {}",
            "The person is experiencing {}",
            "Complaining of {}",
            "Observed symptoms: {}",
            "Patient has {}",
            "Signs noted: {}",
            "Currently showing {}",
            "{} reported",
            "Suffering from {}"
        ]
        
        # Create different combinations
        for i in range(min(len(templates), 10)):
            num_symptoms = random.randint(2, min(5, len(symptoms)))
            selected = random.sample(symptoms, num_symptoms)
            
            # Join symptoms naturally
            if len(selected) == 1:
                symptom_text = selected[0]
            elif len(selected) == 2:
                symptom_text = f"{selected[0]} and {selected[1]}"
            else:
                symptom_text = ", ".join(selected[:-1]) + f", and {selected[-1]}"
            
            template = random.choice(templates)
            variations.append(template.format(symptom_text))
        
        return variations
    
    def _generate_clinical_scenarios(self, poison_data: Dict) -> List[str]:
        """Generate realistic clinical scenario descriptions"""
        scenarios = []
        
        poison_name = poison_data.get("name", "Unknown")
        common_names = poison_data.get("common_names", [])
        common_sources = poison_data.get("common_sources", [])
        immediate_symptoms = poison_data.get("symptoms_immediate", [])
        delayed_symptoms = poison_data.get("symptoms_delayed", [])
        
        # Combine all symptoms
        all_symptoms = immediate_symptoms + delayed_symptoms
        
        # Scenario templates
        scenario_templates = [
            # Exposure scenarios
            "Patient exposed to {source}, now showing {symptoms}",
            "After contact with {source}, patient developed {symptoms}",
            "Child accidentally ingested {substance}, presenting with {symptoms}",
            "Worker exposed to {source} at workplace, symptoms: {symptoms}",
            "Adult consumed {substance}, complaining of {symptoms}",
            "Suicide attempt with {substance}, patient has {symptoms}",
            
            # Time-based scenarios
            "2 hours ago ingested {substance}, now experiencing {symptoms}",
            "Found unconscious near {source}, showing {symptoms}",
            "Gradually developing {symptoms} after exposure to {source}",
            
            # Symptom-focused scenarios
            "Emergency case with {symptoms} after suspected {substance} exposure",
            "Critical patient: {symptoms}. History of {source} contact",
            "Severe poisoning suspected: {symptoms}",
            
            # Context scenarios
            "Agricultural worker with {symptoms} after spraying",
            "Child with {symptoms} after playing near {source}",
            "Patient from rural area presenting with {symptoms}",
        ]
        
        for _ in range(20):
            template = random.choice(scenario_templates)
            
            # Select random symptoms
            num_symptoms = random.randint(2, min(5, len(all_symptoms)))
            selected_symptoms = random.sample(all_symptoms, num_symptoms)
            
            if len(selected_symptoms) == 1:
                symptoms_text = selected_symptoms[0]
            elif len(selected_symptoms) == 2:
                symptoms_text = f"{selected_symptoms[0]} and {selected_symptoms[1]}"
            else:
                symptoms_text = ", ".join(selected_symptoms[:-1]) + f", and {selected_symptoms[-1]}"
            
            # Select source/substance
            substance = random.choice(common_names) if common_names else poison_name
            source = random.choice(common_sources) if common_sources else substance
            
            try:
                scenario = template.format(
                    symptoms=symptoms_text,
                    substance=substance,
                    source=source
                )
                scenarios.append(scenario)
            except KeyError:
                continue
        
        return scenarios
    
    def _generate_symptom_combinations(self, symptoms: List[str], n_samples: int) -> List[str]:
        """Generate various symptom combinations"""
        combinations = []
        
        for _ in range(n_samples):
            num_symptoms = random.randint(2, min(6, len(symptoms)))
            selected = random.sample(symptoms, num_symptoms)
            combinations.append(", ".join(selected))
        
        return combinations
    
    def generate_dataset(self, samples_per_poison: int = 200, include_scenarios: bool = True) -> pd.DataFrame:
        """
        Generate comprehensive training dataset
        
        Args:
            samples_per_poison: Number of samples per poison type
            include_scenarios: Include clinical scenario descriptions
            
        Returns:
            DataFrame with training data
        """
        records = []
        
        for poison_id, poison_data in self.poisons.items():
            poison_name = poison_data.get("name", poison_id)
            category = poison_data.get("category", "unknown")
            antidote = poison_data.get("antidote", {})
            
            # Get antidote name
            if isinstance(antidote, dict):
                antidote_name = antidote.get("primary", "Supportive care")
            else:
                antidote_name = antidote or "Supportive care"
            
            # Collect all symptoms
            immediate_symptoms = poison_data.get("symptoms_immediate", [])
            delayed_symptoms = poison_data.get("symptoms_delayed", [])
            
            # Handle nested structures (like cholinergic_toxidrome)
            if "cholinergic_toxidrome" in poison_data:
                for key, syms in poison_data["cholinergic_toxidrome"].items():
                    immediate_symptoms.extend(syms)
            
            all_symptoms = list(set(immediate_symptoms + delayed_symptoms))
            
            if not all_symptoms:
                continue
            
            # Management protocol
            protocol = poison_data.get("management_protocol", [])
            if isinstance(protocol, list):
                protocol_text = " | ".join(protocol[:3])
            else:
                protocol_text = protocol
            
            # First aid
            first_aid = poison_data.get("first_aid", [])
            if isinstance(first_aid, list):
                first_aid_text = " | ".join(first_aid[:3])
            else:
                first_aid_text = first_aid
            
            # Data sources
            sources = poison_data.get("data_sources", [])
            source_names = [s.get("name", "Unknown") for s in sources] if sources else ["Medical Literature"]
            
            # Generate samples
            samples_generated = 0
            
            # 1. Direct symptom combinations
            symptom_combos = self._generate_symptom_combinations(all_symptoms, samples_per_poison // 2)
            for combo in symptom_combos:
                record = {
                    "case_id": str(uuid.uuid4()),
                    "poison_name": poison_name,
                    "poison_id": poison_id,
                    "poison_category": category,
                    "antidote": antidote_name,
                    "symptoms": combo,
                    "management_protocol": protocol_text,
                    "first_aid": first_aid_text,
                    "severity_level": poison_data.get("typical_severity", "moderate"),
                    "data_source": random.choice(source_names),
                    "input_text": combo
                }
                records.append(record)
                samples_generated += 1
            
            # 2. Symptom variations (natural language)
            variations = self._get_symptom_variations(all_symptoms)
            for var in variations:
                record = {
                    "case_id": str(uuid.uuid4()),
                    "poison_name": poison_name,
                    "poison_id": poison_id,
                    "poison_category": category,
                    "antidote": antidote_name,
                    "symptoms": var,
                    "management_protocol": protocol_text,
                    "first_aid": first_aid_text,
                    "severity_level": poison_data.get("typical_severity", "moderate"),
                    "data_source": random.choice(source_names),
                    "input_text": var
                }
                records.append(record)
                samples_generated += 1
            
            # 3. Clinical scenarios
            if include_scenarios:
                scenarios = self._generate_clinical_scenarios(poison_data)
                for scenario in scenarios:
                    record = {
                        "case_id": str(uuid.uuid4()),
                        "poison_name": poison_name,
                        "poison_id": poison_id,
                        "poison_category": category,
                        "antidote": antidote_name,
                        "symptoms": scenario,
                        "management_protocol": protocol_text,
                        "first_aid": first_aid_text,
                        "severity_level": poison_data.get("typical_severity", "moderate"),
                        "data_source": random.choice(source_names),
                        "input_text": scenario
                    }
                    records.append(record)
                    samples_generated += 1
            
            # 4. Fill remaining with random combinations
            while samples_generated < samples_per_poison:
                num_symptoms = random.randint(2, min(5, len(all_symptoms)))
                selected = random.sample(all_symptoms, num_symptoms)
                symptoms_text = ", ".join(selected)
                
                record = {
                    "case_id": str(uuid.uuid4()),
                    "poison_name": poison_name,
                    "poison_id": poison_id,
                    "poison_category": category,
                    "antidote": antidote_name,
                    "symptoms": symptoms_text,
                    "management_protocol": protocol_text,
                    "first_aid": first_aid_text,
                    "severity_level": poison_data.get("typical_severity", "moderate"),
                    "data_source": random.choice(source_names),
                    "input_text": symptoms_text
                }
                records.append(record)
                samples_generated += 1
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Shuffle
        df = df.sample(frac=1).reset_index(drop=True)
        
        return df
    
    def generate_and_save(
        self, 
        samples_per_poison: int = 200,
        output_filename: str = "comprehensive_poison_dataset.csv"
    ) -> str:
        """Generate dataset and save to CSV"""
        df = self.generate_dataset(samples_per_poison)
        
        output_path = os.path.join(self.output_dir, output_filename)
        df.to_csv(output_path, index=False)
        
        print(f"✅ Dataset generated: {len(df)} samples")
        print(f"✅ Poison types: {df['poison_name'].nunique()}")
        print(f"✅ Saved to: {output_path}")
        
        return output_path
    
    def generate_symptom_only_dataset(self, samples_per_poison: int = 100) -> pd.DataFrame:
        """Generate dataset with only symptoms (for focused training)"""
        records = []
        
        for poison_id, poison_data in self.poisons.items():
            poison_name = poison_data.get("name", poison_id)
            
            immediate_symptoms = poison_data.get("symptoms_immediate", [])
            delayed_symptoms = poison_data.get("symptoms_delayed", [])
            
            if "cholinergic_toxidrome" in poison_data:
                for key, syms in poison_data["cholinergic_toxidrome"].items():
                    immediate_symptoms.extend(syms)
            
            all_symptoms = list(set(immediate_symptoms + delayed_symptoms))
            
            if not all_symptoms:
                continue
            
            for _ in range(samples_per_poison):
                num_symptoms = random.randint(2, min(5, len(all_symptoms)))
                selected = random.sample(all_symptoms, num_symptoms)
                
                records.append({
                    "input_text": ", ".join(selected),
                    "poison_name": poison_name,
                    "poison_id": poison_id
                })
        
        df = pd.DataFrame(records)
        return df.sample(frac=1).reset_index(drop=True)


def generate_training_data(output_dir: str = None, samples_per_poison: int = 200) -> str:
    """Convenience function to generate training data"""
    generator = ToxicologyDatasetGenerator(output_dir)
    return generator.generate_and_save(samples_per_poison)


if __name__ == "__main__":
    # Generate dataset
    generator = ToxicologyDatasetGenerator()
    output_path = generator.generate_and_save(samples_per_poison=200)
    
    # Print sample
    df = pd.read_csv(output_path)
    print("\nSample records:")
    print(df.head(10).to_string())
    print(f"\nDataset shape: {df.shape}")
    print(f"\nPoison distribution:\n{df['poison_name'].value_counts()}")
