"""Generate temporary jamabandi PNGs for live demos (synthetic, not official)."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "samples" / "temp_jamabandi"

TEMP_SAMPLES = [
    {
        "file": "temp_jamabandi_ulpin_sihi.png",
        "title": "TEMP DEMO — ULPIN + Khasra",
        "ulpin": "HR06A1B2C3D4E5",
        "khasra": "123/4",
        "survey": "",
        "khata": "45",
        "khewat": "12",
        "khatauni": "3",
        "owner": "Ramesh Kumar",
        "village": "Sihi",
        "city": "Ballabgarh",
        "district": "Faridabad",
        "state": "Haryana",
        "area": "2.5 acres",
        "land": "AGRICULTURAL",
    },
    {
        "file": "temp_jamabandi_khasra_palla.png",
        "title": "TEMP DEMO — Khasra only",
        "ulpin": "",
        "khasra": "88/1",
        "survey": "",
        "khata": "22",
        "khewat": "8",
        "khatauni": "",
        "owner": "Anita Sharma",
        "village": "Palla",
        "city": "Ballabgarh",
        "district": "Faridabad",
        "state": "Haryana",
        "area": "1.8 acres",
        "land": "AGRICULTURAL",
    },
    {
        "file": "temp_jamabandi_house_nit.png",
        "title": "TEMP DEMO — Residential plot",
        "ulpin": "",
        "khasra": "12/3",
        "survey": "",
        "khata": "7",
        "khewat": "2",
        "khatauni": "",
        "owner": "Priya Verma",
        "village": "NIT",
        "city": "Faridabad",
        "district": "Faridabad",
        "state": "Haryana",
        "area": "180 sq. yd.",
        "land": "RESIDENTIAL",
    },
    {
        "file": "temp_jamabandi_survey_ap.png",
        "title": "TEMP DEMO — Survey (South India)",
        "ulpin": "",
        "khasra": "",
        "survey": "201/3",
        "khata": "88",
        "khewat": "",
        "khatauni": "",
        "owner": "Lakshmi Reddy",
        "village": "Anantapur Rural",
        "city": "Anantapur",
        "district": "Anantapur",
        "state": "Andhra Pradesh",
        "area": "3.0 acres",
        "land": "AGRICULTURAL",
    },
    {
        "file": "temp_jamabandi_hindi_labels.png",
        "title": "TEMP DEMO — Hindi labels / English values",
        "ulpin": "HR06F7H9K2I2J0",
        "khasra": "125/10",
        "survey": "",
        "khata": "45",
        "khewat": "12",
        "khatauni": "",
        "owner": "Meera Singh",
        "village": "Sihi",
        "city": "Ballabgarh",
        "district": "Faridabad",
        "state": "Haryana",
        "area": "1.2 acres",
        "land": "AGRICULTURAL",
        "hindi_rows": True,
    },
]


def font(size: int):
    for name in (
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def build_meta(sample: dict) -> str:
    parts = ["BHUMI_META"]
    if sample.get("ulpin"):
        parts.append(f"ULPIN:{sample['ulpin']}")
    parts.append(f"KHASRA:{sample.get('khasra') or ''}")
    if sample.get("survey"):
        parts.append(f"SURVEY:{sample['survey']}")
    if sample.get("khata"):
        parts.append(f"KHATA:{sample['khata']}")
    if sample.get("khewat"):
        parts.append(f"KHEWAT:{sample['khewat']}")
    if sample.get("khatauni"):
        parts.append(f"KHATAUNI:{sample['khatauni']}")
    parts.extend(
        [
            f"OWNER:{sample['owner']}",
            f"VILLAGE:{sample['village']}",
            f"CITY:{sample['city']}",
            f"DISTRICT:{sample['district']}",
            f"STATE:{sample['state']}",
            f"AREA:{sample['area']}",
            f"TYPE:{sample['land']}",
        ]
    )
    return "|".join(parts)


def draw_form(sample: dict) -> Image.Image:
    img = Image.new("RGB", (1240, 1750), (243, 235, 224))
    draw = ImageDraw.Draw(img)
    title_f = font(34)
    body_f = font(26)
    small_f = font(18)

    draw.rectangle((36, 36, 1204, 1714), outline=(47, 59, 44), width=4)
    draw.rectangle((52, 52, 1188, 1698), outline=(181, 103, 61), width=2)
    draw.text((90, 70), sample["title"], fill=(181, 103, 61), font=body_f)
    draw.text((90, 115), f"GOVERNMENT OF {sample['state'].upper()}", fill=(26, 34, 24), font=title_f)
    draw.text((90, 165), "Temporary Jamabandi Extract (synthetic demo)", fill=(61, 90, 64), font=body_f)
    draw.line((80, 215, 1160, 215), fill=(181, 103, 61), width=3)

    if sample.get("hindi_rows"):
        rows = [
            ("यू एल पिन / ULPIN", sample.get("ulpin") or "—"),
            ("खसरा / Khasra", sample.get("khasra") or "—"),
            ("खाता / Khata", sample.get("khata") or "—"),
            ("खेवट / Khewat", sample.get("khewat") or "—"),
            ("मालिक / Owner", sample["owner"]),
            ("गाँव / Village", sample["village"]),
            ("तहसील / City", sample["city"]),
            ("जिला / District", sample["district"]),
            ("राज्य / State", sample["state"]),
            ("क्षेत्रफल / Area", sample["area"]),
            ("Land Type", sample["land"]),
        ]
    else:
        rows = [
            ("Document Type", "JAMABANDI"),
            ("ULPIN (Bhu-Aadhaar)", sample.get("ulpin") or "—"),
            ("Owner Name", sample["owner"]),
            ("Khasra Number", sample.get("khasra") or "—"),
            ("Survey Number", sample.get("survey") or "—"),
            ("Khata Number", sample.get("khata") or "—"),
            ("Khewat Number", sample.get("khewat") or "—"),
            ("Khatauni Number", sample.get("khatauni") or "—"),
            ("Village", sample["village"]),
            ("Tehsil / City", sample["city"]),
            ("District", sample["district"]),
            ("State", sample["state"]),
            ("Area / Measurements", sample["area"]),
            ("Land Type", sample["land"]),
        ]

    y = 250
    for label, value in rows:
        draw.rectangle((90, y - 6, 1150, y + 42), fill=(250, 246, 239))
        draw.text((110, y), f"{label}", fill=(107, 114, 102), font=body_f)
        draw.text((560, y), str(value), fill=(26, 34, 24), font=body_f)
        y += 56

    draw.text(
        (90, 1580),
        "SYNTHETIC / TEMPORARY — for OCR & marketplace demo only. Not an official record.",
        fill=(155, 44, 44),
        font=small_f,
    )
    draw.text((90, 1620), "Expected JSON keys: ulpin, khasraNumber, khataNumber, khewatNumber, ownerName…", fill=(92, 111, 100), font=small_f)
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    expected = {}
    for sample in TEMP_SAMPLES:
        image = draw_form(sample)
        meta = build_meta(sample)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("bhumi_meta", meta)
        path = OUT / sample["file"]
        image.save(path, "PNG", pnginfo=pnginfo)
        expected[sample["file"]] = {
            "ulpin": sample.get("ulpin") or None,
            "khasraNumber": sample.get("khasra") or None,
            "surveyNumber": sample.get("survey") or None,
            "khataNumber": sample.get("khata") or None,
            "khewatNumber": sample.get("khewat") or None,
            "ownerName": sample["owner"],
            "village": sample["village"],
            "state": sample["state"],
            "matchTier": "ULPIN" if sample.get("ulpin") else ("SURVEY" if sample.get("survey") else "PARCEL"),
        }
        print("wrote", path)

    manifest = OUT / "expected_results.json"
    manifest.write_text(json.dumps(expected, indent=2), encoding="utf-8")
    print("wrote", manifest)
    print(f"\n{len(TEMP_SAMPLES)} temporary jamabandis in {OUT}")


if __name__ == "__main__":
    main()
