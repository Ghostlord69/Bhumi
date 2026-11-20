# Handwrite → photo → see extract JSON / post to Bhumi

**How to see JSON only (no post):** photo the paper, then:

```bash
curl -s -F "file=@/path/to/your-photo.jpg" http://localhost:8000/extract
```

**How to post:** `user@bhumi.test` / `User@123` → Sell → attach paper + ≥3 photos.

**Writing tips:** block capitals, dark pen, one field per line, flat bright photo.

---

# A. Seeded in our system (AI should match government record)

Use city **Ballabgarh** (Haryana / Faridabad) unless noted.

## A1 — ULPIN + khasra match → AI verified queue

```
JAMABANDI / RECORD OF RIGHTS
ULPIN: HR06A1B2C3D4E5
KHASRA: 123/4
KHATA: 45
KHEWAT: 12
KHATAUNI: 3
OWNER: Ramesh Kumar
VILLAGE: Sihi
TEHSIL: Ballabgarh
DISTRICT: Faridabad
STATE: Haryana
AREA: 2.5 acres
LAND TYPE: AGRICULTURAL
```

## A2 — Khasra-only match

```
JAMABANDI
KHASRA NUMBER: 88/1
KHATA: 22
KHEWAT: 8
OWNER NAME: Anita Sharma
VILLAGE: Palla
TEHSIL / CITY: Ballabgarh
DISTRICT: Faridabad
STATE: Haryana
MEASUREMENTS: 1,800 sq. yd.
LAND: RESIDENTIAL
```

## A3 — ULPIN seed match

```
BHU-AADHAAR / ULPIN
ULPIN: HR06F6G7H8I9J0
KHASRA: 999/1
OWNER: Demo Ulpin Owner
VILLAGE: Sihi
CITY: Ballabgarh
DISTRICT: Faridabad
STATE: Haryana
AREA: 1.2 acres
LAND TYPE: AGRICULTURAL
```

## A4 — Survey seed (Andhra) — post city Anantapur

```
RECORD OF RIGHTS
SURVEY NUMBER: 201/3
KHATA: 88
OWNER: Lakshmi Reddy
VILLAGE: Anantapur Rural
TEHSIL: Anantapur
DISTRICT: Anantapur
STATE: Andhra Pradesh
AREA: 3.0 acres
LAND TYPE: AGRICULTURAL
```

---

# B. NOT in our system (for rich JSON — expect physical queue if you post)

These owners / khasra / ULPIN are **not** in the seed government DB. OCR should still fill JSON; posting → `NEEDS_PHYSICAL_VERIFICATION`.

## B1 — Full jamabandi + real ULPIN (Faridabad coords) → lat/lng in JSON

ULPIN below encodes ≈ `28.408900, 77.317800` (so `latitude` / `longitude` / `locateUrl` appear when OCR reads ULPIN correctly).

```
JAMABANDI / RECORD OF RIGHTS
ULPIN: 86CZS4DA9TP0H0
KHASRA: 441/2/3
KHATA: 310
KHEWAT: 77
KHATAUNI: 9
OWNER: Kavita Malhotra
VILLAGE: NIT
TEHSIL: Faridabad
DISTRICT: Faridabad
STATE: Haryana
AREA: 1.75 acres
LAND TYPE: RESIDENTIAL
```

**Example JSON shape you should see** (values may vary with OCR noise):

```json
{
  "documentType": "JAMABANDI",
  "ulpin": "86CZS4DA9TP0H0",
  "khasraNumber": "441/2/3",
  "khataNumber": "310",
  "khewatNumber": "77",
  "khatauniNumber": "9",
  "ownerName": "Kavita Malhotra",
  "village": "NIT",
  "tehsil": "Faridabad",
  "district": "Faridabad",
  "state": "Haryana",
  "areaAcres": 1.75,
  "landType": "RESIDENTIAL",
  "latitude": 28.4089,
  "longitude": 77.3178,
  "locateUrl": "https://www.google.com/maps?q=28.408900,77.317800",
  "confidence": 0.0,
  "matchTier": "..."
}
```

(`confidence` may be present in AI JSON; the marketplace UI strips confidence from user-facing summaries.)

## B2 — Jaipur parcel (not seeded)

ULPIN ≈ Jaipur `26.912400, 75.787300`

```
JAMABANDI
ULPIN: 84SGCGD8ZJ9CH0
KHASRA: 55/9/1
KHATA: 120
OWNER: Arjun Rathore
VILLAGE: Amer
TEHSIL: Jaipur
DISTRICT: Jaipur
STATE: Rajasthan
AREA: 0.9 acres
LAND TYPE: AGRICULTURAL
```

## B3 — Mumbai survey-style (not seeded)

ULPIN ≈ Mumbai `19.076000, 72.877700`

```
RECORD OF RIGHTS
ULPIN: 7B2C00D5RDLSH0
SURVEY NUMBER: 902/4
KHATA: 44
OWNER: Fatima Sheikh
VILLAGE: Andheri
TEHSIL: Mumbai Suburban
DISTRICT: Mumbai
STATE: Maharashtra
AREA: 0.25 acres
LAND TYPE: RESIDENTIAL
```

## B4 — Bengaluru + multi-segment path (not seeded)

ULPIN ≈ Bengaluru `12.971600, 77.594600`

```
JAMABANDI
ULPIN: 74UBYZDAYYYZH0
KHASRA / SURVEY: 318/2/1/4
KHATA: 88/3
KHEWAT: 5
OWNER: Suresh Nair
VILLAGE: Whitefield
TEHSIL: Bengaluru East
DISTRICT: Bengaluru Urban
STATE: Karnataka
AREA: 2.2 acres
LAND TYPE: AGRICULTURAL
```

## B5 — Hindi labels + English values (not seeded — good OCR stress)

```
जमाबंदी / JAMABANDI
यूलपिन / ULPIN: 86CZS4DA9TP0H0
खसरा / KHASRA: 512/8
खाता / KHATA: 66
मालिक / OWNER: Neha Kapoor
गाँव / VILLAGE: Ballabgarh
जिला / DISTRICT: Faridabad
राज्य / STATE: Haryana
क्षेत्रफल / AREA: 1.1 acres
LAND TYPE: AGRICULTURAL
```

## B6 — Minimal fields (JSON will be sparse — still useful)

```
KHASRA: 333/3/3
OWNER: Ghost Parcel Owner
VILLAGE: Unknown Hamlet
STATE: Haryana
```

---

# Cheat sheet

| Sheet | In seed DB? | After `/extract` | If you post listing |
|-------|-------------|------------------|---------------------|
| A1–A4 | Yes | IDs match seed | Often **AI verified** |
| B1–B5 | No | Full-ish JSON + Locate if ULPIN OK | **Physical verification** |
| B6 | No | Sparse JSON | Physical verification |

**Form tip for B sheets:** city can still be Ballabgarh so the Ballabgarh officer sees the physical queue; paper content can say another district — matching uses land IDs, not village text alone.
