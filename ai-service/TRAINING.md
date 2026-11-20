# What to collect and train so the agent can read official land documents

You do **not** train a chatbot to “understand land.” You train (or configure) three separate pieces:

1. **Read text on the page** (OCR / handwriting)
2. **Find which text is which field** (layout / labels)
3. **Match those fields to the official `land_record` row** (rules in Java — this is not ML)

The matcher in `backend` is the legal decision. The agent only fills the JSON in `schema/extraction.schema.json`.

## 1. Official document types (collect these)

Pick **one state** first (one layout family). Mixing every state’s forms in week 8 will fail.

| Type | What it looks like | Why you need it |
|------|--------------------|-----------------|
| Jamabandi / Record of Rights | Printed table, khasra, owner, area | Most common rural title extract |
| RTC / 7/12 / Pahani (as used in your state) | Printed government extract | Alternate official format |
| Sale deed (registered) | Stamped, bilingual, seals | Seller proof of transfer |
| Khatauni / khata | Owner-centric list | Owner name matching |
| Mutation / intkal (optional) | Handwritten or mixed | Stress the human-queue path |

**Counts that are enough for a student prototype**

- Printed, same template: **80–150 pages** (train/val/test split 70/15/15)
- Same template, messy scans (skew, stamp, fade): **30–50 pages**
- Handwritten: **20–40 pages** if you claim handwriting; otherwise skip and always send those to the officer

Photocopy **real layouts**. Replace real names with fake names if you publish the dataset.

## 2. What to label on each page (this is the training target)

For every image/PDF page, store one JSON like `data/annotations/example_jamabandi_001.json`:

- Full-page image (or PDF page rendered at 300 DPI)
- `documentType`
- For each field: **value** + **bounding box** `[x, y, w, h]` in pixels  
  Fields: `ownerName`, `khasraNumber`, `village`, `tehsil`, `district`, `state`, `areaAcres`, `landType`
- Optional: full OCR transcript line-by-line (helps OCR fine-tune)

Tools: Label Studio, CVAT, or Roboflow. Export boxes + text.

Without boxes you can still run **pretrained PaddleOCR** and map fields with keywords (“Khasra”, “खाता”, “Village”). That is weaker but acceptable for a first demo.

## 3. Ground-truth land records (not for OCR — for the matcher)

The same plots must exist in PostgreSQL (`V2__seed_land_records.sql` style):

- `khasra_number`, `village`, `district`, `owner_name`, `area_acres`
- Optional lat/lng or polygon later

Each training document should name a plot that **exists in the DB**. Also keep **mismatch samples** (wrong khasra) so auto-verify does not fire.

## 4. What you actually train vs what you download

| Piece | Train from scratch? | What you need |
|-------|---------------------|----------------|
| PaddleOCR (printed English/Hindi) | **No** for the prototype | Pretrained model. Fine-tune only if your scans fail on digits/khasra |
| TrOCR / handwriting | **No** unless you have 100+ labeled handwritten pages | Otherwise officer-only for handwriting |
| LayoutLMv3 (field finding) | **Fine-tune**, do not train from scratch | The box+label JSON above, 100+ pages of one template |
| LLM (schema fill) | **Do not train** | Prompt + extracted text. Never let it set VERIFIED |
| Matcher | **Not ML** | Java rules: normalize strings, area ±5%, confidence threshold |

**Practical path for 12 weeks:** pretrained OCR + keyword/layout rules on **one form template**. Fine-tune LayoutLM only if field mapping is wrong on that template.

## 5. Languages and image quality

- Script of **your sample state** (Devanagari and/or English). Pretrained OCR must support that script.
- Scan at **300 DPI**, color or grayscale, full page including stamps.
- Include stamps/seals in training images so the model does not treat them as owner names.

## 6. Folder layout for the agent

```
ai-service/
  schema/extraction.schema.json     frozen field names
  data/raw/                         original PDFs
  data/images/                      300 DPI pages
  data/annotations/                 one JSON per page
  data/splits/train.txt val.txt test.txt
  src/preprocess.py                 deskew, binarize (OpenCV)
  src/ocr.py                        PaddleOCR
  src/extract.py                    boxes / keywords → JSON
  src/app.py                        FastAPI POST /extract
```

Backend `AiClient` sends the file; AI service returns the schema JSON + confidence. Java `MatchingService` compares to `land_record`.

## 7. Done criteria for the agent (not “trained forever”)

- On a **held-out printed** jamabandi of the chosen template, khasra + village + owner are correct on most pages.
- Confidence is low when the page is unreadable.
- A wrong khasra never becomes `AUTO_VERIFIED`.
