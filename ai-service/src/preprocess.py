"""Image / PDF page load, deskew, contrast for OCR (print + handwriting)."""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any, Optional, Tuple

import numpy as np
from PIL import Image


def _cv2():
    import cv2
    return cv2


@dataclass
class PreprocessResult:
    gray: Any
    binary: Optional[Any] = None


def load_image_bytes(data: bytes) -> Any:
    """Load image bytes (PNG/JPEG) into a BGR ndarray when OpenCV is available, else RGB ndarray."""
    try:
        cv2 = _cv2()
        arr = np.frombuffer(data, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is not None:
            return image
    except Exception:
        pass
    pil = Image.open(io.BytesIO(data)).convert("RGB")
    return np.array(pil)


def _deskew(gray: Any, cv2) -> Any:
    coords = np.column_stack(np.where(gray < 200))
    if coords.size == 0:
        return gray
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    if abs(angle) <= 0.3 or abs(angle) >= 15:
        return gray
    (h, w) = gray.shape[:2]
    matrix = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(gray, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def _upscale(gray: Any, cv2, min_side: int = 2000) -> Any:
    h, w = gray.shape[:2]
    if max(h, w) >= min_side:
        return gray
    scale = min_side / max(h, w)
    return cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)


def _unsharp(gray: Any, cv2) -> Any:
    blur = cv2.GaussianBlur(gray, (0, 0), 1.2)
    return cv2.addWeighted(gray, 1.35, blur, -0.35, 0)


def preprocess(image: Any) -> Any:
    """Backward-compatible: returns enhanced grayscale (CLAHE + deskew + upscale)."""
    return preprocess_variants(image).gray


def preprocess_variants(image: Any) -> PreprocessResult:
    """Return gray (for print OCR) and adaptive binary (for handwriting crops)."""
    try:
        cv2 = _cv2()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
        gray = cv2.fastNlMeansDenoising(gray, None, 8, 7, 21)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        gray = _deskew(gray, cv2)
        gray = _upscale(gray, cv2, min_side=2000)
        gray = _unsharp(gray, cv2)

        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 12
        )
        # Otsu fallback blend when adaptive is too noisy
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Prefer adaptive for ink; keep otsu available via average ink density check
        ink_ratio = float(np.mean(binary < 128))
        if ink_ratio < 0.02 or ink_ratio > 0.45:
            binary = otsu
        return PreprocessResult(gray=gray, binary=binary)
    except Exception:
        pil = Image.fromarray(image if image.ndim == 2 else image)
        gray_img = pil.convert("L")
        if max(gray_img.size) < 2000:
            scale = 2000 / max(gray_img.size)
            gray_img = gray_img.resize(
                (int(gray_img.size[0] * scale), int(gray_img.size[1] * scale)),
                Image.Resampling.BICUBIC,
            )
        gray = np.array(gray_img)
        return PreprocessResult(gray=gray, binary=None)


def to_bgr(gray: Any) -> Any:
    try:
        cv2 = _cv2()
        if gray.ndim == 2:
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return gray
    except Exception:
        if gray.ndim == 2:
            return np.stack([gray, gray, gray], axis=-1)
        return gray


def crop_box(image: Any, box: Tuple[int, int, int, int], pad: int = 4) -> Any:
    """Crop (x1,y1,x2,y2) with padding; works on gray or BGR."""
    h, w = image.shape[:2]
    x1, y1, x2, y2 = box
    x1 = max(0, x1 - pad)
    y1 = max(0, y1 - pad)
    x2 = min(w, x2 + pad)
    y2 = min(h, y2 + pad)
    if x2 <= x1 or y2 <= y1:
        return image
    return image[y1:y2, x1:x2]
