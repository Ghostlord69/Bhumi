"""Optional YOLO field-block detection for jamabandi pages.

If ultralytics + weights at models/jamabandi_blocks.pt are available, detect
labeled boxes (ulpin, khasra, khata, khewat, owner, village, other_text).
Otherwise return empty and let line-OCR fallback run.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

WEIGHTS = Path(__file__).resolve().parents[1] / "models" / "jamabandi_blocks.pt"
_model = None
_ready: Optional[bool] = None

CLASS_NAMES = ["ulpin", "khasra", "khata", "khewat", "owner", "village", "other_text"]


@dataclass
class Block:
    label: str
    score: float
    box: Tuple[int, int, int, int]  # x1,y1,x2,y2
    text: str = ""


def _init() -> bool:
    global _model, _ready
    if _ready is not None:
        return _ready
    if not WEIGHTS.exists():
        logger.info("YOLO weights missing at %s — using line OCR fallback", WEIGHTS)
        _ready = False
        return False
    try:
        from ultralytics import YOLO

        _model = YOLO(str(WEIGHTS))
        _ready = True
        logger.info("YOLO jamabandi blocks ready")
    except Exception as ex:
        logger.warning("YOLO unavailable: %s", ex)
        _ready = False
    return _ready


def detect_blocks(image_bgr: np.ndarray, conf: float = 0.25) -> List[Block]:
    if not _init() or _model is None:
        return []
    try:
        results = _model.predict(source=image_bgr, conf=conf, verbose=False)
        blocks: List[Block] = []
        if not results:
            return blocks
        r0 = results[0]
        names = getattr(r0, "names", None) or {i: n for i, n in enumerate(CLASS_NAMES)}
        boxes = getattr(r0, "boxes", None)
        if boxes is None:
            return blocks
        for box in boxes:
            xyxy = box.xyxy[0].tolist()
            cls_id = int(box.cls[0].item()) if box.cls is not None else 0
            score = float(box.conf[0].item()) if box.conf is not None else 0.0
            label = names.get(cls_id, CLASS_NAMES[min(cls_id, len(CLASS_NAMES) - 1)])
            x1, y1, x2, y2 = [int(v) for v in xyxy]
            blocks.append(Block(label=label, score=score, box=(x1, y1, x2, y2)))
        return blocks
    except Exception as ex:
        logger.warning("YOLO detect failed: %s", ex)
        return []


def read_blocks(image_bgr: np.ndarray) -> List[Tuple[str, str, float]]:
    """Return list of (label, text, score) from YOLO crops + TrOCR/Tesseract."""
    from ocr import OcrLine  # noqa: F401
    from preprocess import crop_box

    blocks = detect_blocks(image_bgr)
    if not blocks:
        return []
    out: List[Tuple[str, str, float]] = []
    try:
        from trocr_reader import read_crop
    except Exception:
        read_crop = None
    try:
        import pytesseract
        from PIL import Image
    except Exception:
        pytesseract = None
        Image = None

    for b in blocks:
        crop = crop_box(image_bgr, b.box, pad=4)
        text = ""
        if read_crop:
            text = read_crop(crop) or ""
        if (not text or len(text) < 2) and pytesseract is not None and Image is not None:
            import cv2

            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
            text = pytesseract.image_to_string(Image.fromarray(gray), config="--oem 3 --psm 7").strip()
        if text:
            # Prefix label so extract_fields keyword cascade can see "ULPIN …"
            prefix = {
                "ulpin": "ULPIN",
                "khasra": "Khasra",
                "khata": "Khata",
                "khewat": "Khewat",
                "owner": "Owner",
                "village": "Village",
            }.get(b.label, b.label)
            out.append((b.label, f"{prefix} {text}", max(0.7, b.score)))
    return out
