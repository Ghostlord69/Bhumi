"""Real OCR for handwritten / scanned land labels.

Default on macOS: notebook-page crop → merged line bands → Tesseract + TrOCR
per line (Paddle skipped — it hangs). Override with BHUMI_OCR_ENGINE=
  labels | tesseract | trocr | paddle | hybrid
"""

from __future__ import annotations

import logging
import os
import platform
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

_ocr_en = None
_ocr_hi = None
_paddle_ready = None

LOW_SCORE = 0.75
WIKI_NOISE = re.compile(
    r"wikipedia|wikidata|what links here|related changes|permanent link|cite this page|special pages",
    re.I,
)
LABEL_HINT = re.compile(
    r"ulpin|mulpin|uupin|bhu|khasra|kanasra|khaska|khata|khewat|knewat|krewat|survey|"
    r"खसरा|खाता|खेवट|खेवात|खतौनी|भू|यूलपिन|यू\s*एल\s*पिन|आधार",
    re.I,
)
DEVANAGARI = re.compile(r"[\u0900-\u097F]")


@dataclass
class OcrLine:
    text: str
    score: float
    box: Optional[Tuple[int, int, int, int]] = field(default=None)


def _engine_mode() -> str:
    raw = (os.environ.get("BHUMI_OCR_ENGINE") or "").strip().lower()
    if raw in {"labels", "tesseract", "trocr", "paddle", "hybrid"}:
        return raw
    # Best demo path for phone photos of handwritten KEY: VALUE lines
    return "labels"


def _cv2():
    import cv2

    return cv2


def _to_gray(image: np.ndarray) -> np.ndarray:
    cv2 = _cv2()
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def _notebook_page(gray: np.ndarray) -> np.ndarray:
    """Crop the bright notebook / paper region out of a phone photo."""
    cv2 = _cv2()
    h, w = gray.shape[:2]
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, bright = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if float(np.mean(bright)) < 127:
        bright = 255 - bright
    contours, _ = cv2.findContours(bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return gray[int(h * 0.1) : int(h * 0.9), int(w * 0.1) : int(w * 0.9)]
    c = max(contours, key=cv2.contourArea)
    x, y, bw, bh = cv2.boundingRect(c)
    if bw * bh < 0.15 * h * w:
        return gray[int(h * 0.1) : int(h * 0.9), int(w * 0.1) : int(w * 0.9)]
    inset = max(4, int(0.03 * bh))
    return gray[max(0, y + inset) : min(h, y + bh - inset), max(0, x + inset) : min(w, x + bw - inset)]


def _prepare_page(gray: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    cv2 = _cv2()
    page = _notebook_page(gray)
    # Upscale small phone crops for OCR
    h, w = page.shape[:2]
    if max(h, w) < 1400:
        scale = 1400 / max(h, w)
        page = cv2.resize(page, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
    page = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8)).apply(page)
    thr = cv2.adaptiveThreshold(
        page, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 41, 14
    )
    thr = cv2.morphologyEx(
        thr, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (28, 3))
    )
    return page, thr


def _merged_bands(thr: np.ndarray) -> List[Tuple[int, int]]:
    row = thr.sum(axis=1).astype(float)
    k = np.ones(17) / 17.0
    row = np.convolve(row, k, mode="same")
    thresh = max(row.max() * 0.12, 1.0)
    active = row > thresh
    raw: List[List[int]] = []
    start = None
    for i, on in enumerate(active):
        if on and start is None:
            start = i
        elif not on and start is not None:
            raw.append([start, i])
            start = None
    if start is not None:
        raw.append([start, len(active)])

    merged: List[List[int]] = []
    for band in raw:
        if not merged:
            merged.append(band)
            continue
        if band[0] - merged[-1][1] < 28:
            merged[-1][1] = band[1]
        else:
            merged.append(band)

    ph = thr.shape[0]
    out: List[Tuple[int, int]] = []
    for a, b in merged:
        height = b - a
        if height < int(0.025 * ph) or height > int(0.28 * ph):
            continue
        out.append((a, b))
    return out


def _line_crop(page: np.ndarray, thr: np.ndarray, y1: int, y2: int) -> np.ndarray:
    cv2 = _cv2()
    y1 = max(0, y1 - 8)
    y2 = min(page.shape[0], y2 + 8)
    strip = thr[y1:y2]
    xs = np.where(strip.sum(axis=0) > (strip.shape[0] * 255 * 0.008))[0]
    if xs.size == 0:
        crop = page[y1:y2]
    else:
        x1 = max(0, int(xs[0]) - 12)
        x2 = min(page.shape[1], int(xs[-1]) + 12)
        crop = page[y1:y2, x1:x2]
    return cv2.copyMakeBorder(crop, 12, 12, 12, 12, cv2.BORDER_CONSTANT, value=255)


def _tess_line(crop: np.ndarray) -> str:
    try:
        import pytesseract

        # hin+eng reads Devanagari labels; eng whitelist helps Latin values (ULPIN/khasra).
        attempts = [
            ("hin+eng", "--oem 3 --psm 7"),
            ("hin+eng", "--oem 3 --psm 6"),
            ("eng", "--oem 3 --psm 7"),
            (
                "eng",
                "--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:/\\- ",
            ),
        ]
        best = ""
        best_score = -1
        for lang, cfg in attempts:
            try:
                text = pytesseract.image_to_string(crop, lang=lang, config=cfg).strip()
            except Exception:
                continue
            text = re.sub(r"\s+", " ", text)
            if not text:
                continue
            score = len(text)
            if LABEL_HINT.search(text):
                score += 40
            if DEVANAGARI.search(text):
                score += 20
            if re.search(r"[A-Za-z0-9]{4,}|/\d", text):
                score += 15
            if score > best_score:
                best_score = score
                best = text
        return best
    except Exception:
        return ""


def _trocr_line(crop: np.ndarray) -> str:
    try:
        from trocr_reader import read_crop
    except Exception:
        return ""
    text = read_crop(crop) or ""
    text = re.sub(r"\s+", " ", text).strip()
    if not text or WIKI_NOISE.search(text):
        return ""
    # TrOCR sometimes appends long garbage after a good start
    if len(text) > 80:
        text = text[:80]
    return text


def _pick_line_text(tess: str, trocr: str) -> Tuple[str, float]:
    """Prefer the candidate that looks like a land-record label."""
    scored = []
    for text, base in ((tess, 0.70), (trocr, 0.74)):
        if not text:
            continue
        score = base
        if LABEL_HINT.search(text):
            score += 0.15
        if re.search(r"\d", text):
            score += 0.05
        if WIKI_NOISE.search(text):
            score -= 0.5
        scored.append((score, text))
    if not scored:
        return "", 0.0
    scored.sort(reverse=True)
    return scored[0][1], min(0.92, scored[0][0])


def _run_labels_ocr(image: np.ndarray) -> List[OcrLine]:
    """Phone-photo handwriting path used for live teacher demos."""
    gray = _to_gray(image)
    page, thr = _prepare_page(gray)
    bands = _merged_bands(thr)
    logger.info("labels OCR: %s line bands on page %sx%s", len(bands), page.shape[1], page.shape[0])
    lines: List[OcrLine] = []
    for y1, y2 in bands[:12]:
        crop = _line_crop(page, thr, y1, y2)
        tess = _tess_line(crop)
        trocr = _trocr_line(crop)
        text, score = _pick_line_text(tess, trocr)
        if not text:
            continue
        # Keep both if they differ and both look useful
        lines.append(OcrLine(text=text, score=score, box=(0, y1, page.shape[1], y2)))
        if tess and trocr and tess.lower() != trocr.lower():
            alt, alt_score = _pick_line_text(trocr if text == tess else tess, "")
            if alt and LABEL_HINT.search(alt) and alt.lower() != text.lower():
                lines.append(OcrLine(text=alt, score=alt_score, box=(0, y1, page.shape[1], y2)))
    # Full-page safety net: English + Hindi OCR
    try:
        import pytesseract
        from PIL import Image

        pil = Image.fromarray(page)
        for lang in ("hin+eng", "eng"):
            try:
                full = pytesseract.image_to_string(pil, lang=lang, config="--oem 3 --psm 6")
            except Exception:
                continue
            for row in full.splitlines():
                row = row.strip()
                if row and (LABEL_HINT.search(row) or DEVANAGARI.search(row) or re.search(r"\d+/\d+", row)):
                    lines.append(OcrLine(text=row, score=0.66))
    except Exception:
        pass
    return _dedupe(lines)


def _init_paddle():
    global _ocr_en, _ocr_hi, _paddle_ready
    if _paddle_ready is not None:
        return _paddle_ready
    try:
        from paddleocr import PaddleOCR

        _ocr_en = PaddleOCR(
            use_angle_cls=False, lang="en", show_log=False, use_gpu=False, enable_mkldnn=False
        )
        try:
            _ocr_hi = PaddleOCR(
                use_angle_cls=False, lang="hi", show_log=False, use_gpu=False, enable_mkldnn=False
            )
        except Exception:
            _ocr_hi = None
        _paddle_ready = True
    except Exception as ex:
        logger.warning("PaddleOCR unavailable: %s", ex)
        _paddle_ready = False
    return _paddle_ready


def _box_from_item(item) -> Optional[Tuple[int, int, int, int]]:
    try:
        pts = item[0]
        xs = [int(p[0]) for p in pts]
        ys = [int(p[1]) for p in pts]
        return min(xs), min(ys), max(xs), max(ys)
    except Exception:
        return None


def _run_engine(engine, image: np.ndarray) -> List[OcrLine]:
    if engine is None:
        return []
    result = engine.ocr(image, cls=False)
    lines: List[OcrLine] = []
    if not result:
        return lines
    page = result[0] if isinstance(result, list) and result else result
    if not page:
        return lines
    for item in page:
        try:
            text = item[1][0]
            score = float(item[1][1])
            if text and text.strip():
                lines.append(OcrLine(text=text.strip(), score=score, box=_box_from_item(item)))
        except Exception:
            continue
    return lines


def _run_tesseract(image: np.ndarray) -> List[OcrLine]:
    try:
        import pytesseract
        from PIL import Image
    except Exception as ex:
        logger.warning("Tesseract unavailable: %s", ex)
        return []
    gray = _to_gray(image)
    page, _ = _prepare_page(gray)
    text = pytesseract.image_to_string(Image.fromarray(page), config="--oem 3 --psm 6")
    return [OcrLine(text=line.strip(), score=0.68) for line in text.splitlines() if line.strip()]


def _dedupe(lines: List[OcrLine]) -> List[OcrLine]:
    best = {}
    for line in lines:
        key = re.sub(r"\s+", " ", line.text.lower())
        prev = best.get(key)
        if prev is None or line.score > prev.score:
            best[key] = line
    return list(best.values())


def run_ocr(
    image_bgr_or_gray: np.ndarray,
    binary: Optional[np.ndarray] = None,
    use_trocr: bool = True,
) -> List[OcrLine]:
    if image_bgr_or_gray.ndim == 2:
        image = np.stack([image_bgr_or_gray] * 3, axis=-1)
    else:
        image = image_bgr_or_gray

    mode = _engine_mode()
    logger.info("OCR engine mode=%s", mode)

    if mode == "labels":
        # Prefer YOLO field blocks when weights are present
        try:
            from yolo_blocks import read_blocks

            labeled = read_blocks(image)
            if labeled:
                yolo_lines = [
                    OcrLine(text=text, score=score) for (_label, text, score) in labeled
                ]
                if yolo_lines:
                    return _dedupe(yolo_lines)
        except Exception as ex:
            logger.info("YOLO blocks skipped: %s", ex)
        lines = _run_labels_ocr(image)
        if lines:
            return lines
        return _run_tesseract(image)

    if mode == "tesseract":
        return _run_tesseract(image)

    if mode == "trocr":
        return _run_labels_ocr(image)

    lines: List[OcrLine] = []
    if mode in {"paddle", "hybrid"} and _init_paddle():
        lines.extend(_run_engine(_ocr_en, image))
        lines.extend(_run_engine(_ocr_hi, image))
        lines = _dedupe(lines)
    if not lines:
        lines = _run_labels_ocr(image) or _run_tesseract(image)
    return lines
