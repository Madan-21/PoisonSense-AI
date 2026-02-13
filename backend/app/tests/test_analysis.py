# Tests for PoisonSense ML analysis pipeline
import pytest
import sys
import os

# Add backend to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.ml.preprocess import (
    clean_text,
    normalize_symptoms,
    extract_symptoms_list,
    detect_suspected_poison,
    build_model_input,
)
from app.ml.evaluate import compute_severity_from_confidence


# ===========================
# Preprocessing Tests
# ===========================

class TestCleanText:
    """Tests for text cleaning function"""

    def test_basic_cleaning(self):
        assert clean_text("  Headache, Nausea  ") == "headache, nausea"

    def test_removes_special_chars(self):
        result = clean_text("vomiting!! and dizziness??")
        assert "!" not in result
        assert "?" not in result

    def test_preserves_commas(self):
        result = clean_text("headache, nausea, vomiting")
        assert result.count(",") == 2

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_none_input(self):
        assert clean_text(None) == ""

    def test_collapses_whitespace(self):
        result = clean_text("headache    and    nausea")
        assert "    " not in result


class TestNormalizeSymptoms:
    """Tests for symptom normalization"""

    def test_synonym_replacement(self):
        result = normalize_symptoms("throwing up and dizzy")
        assert "vomiting" in result
        assert "dizziness" in result

    def test_belly_pain_to_abdominal(self):
        result = normalize_symptoms("belly pain and tired")
        assert "abdominal pain" in result
        assert "fatigue" in result

    def test_breathing_difficulty(self):
        result = normalize_symptoms("can't breathe properly")
        assert "shortness of breath" in result

    def test_already_medical_terms(self):
        result = normalize_symptoms("nausea, vomiting, diarrhea")
        assert "nausea" in result
        assert "vomiting" in result
        assert "diarrhea" in result

    def test_mixed_informal_formal(self):
        result = normalize_symptoms("throwing up, headache, tired")
        assert "vomiting" in result
        assert "headache" in result
        assert "fatigue" in result


class TestExtractSymptomsList:
    """Tests for symptom extraction"""

    def test_comma_separated(self):
        result = extract_symptoms_list("headache, nausea, vomiting")
        assert len(result) == 3

    def test_and_separated(self):
        result = extract_symptoms_list("headache and nausea and vomiting")
        assert len(result) == 3

    def test_semicolon_separated(self):
        result = extract_symptoms_list("headache; nausea; vomiting")
        assert len(result) == 3

    def test_normalizes_during_extraction(self):
        result = extract_symptoms_list("throwing up, dizzy, belly pain")
        assert "vomiting" in result
        assert "dizziness" in result
        assert "abdominal pain" in result

    def test_empty_input(self):
        result = extract_symptoms_list("")
        assert result == []


class TestDetectSuspectedPoison:
    """Tests for suspected poison detection from text"""

    def test_detects_rat_poison(self):
        result = detect_suspected_poison("I think I ate rat poison")
        assert result == "Arsenic"

    def test_detects_pesticide(self):
        result = detect_suspected_poison("drank pesticide by accident")
        assert result == "Organophosphate"

    def test_detects_paracetamol(self):
        result = detect_suspected_poison("took too much paracetamol")
        assert result == "Acetaminophen"

    def test_no_poison_mentioned(self):
        result = detect_suspected_poison("having headache and vomiting")
        assert result is None

    def test_case_insensitive(self):
        result = detect_suspected_poison("Drank BLEACH by mistake")
        assert result == "Household Chemical"


class TestBuildModelInput:
    """Tests for the full preprocessing pipeline"""

    def test_returns_all_keys(self):
        result = build_model_input("throwing up and dizzy after eating rat poison")
        assert "model_input" in result
        assert "symptoms_list" in result
        assert "suspected_poison" in result
        assert "original_text" in result

    def test_detects_poison_in_pipeline(self):
        result = build_model_input("took too much paracetamol, feeling sick")
        assert result["suspected_poison"] == "Acetaminophen"

    def test_normalizes_in_pipeline(self):
        result = build_model_input("belly pain and throwing up")
        assert "abdominal pain" in result["model_input"]
        assert "vomiting" in result["model_input"]


# ===========================
# Evaluation Utility Tests
# ===========================

class TestSeverityMapping:
    """Tests for confidence-to-severity mapping"""

    def test_high_confidence(self):
        assert compute_severity_from_confidence(0.92) == "high"

    def test_moderate_confidence(self):
        assert compute_severity_from_confidence(0.70) == "moderate"

    def test_low_confidence(self):
        assert compute_severity_from_confidence(0.40) == "low"

    def test_uncertain_confidence(self):
        assert compute_severity_from_confidence(0.20) == "uncertain"

    def test_boundary_high(self):
        assert compute_severity_from_confidence(0.85) == "high"

    def test_boundary_moderate(self):
        assert compute_severity_from_confidence(0.60) == "moderate"

    def test_boundary_low(self):
        assert compute_severity_from_confidence(0.35) == "low"
