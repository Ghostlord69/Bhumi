"""Unit tests for ULPIN-first field cascade (no OCR engines required)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from extract import extract_fields, normalize_ulpin
from ocr import OcrLine


def test_normalize_ulpin():
    assert normalize_ulpin("HR06A1B2C3D4E5") == "HR06A1B2C3D4E5"
    assert normalize_ulpin("hr06a1b2c3d4e5") == "HR06A1B2C3D4E5"
    assert normalize_ulpin("short") is None


def test_meta_ulpin_first():
    meta = (
        "BHUMI_META|ULPIN:HR06A1B2C3D4E5|KHASRA:123/4|KHATA:45|KHEWAT:12|KHATAUNI:3|"
        "OWNER:Ramesh Kumar|VILLAGE:Sihi|CITY:Ballabgarh|DISTRICT:Faridabad|"
        "STATE:Haryana|AREA:2.5 acres|TYPE:AGRICULTURAL"
    )
    result = extract_fields([OcrLine(text=meta, score=0.99)])
    assert result["ulpin"] == "HR06A1B2C3D4E5"
    assert result["khasraNumber"] == "123/4"
    assert result["khataNumber"] == "45"
    assert result["khewatNumber"] == "12"
    assert result["khatauniNumber"] == "3"
    assert result["matchTier"] == "ULPIN"
    assert result["parcelIdType"] == "ULPIN"
    assert result["confidence"] >= 0.90


def test_keyword_ulpin_without_full_jamabandi():
    lines = [
        OcrLine(text="Government of Haryana Land Record", score=0.9),
        OcrLine(text="ULPIN (Bhu-Aadhaar): HR06F6G7H8I9J0", score=0.88),
        OcrLine(text="Village Sihi", score=0.8),
    ]
    result = extract_fields(lines)
    assert result["ulpin"] == "HR06F6G7H8I9J0"
    assert result["matchTier"] == "ULPIN"
    assert result["confidence"] >= 0.90


def test_khasra_parcel_tier():
    lines = [
        OcrLine(text="Jamabandi Extract", score=0.9),
        OcrLine(text="Khasra Number: 88/1", score=0.85),
        OcrLine(text="Owner Name: Anita Sharma", score=0.9),
        OcrLine(text="Khata: 22", score=0.8),
        OcrLine(text="Khewat Number 8", score=0.8),
    ]
    result = extract_fields(lines)
    assert result["ulpin"] is None
    assert result["khasraNumber"] == "88/1"
    assert result["khataNumber"] == "22"
    assert result["khewatNumber"] == "8"
    assert result["matchTier"] == "PARCEL"
    assert result["parcelIdType"] == "KHASRA"
    assert result["confidence"] >= 0.75


def test_survey_south_tier():
    lines = [
        OcrLine(text="RTC Extract Andhra Pradesh", score=0.9),
        OcrLine(text="Survey Number: 201/3", score=0.86),
        OcrLine(text="Khata Number: 88", score=0.8),
        OcrLine(text="Owner: Lakshmi Reddy", score=0.9),
    ]
    result = extract_fields(lines)
    assert result["surveyNumber"] == "201/3"
    assert result["matchTier"] == "PARCEL"
    assert result["parcelIdType"] == "SURVEY"


def test_weak_tier_low_confidence():
    lines = [
        OcrLine(text="illegible scribble page", score=0.3),
        OcrLine(text="no useful identifiers", score=0.25),
    ]
    result = extract_fields(lines)
    assert result["matchTier"] == "WEAK"
    assert result["confidence"] < 0.75


if __name__ == "__main__":
    test_normalize_ulpin()
    test_meta_ulpin_first()
    test_keyword_ulpin_without_full_jamabandi()
    test_khasra_parcel_tier()
    test_survey_south_tier()
    test_weak_tier_low_confidence()
    print("all extract tests passed")
