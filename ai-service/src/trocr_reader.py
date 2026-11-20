"""Optional TrOCR handwriting reader for low-confidence line crops."""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

_processor = None
_model = None
_ready: Optional[bool] = None


def _init() -> bool:
    global _processor, _model, _ready
    if _ready is not None:
        return _ready
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel

        name = "microsoft/trocr-base-handwritten"
        _processor = TrOCRProcessor.from_pretrained(name)
        _model = VisionEncoderDecoderModel.from_pretrained(name)
        _model.eval()
        _ready = True
        logger.info("TrOCR ready (%s)", name)
    except Exception as ex:
        logger.warning("TrOCR unavailable: %s", ex)
        _ready = False
    return _ready


def read_crop(image_bgr_or_gray: np.ndarray) -> Optional[str]:
    """OCR a single cropped line/word image. Returns None if TrOCR is unavailable."""
    if not _init() or _processor is None or _model is None:
        return None
    try:
        import torch

        if image_bgr_or_gray.ndim == 2:
            pil = Image.fromarray(image_bgr_or_gray).convert("RGB")
        else:
            # Assume BGR from OpenCV
            rgb = image_bgr_or_gray[:, :, ::-1]
            pil = Image.fromarray(rgb).convert("RGB")

        pixel_values = _processor(images=pil, return_tensors="pt").pixel_values
        with torch.no_grad():
            generated = _model.generate(pixel_values, max_new_tokens=64)
        text = _processor.batch_decode(generated, skip_special_tokens=True)[0]
        text = (text or "").strip()
        return text or None
    except Exception as ex:
        logger.debug("TrOCR crop failed: %s", ex)
        return None
