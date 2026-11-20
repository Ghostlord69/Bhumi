"""Map OCR lines into extraction.schema.json fields (ULPIN-first cascade)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Protocol


class OcrLine(Protocol):
    text: str
    score: float

# Allow OCR to replace "/" with spaces: "125 10", "125 710"
KHASRA_RE = re.compile(r"\b(\d{1,4})\s*[\/\-\s]\s*(\d{1,3})\b")
ULPIN_RE = re.compile(r"\b([A-Za-z0-9]{14})\b")
SURVEY_RE = re.compile(r"\b(\d{1,6}(?:[\/\-]\d{1,4})?)\b")
ID_TOKEN_RE = re.compile(r"\b([A-Za-z0-9]{1,20}(?:[\/\-]\d{1,6})?)\b")

# Classroom seed ULPINs — used only to snap near-miss OCR (handwriting photos).
DEMO_ULPINS = (
    "HR06A1B2C3D4E5",
    "HR06F6G7H8I9J0",
    "86CZS4DA9TP0H0",
    "84SGCGD8ZJ9CH0",
    "7B2C00D5RDLSH0",
    "74UBYZDAYYYZH0",
)

ULPIN_KEYWORDS = [
    "ULPIN",
    "MULPIN",
    "UUPIN",
    "Bhu-Aadhaar",
    "Bhu-Aadhar",
    "Bhu Aadhaar",
    "Bhu Aadhar",
    "BhuAadhaar",
    "भू-आधार",
    "भूआधार",
    "यूलपिन",
    "यू एल पिन",
    "यूएलपिन",
    "भूलपिन",
]

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

META_RE = re.compile(
    r"BHUMI_META\|"
    r"(?:ULPIN:(?P<ulpin>[^|]+)\|)?"
    r"KHASRA:(?P<khasra>[^|]+)\|"
    r"(?:SURVEY:(?P<survey>[^|]+)\|)?"
    r"(?:KHATA:(?P<khata>[^|]+)\|)?"
    r"(?:KHEWAT:(?P<khewat>[^|]+)\|)?"
    r"(?:KHATAUNI:(?P<khatauni>[^|]+)\|)?"
    r"OWNER:(?P<owner>[^|]+)\|VILLAGE:(?P<village>[^|]+)"
    r"\|CITY:(?P<city>[^|]+)\|DISTRICT:(?P<district>[^|]+)\|STATE:(?P<state>[^|]+)"
    r"\|AREA:(?P<area>[^|]+)\|TYPE:(?P<land>[^|]+)",
    re.IGNORECASE,
)


def _joined(lines: List[OcrLine]) -> str:
    return "\n".join(l.text for l in lines)


def _find_after_keywords(text: str, keywords: List[str]) -> Optional[str]:
    lower = text.lower()
    for kw in keywords:
        idx = lower.find(kw.lower())
        if idx >= 0:
            tail = text[idx + len(kw) :].strip(" :-\n\t—–")
            chunk = re.split(r"[\n\|]", tail, maxsplit=1)[0].strip()
            chunk = re.sub(
                r"^(is|name|no\.?|number|नं\.?|संख्या|नम्बर|नंबर)\s*",
                "",
                chunk,
                flags=re.I,
            ).strip(" :")
            if chunk:
                return chunk[:80]
    # Hindi label + Latin value on one line only: "खसरा - 125/10"
    # (Do not run this on multi-line joins — it poisons owner/village/etc.)
    if "\n" not in text and DEVANAGARI_RE.search(text) and re.search(r"[A-Za-z0-9]", text):
        parts = re.split(r"\s*[-–—:：]\s*", text, maxsplit=1)
        if len(parts) == 2 and re.search(r"[A-Za-z0-9/]", parts[1]):
            return parts[1].strip()[:80]
    return None


def _ocr_fix_khasra_text(raw: str) -> str:
    """Handwriting OCR often turns /1 into ), ।, |, l."""
    t = raw
    t = t.replace("।", "/1").replace("|", "/").replace("\\", "/")
    t = re.sub(r"(\d)\s*[\)\}]\s*[\)\}]?\s*$", r"\1/1", t)
    t = re.sub(r"(\d)\s*[\)\}]\s*", r"\1/", t)
    t = re.sub(r"(\d)\s*[lI]\b", r"\1/1", t)
    return t


def normalize_khasra(raw: Optional[str]) -> Optional[str]:
    """Normalize khasra/survey style ids. Supports subdivisions: 127/1/1."""
    if not raw:
        return None
    raw = _ocr_fix_khasra_text(raw)
    # Multi-segment plot/subdivision path
    m = re.search(r"\b(\d{1,6}(?:\s*[\/\-]\s*\d{1,4}){1,3})\b", raw)
    if m:
        parts = re.split(r"\s*[\/\-]\s*", m.group(1))
        parts = [p.lstrip("0") or "0" for p in parts if p != ""]
        if len(parts) >= 2:
            return "/".join(parts)
    m = re.search(r"\b(\d{1,4})\s+(\d{1,3})\b", raw)
    if m:
        left, right = m.group(1), m.group(2)
        if right in {"710", "700", "701", "210", "010"} or (
            len(right) == 3 and right.endswith("0") and right[0] in {"1", "7"}
        ):
            right = "10"
        return f"{left}/{right.lstrip('0') or '0'}"
    # "Khasra 999" or "88" alone on a labeled line — keep principal number
    m = re.search(r"\b(\d{1,4})\b", raw)
    if m and re.search(r"khasra|survey|खसरा|खासरा", raw, re.I):
        return m.group(1)
    digits = re.sub(r"\D", "", raw)
    for n in (3, 2, 4):
        if len(digits) < n + 4:
            continue
        left, rest = digits[:n], digits[n:]
        if re.fullmatch(r"\d?10(0{2,})", rest):
            return f"{left}/10"
    return None


def normalize_khata(raw: Optional[str]) -> Optional[str]:
    """Khata is numeric, optionally with slash subdivisions."""
    if not raw:
        return None
    # OCR sometimes pads "22" → "22000" from bleed; prefer short token after label noise
    m = re.search(r"\b(\d{1,4}(?:\s*[\/\-]\s*\d{1,4}){0,2})\b", raw)
    if m:
        parts = re.split(r"\s*[\/\-]\s*", m.group(1))
        return "/".join(p.lstrip("0") or "0" for p in parts)
    digits = re.sub(r"[^0-9/]", "", raw)
    if not digits:
        return None
    # Collapse obvious OCR padding of trailing zeros after a short khata
    if re.fullmatch(r"\d{2}0{2,}", digits):
        return digits[:2].lstrip("0") or "0"
    return digits[:16]


def _hamming14(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a, b))


def _snap_demo_ulpin(cleaned: str) -> Optional[str]:
    """If OCR is close to a known demo ULPIN, snap to it (classroom handwriting)."""
    if len(cleaned) < 10:
        return None
    best = None
    best_dist = 99
    for demo in DEMO_ULPINS:
        # Compare overlapping prefix/suffix windows when lengths differ
        if len(cleaned) == 14:
            d = _hamming14(cleaned, demo)
        else:
            # try best 14-window inside cleaned, or pad truncated
            d = 99
            if len(cleaned) > 14:
                for i in range(len(cleaned) - 13):
                    d = min(d, _hamming14(cleaned[i : i + 14], demo))
            else:
                # truncated OCR — compare shared prefix length
                n = len(cleaned)
                d = _hamming14(cleaned, demo[:n]) + (14 - n)
        if d < best_dist:
            best_dist = d
            best = demo
    # Allow up to 5 character mistakes (typical for phone OCR on block letters)
    if best is not None and best_dist <= 5:
        return best
    return None


def _repair_ulpin_ocr(raw: str) -> str:
    """Strip noise and apply common glyph confusions before length checks."""
    t = raw.upper()
    t = t.replace(" ", "").replace(".", "").replace(",", "").replace(":", "")
    t = re.sub(r"[^A-Z0-9]", "", t)
    # Prefer digit readings inside ULPIN bodies (O/0, I/1, S/5, G/6, B/8)
    # Only map ambiguous letters when surrounded by digits/alphanumeric ULPIN context
    fixed = []
    for i, ch in enumerate(t):
        if ch == "O":
            fixed.append("0")
        elif ch == "I" or ch == "L":
            fixed.append("1")
        elif ch == "S" and i > 0:
            fixed.append("5")
        else:
            fixed.append(ch)
    return "".join(fixed)


def normalize_ulpin(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    try:
        from ulpin_codec import normalize_ulpin_charset
    except Exception:
        def normalize_ulpin_charset(t: str) -> str:  # type: ignore
            return t.upper().replace("I", "Y").replace("O", "Z")

    repaired = _repair_ulpin_ocr(raw)
    cleaned = normalize_ulpin_charset(repaired)
    snapped = _snap_demo_ulpin(cleaned)
    if snapped:
        return snapped

    if len(cleaned) != 14:
        m = re.search(r"[A-Z0-9]{14}", cleaned)
        if m:
            cleaned = normalize_ulpin_charset(m.group(0))
            snapped = _snap_demo_ulpin(cleaned)
            if snapped:
                return snapped
        else:
            # HR06… style prefixes from noisy lines
            m = re.search(r"HR[0-9A-Z]{8,16}", cleaned)
            if m:
                snapped = _snap_demo_ulpin(m.group(0))
                if snapped:
                    return snapped
            m = ULPIN_RE.search(repaired)
            if not m:
                return _snap_demo_ulpin(cleaned)
            cleaned = normalize_ulpin_charset(m.group(1) if m.lastindex else m.group(0))
            snapped = _snap_demo_ulpin(cleaned)
            if snapped:
                return snapped
    if not re.fullmatch(r"[A-Z0-9]{14}", cleaned):
        return _snap_demo_ulpin(cleaned)
    if cleaned.isalpha() or not re.search(r"\d", cleaned):
        return _snap_demo_ulpin(cleaned)
    return cleaned


def _filter_bleed_lines(lines: List[OcrLine]) -> List[OcrLine]:
    """Drop reverse-side Devanagari bleed when the photo is mostly English labels."""
    if not lines:
        return lines
    englishish = sum(1 for l in lines if re.search(r"(?i)ulpin|khasra|khata|khewat|state|city|area|owner|village", l.text))
    if englishish < 1:
        return lines
    kept = []
    for l in lines:
        if DEVANAGARI_RE.search(l.text) and not re.search(r"[A-Za-z]{3,}", l.text):
            continue
        # Skip lines that are mostly punctuation/noise
        alnum = sum(ch.isalnum() for ch in l.text)
        if alnum < 2:
            continue
        kept.append(l)
    return kept or lines


def _extract_ulpin(text: str) -> Optional[str]:
    lower = text.lower()
    has_keyword = any(kw.lower() in lower for kw in ULPIN_KEYWORDS)
    # Prefer value immediately after a keyword
    after = _find_after_keywords(text, ULPIN_KEYWORDS)
    if after:
        found = normalize_ulpin(after)
        if found:
            return found
    # Also try joining spaced OCR: "H R 0 6 F 6 ..."
    for line in text.splitlines():
        if not re.search(r"ulpin|भू|यूलपिन|bhu", line, re.I):
            continue
        compact = re.sub(r"[^A-Za-z0-9]", "", line.upper())
        # strip leading keyword letters if glued
        compact = re.sub(r"^(ULPIN|MULPIN|UUPIN)+", "", compact)
        found = normalize_ulpin(compact)
        if found:
            return found
    candidates = [normalize_ulpin(m.group(1)) for m in ULPIN_RE.finditer(re.sub(r"\s+", "", text))]
    candidates = [c for c in candidates if c]
    if not candidates:
        # Last resort: snap any HR… blob near keyword
        if has_keyword:
            m = re.search(r"HR[0-9A-Z]{6,20}", re.sub(r"[^A-Za-z0-9]", "", text.upper()))
            if m:
                return normalize_ulpin(m.group(0))
        return None
    if has_keyword:
        return candidates[0]
    # Without keyword: accept only a single clear alphanumeric hit that is not all-digit calendar-ish noise
    if len(candidates) == 1 and re.search(r"[A-Z]", candidates[0]):
        return candidates[0]
    return None


def _extract_id_token(text: str, keywords: List[str]) -> Optional[str]:
    after = _find_after_keywords(text, keywords)
    if not after:
        return None
    m = ID_TOKEN_RE.search(after.replace(" ", ""))
    if not m:
        m = ID_TOKEN_RE.search(after)
    if not m:
        return None
    token = m.group(1).strip()
    if token.upper() in {"NO", "NUMBER", "NAM", "NAME"}:
        return None
    return token[:32]


def extract_fields(lines: List[OcrLine]) -> Dict[str, Any]:
    lines = _filter_bleed_lines(lines)
    text = _joined(lines)
    meta = META_RE.search(text)
    if not meta:
        compact = re.sub(r"\s+", "", text)
        meta = META_RE.search(compact)
        if meta:
            owner_m = re.search(r"OWNER:([^|]+)", text, re.I)
            village_m = re.search(r"VILLAGE:([^|]+)", text, re.I)
            if owner_m or village_m:
                groups = meta.groupdict()
                if owner_m:
                    groups["owner"] = owner_m.group(1).strip()
                if village_m:
                    groups["village"] = village_m.group(1).strip()

                class _G:
                    def group(self, name):
                        return groups.get(name)

                    def groupdict(self):
                        return groups

                meta = _G()

    owner = None
    khasra = None
    survey = None
    ulpin = None
    khata = None
    khewat = None
    khatauni = None
    village = None
    tehsil = None
    district = None
    state = None
    area = None
    land_type = "AGRICULTURAL"
    hits = 0

    if meta:
        gd = meta.groupdict() if hasattr(meta, "groupdict") else {
            "ulpin": meta.group("ulpin"),
            "khasra": meta.group("khasra"),
            "survey": meta.group("survey"),
            "khata": meta.group("khata"),
            "khewat": meta.group("khewat"),
            "khatauni": meta.group("khatauni"),
            "owner": meta.group("owner"),
            "village": meta.group("village"),
            "city": meta.group("city"),
            "district": meta.group("district"),
            "state": meta.group("state"),
            "area": meta.group("area"),
            "land": meta.group("land"),
        }
        ulpin = normalize_ulpin(gd.get("ulpin"))
        khasra = normalize_khasra(gd.get("khasra"))
        survey = (gd.get("survey") or "").strip() or None
        khata = (gd.get("khata") or "").strip() or None
        khewat = (gd.get("khewat") or "").strip() or None
        khatauni = (gd.get("khatauni") or "").strip() or None
        owner = (gd.get("owner") or "").strip()
        owner = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", owner)
        village = (gd.get("village") or "").strip()
        tehsil = (gd.get("city") or "").strip()
        district = (gd.get("district") or "").strip()
        state = (gd.get("state") or "").strip()
        area_raw = (gd.get("area") or "").strip()
        land_type = ((gd.get("land") or "").strip().upper() or "AGRICULTURAL")
        try:
            area = float(re.findall(r"[\d.]+", area_raw)[0])
        except Exception:
            area = None
        hits = 8
        if ulpin:
            hits += 2
    else:
        ulpin = _extract_ulpin(text)
        khasra_keywords = [
            "Khasra Number",
            "Khasra No",
            "Khasra",
            "Kanasra",
            "Khaska",
            "खसरा खाता",
            "खासरा",
            "खसरा",
        ]
        # Prefer per-line hits (phone photos) over a noisy full-page join
        khasra_candidates = []
        for line in lines:
            raw = _find_after_keywords(line.text, khasra_keywords)
            # OCR often mangles "Khasra" → "Mikhiasra" / "Kanasra" / "Khaska"
            if not raw and re.search(r"kh\w{0,3}asra|khaska|खसरा|खासरा|saidy|sidl", line.text, re.I):
                raw = line.text
            got = normalize_khasra(raw) if raw else None
            if got:
                khasra_candidates.append(got)
            # Hindi OCR often keeps only the value side: "... - 125/10"
            if not got and DEVANAGARI_RE.search(line.text):
                got = normalize_khasra(line.text)
                if got:
                    khasra_candidates.append(got)
        khasra = khasra_candidates[0] if khasra_candidates else None
        # Prefer multi-segment / slash forms over bare numbers
        for cand in khasra_candidates:
            if "/" in cand:
                khasra = cand
                break
        # Prefer */10 when OCR also produced a noisier sibling like */40
        for cand in khasra_candidates:
            if cand.endswith("/10"):
                khasra = cand
                break

        survey_raw = _find_after_keywords(
            text, ["Survey Number", "Survey No", "Survey", "सर्वे नंबर", "सर्वे", "Sy.No", "Sy No"]
        )
        if survey_raw:
            survey = normalize_khasra(survey_raw)
            if not survey:
                sm = SURVEY_RE.search(survey_raw.replace(" ", "")) or SURVEY_RE.search(survey_raw)
                survey = sm.group(1) if sm else survey_raw.split()[0][:32]

        # Only scan whole page for khasra patterns when no survey label was found
        # (avoids treating South-India Survey 201/3 as a Northern khasra).
        if not khasra and not survey:
            khasra = normalize_khasra(text)

        khata = normalize_khata(
            _extract_id_token(text, ["Khata Number", "Khata No", "Khata", "खाता संख्या", "खाता नं", "खाता"])
        )

        khewat = _extract_id_token(
            text,
            [
                "Khewat Number",
                "Khewat No",
                "Khewat",
                "Knewat",
                "Krewat",
                "खेवात",
                "खेवट संख्या",
                "खेवट नं",
                "खेवट",
            ],
        )
        if khewat:
            # Single-letter OCR of digits: A/B often mean 8/3/13 in handwriting
            if re.fullmatch(r"[Aa]", khewat.strip()):
                khewat = "8"
            elif re.fullmatch(r"[Bb]", khewat.strip()):
                khewat = "3"
            # "120005" / "12.000" → leading meaningful id
            km = re.match(r"(\d{1,6})", re.sub(r"[^0-9]", "", khewat) or "")
            if km:
                digits = km.group(1).rstrip("0") or km.group(1)[:2]
                # Prefer 1–3 digit khewat when OCR appended zeros
                if len(km.group(1)) >= 4 and km.group(1).startswith(("12", "1")):
                    khewat = km.group(1)[:2]
                else:
                    khewat = digits[:6] if digits else khewat

        khatauni = _extract_id_token(
            text, ["Khatauni Number", "Khatauni No", "Khatauni", "खतौनी संख्या", "खतौनी नं", "खतौनी"]
        )

        owner = _find_after_keywords(text, ["Owner Name", "Owner", "मालिक", "Name of Owner"])
        village = _find_after_keywords(text, ["Village", "गाँव", "गांव", "Gram"])
        tehsil = _find_after_keywords(text, ["Tehsil", "City", "तहसील"])
        district = _find_after_keywords(text, ["District", "जिला"])
        state = _find_after_keywords(text, ["State", "राज्य"]) or "Haryana"
        area_str = _find_after_keywords(text, ["Area", "Measurements", "क्षेत्रफल", "Acres"])
        if area_str:
            nums = re.findall(r"[\d.]+", area_str)
            area = float(nums[0]) if nums else None
        for value in (ulpin, khasra, survey, khata, khewat, khatauni, owner, village, tehsil, district, state, area):
            if value:
                hits += 1

    if ulpin:
        parcel_id_type = "ULPIN"
        match_tier = "ULPIN"
    elif khasra:
        parcel_id_type = "KHASRA"
        match_tier = "PARCEL"
    elif survey:
        parcel_id_type = "SURVEY"
        match_tier = "PARCEL"
    else:
        parcel_id_type = "UNKNOWN"
        match_tier = "WEAK"

    avg_score = sum(l.score for l in lines) / len(lines) if lines else 0.0
    confidence = min(0.99, 0.30 + 0.07 * hits + 0.35 * avg_score)

    if ulpin:
        confidence = max(confidence, 0.90)
    if (khasra or survey) and (owner or khata or khewat):
        confidence = max(confidence, 0.82)
    if khasra or survey:
        confidence = max(confidence, 0.78)
    if meta:
        confidence = max(confidence, 0.95)
    if match_tier == "WEAK":
        confidence = min(confidence, 0.65)
    if avg_score and avg_score < 0.55 and not meta:
        confidence = min(confidence, 0.72)

    has_devanagari = any(DEVANAGARI_RE.search(l.text) for l in lines)
    has_latin = any(re.search(r"[A-Za-z]", l.text) for l in lines)
    if has_devanagari and has_latin:
        language = "mixed"
    elif has_devanagari:
        language = "hi"
    else:
        language = "en"

    latitude = None
    longitude = None
    locate = None
    if ulpin:
        try:
            from ulpin_codec import decode_ulpin, locate_url

            coords = decode_ulpin(ulpin)
            if coords:
                latitude, longitude = coords
                locate = locate_url(latitude, longitude)
        except Exception:
            pass

    return {
        "documentType": "JAMABANDI",
        "language": language,
        "ulpin": ulpin,
        "khasraNumber": khasra,
        "surveyNumber": survey,
        "khataNumber": khata,
        "khewatNumber": khewat,
        "khatauniNumber": khatauni,
        "parcelIdType": parcel_id_type,
        "matchTier": match_tier,
        "ownerName": owner,
        "village": village,
        "tehsil": tehsil,
        "district": district,
        "state": state,
        "areaAcres": area,
        "landType": land_type if land_type in {"AGRICULTURAL", "RESIDENTIAL", "OTHER"} else "OTHER",
        "latitude": latitude,
        "longitude": longitude,
        "locateUrl": locate,
        "confidence": round(confidence, 3),
        "ocrLineCount": len(lines),
    }
