"""FastAPI entry: POST /extract → extraction JSON + confidence (ULPIN-first)."""

from __future__ import annotations

import logging
import sys
from io import BytesIO
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile
from PIL import Image

# Allow `python -m uvicorn src.app:app` with sibling imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract import extract_fields
from ocr import OcrLine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bhumi-ai")

app = FastAPI(title="Bhumi document agent")


def _empty_result(note: str, filename: Optional[str] = None) -> dict:
    return {
        "documentType": "OTHER",
        "language": "mixed",
        "ulpin": None,
        "ownerName": None,
        "khasraNumber": None,
        "surveyNumber": None,
        "khataNumber": None,
        "khewatNumber": None,
        "khatauniNumber": None,
        "parcelIdType": "UNKNOWN",
        "matchTier": "WEAK",
        "village": None,
        "tehsil": None,
        "district": None,
        "state": None,
        "areaAcres": None,
        "landType": None,
        "confidence": 0.0,
        "filename": filename,
        "note": note,
    }


@app.get("/health")
def health():
    return {"ok": True, "service": "bhumi-ai", "pipeline": "ulpin-first-labels-ocr"}


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    data = await file.read()
    if not data:
        return _empty_result("Empty upload", file.filename)
    try:
        # Digital sample PNGs may carry bhumi_meta — still useful for printed demos.
        # Live teacher photos (JPG/HEIC) have no meta and go through real OCR.
        meta_lines = []
        try:
            pil = Image.open(BytesIO(data))
            chunk = pil.info.get("bhumi_meta")
            if chunk:
                meta_lines = [OcrLine(text=chunk, score=0.99)]
        except Exception:
            meta_lines = []

        if meta_lines:
            result = extract_fields(meta_lines)
            result["filename"] = file.filename
            result["note"] = "Extracted from digital paper metadata + schema mapping"
            return result

        from ocr import run_ocr
        from preprocess import load_image_bytes

        image = load_image_bytes(data)
        lines = run_ocr(image, use_trocr=True)
        result = extract_fields(lines)
        result["filename"] = file.filename
        result["note"] = "Extracted via real OCR (line bands + Tesseract/TrOCR)"
        result["ocrLines"] = [l.text for l in lines[:20]]
        logger.info(
            "extract file=%s ulpin=%s khasra=%s survey=%s tier=%s conf=%s lines=%s",
            file.filename,
            result.get("ulpin"),
            result.get("khasraNumber"),
            result.get("surveyNumber"),
            result.get("matchTier"),
            result.get("confidence"),
            result.get("ocrLineCount"),
        )
        return result
    except Exception as ex:
        logger.exception("extract failed")
        return _empty_result(f"Extraction failed: {ex}", file.filename)
