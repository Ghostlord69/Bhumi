"""Generate synthetic jamabandi-style PNGs for OCR demos (no real PII)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "samples" / "printed"

SAMPLES = [
    {
        "file": "jamabandi_123_4.png",
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
        "file": "jamabandi_88_1.png",
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
        "file": "jamabandi_45_2.png",
        "ulpin": "",
        "khasra": "45/2",
        "survey": "",
        "khata": "10",
        "khewat": "4",
        "khatauni": "1",
        "owner": "Suresh Yadav",
        "village": "Tigaon",
        "city": "Ballabgarh",
        "district": "Faridabad",
        "state": "Haryana",
        "area": "1.0 acres",
        "land": "AGRICULTURAL",
    },
    {
        "file": "jamabandi_12_3.png",
        "ulpin": "",
        "khasra": "12/3",
        "survey": "",
        "khata": "7",
        "khewat": "",
        "khatauni": "",
        "owner": "Priya Verma",
        "village": "Dayalpur",
        "city": "Faridabad",
        "district": "Faridabad",
        "state": "Haryana",
        "area": "2.0 acres",
        "land": "RESIDENTIAL",
    },
    {
        "file": "jamabandi_ulpin_only.png",
        "ulpin": "HR06F6G7H8I9J0",
        "khasra": "999/1",
        "survey": "",
        "khata": "",
        "khewat": "",
        "khatauni": "",
        "owner": "Demo Ulpin Owner",
        "village": "Sihi",
        "city": "Ballabgarh",
        "district": "Faridabad",
        "state": "Haryana",
        "area": "1.2 acres",
        "land": "AGRICULTURAL",
    },
    {
        "file": "survey_south_201.png",
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
]


def font(size: int):
    for name in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
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
    img = Image.new("RGB", (1240, 1850), (246, 241, 231))
    draw = ImageDraw.Draw(img)
    title_f = font(36)
    body_f = font(28)
    small_f = font(20)

    draw.rectangle((40, 40, 1200, 1810), outline=(31, 107, 69), width=4)
    draw.rectangle((55, 55, 1185, 1795), outline=(31, 107, 69), width=1)
    draw.text((220, 80), f"GOVERNMENT OF {sample['state'].upper()}", fill=(18, 35, 26), font=title_f)
    draw.text((260, 130), "District Land Records — Jamabandi Extract", fill=(31, 107, 69), font=body_f)
    draw.line((80, 190, 1160, 190), fill=(196, 165, 116), width=3)

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
    y = 220
    for label, value in rows:
        draw.text((100, y), f"{label}:", fill=(92, 111, 100), font=body_f)
        draw.text((520, y), value, fill=(18, 35, 26), font=body_f)
        y += 58

    meta = build_meta(sample)
    draw.text((80, 1680), meta[:110], fill=(40, 40, 40), font=small_f)
    if len(meta) > 110:
        draw.text((80, 1710), meta[110:], fill=(40, 40, 40), font=small_f)
    draw.text((80, 1750), "Synthetic demo document — not an official record", fill=(120, 120, 120), font=small_f)
    img.info["bhumi_meta"] = meta
    return img


def save_with_meta(image: Image.Image, path: Path, meta: str):
    from PIL import PngImagePlugin

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("bhumi_meta", meta)
    image.save(path, "PNG", pnginfo=pnginfo)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ai_images = ROOT / "ai-service" / "data" / "images"
    ai_images.mkdir(parents=True, exist_ok=True)
    for sample in SAMPLES:
        image = draw_form(sample)
        meta = image.info["bhumi_meta"]
        save_with_meta(image, OUT / sample["file"], meta)
        save_with_meta(image, ai_images / sample["file"], meta)
        print("wrote", OUT / sample["file"])
    for i in range(5, 13):
        sample = {
            "file": f"jamabandi_demo_{i}.png",
            "ulpin": "",
            "khasra": f"{10 + i}/{i % 7 + 1}",
            "survey": "",
            "khata": str(i),
            "khewat": str(i % 5 + 1),
            "khatauni": "",
            "owner": f"Demo Owner {i}",
            "village": "Sihi",
            "city": "Ballabgarh",
            "district": "Faridabad",
            "state": "Haryana",
            "area": f"{(i % 5) + 1}.0 acres",
            "land": "AGRICULTURAL",
        }
        image = draw_form(sample)
        meta = image.info["bhumi_meta"]
        save_with_meta(image, OUT / sample["file"], meta)
        save_with_meta(image, ai_images / sample["file"], meta)
        print("wrote", OUT / sample["file"])


if __name__ == "__main__":
    main()
