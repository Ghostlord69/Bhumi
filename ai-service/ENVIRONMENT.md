# Environment to train and run the document AI agent

This is the full local setup: machine, Python, GPU/CPU, models, labeling, training, and how the agent is meant to talk to Spring Boot. Follow the steps in order. Do not skip version pins — mixed CUDA/Paddle builds are the usual failure mode.

---

## 0. What you are installing (mental model)

Three programs, not one:

1. **Label Studio** — you draw boxes on scans and type khasra, owner, village, etc.
2. **PaddleOCR (and optionally LayoutLMv3)** — reads pixels → text and fields.
3. **Your FastAPI service** (`ai-service/src/app.py`) — receives a file from Java, returns JSON. Java still decides AUTO vs HUMAN using PostgreSQL/government records.

You do **not** train ChatGPT. You do **not** need a database for this training loop.

---

## 1. Hardware and OS

**Minimum (CPU-only, student laptop)**

- 16 GB RAM (8 GB will swap and feel frozen during OCR)
- 20 GB free disk (models + images)
- macOS Apple Silicon, Windows 11, or Ubuntu 22.04

**Recommended if you fine-tune LayoutLM**

- NVIDIA GPU, 8 GB VRAM or more (RTX 3060 / 4060 class)
- CUDA toolkit matching the Paddle/PyTorch wheel you install
- Linux is less painful than Windows for CUDA

Apple Silicon: use **CPU PaddleOCR**. There is no stable CUDA path. That is enough for a printed-jamabandi demo.

Check disk:

```bash
df -h .
```

---

## 2. System packages

### macOS

1. Install [Homebrew](https://brew.sh) if missing.
2. Install tools:

```bash
brew install python@3.11 git wget libpng jpeg
```

Use **Python 3.11**, not 3.13. PaddleOCR wheels lag new Python.

```bash
python3.11 --version
```

You want `Python 3.11.x`.

### Ubuntu 22.04

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip \
  git wget unzip build-essential libgl1 libglib2.0-0 libgomp1
```

`libgl1` is required by OpenCV. Without it you get `libGL.so.1: cannot open shared object file`.

### Windows

1. Install Python 3.11 from python.org. Tick **Add python.exe to PATH**.
2. Install [Git for Windows](https://git-scm.com).
3. Optional GPU: install the NVIDIA driver from GeForce Experience, then CUDA **only if** the Paddle wheel you pick lists that CUDA version.

Check:

```bat
python --version
```

---

## 3. NVIDIA GPU (Linux/Windows only — skip on Mac)

1. Confirm a GPU exists:

```bash
nvidia-smi
```

You must see a driver version and a GPU name. If the command is missing, install the vendor driver first. Do not install CUDA until `nvidia-smi` works.

2. Note the CUDA version in the top-right of `nvidia-smi` (example: `CUDA Version: 12.4`). That is the **driver’s max**, not what you must compile. You will pick a **Paddle wheel** built for CUDA 11.8 or 12.x as listed on the Paddle site.

3. If you only run inference with PaddleOCR’s pretrained models, **CPU is enough**. Install GPU Paddle only when OCR on a batch of 100 pages is too slow.

---

## 4. Create an isolated Python environment

Never install ML libraries into system Python.

```bash
cd /Users/kmishra/land-registry/ai-service
python3.11 -m venv .venv
```

Activate:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

The prompt should start with `(.venv)`.

Upgrade installer tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Confirm which Python:

```bash
which python
python -c "import sys; print(sys.version); print(sys.executable)"
```

The path must be inside `ai-service/.venv`.

---

## 5. Install PaddlePaddle + PaddleOCR + OpenCV

### 5a. CPU (default — use this first)

```bash
pip install paddlepaddle==2.6.2
pip install paddleocr==2.8.1
pip install opencv-python-headless==4.10.0.84 pillow==10.4.0 numpy==1.26.4
pip install fastapi==0.115.0 uvicorn==0.30.6 python-multipart==0.0.12

**Verify OCR works before labeling 100 pages:**

```bash
python - <<'PY'
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
print('PaddleOCR ready', ocr is not None)
PY
```

First run **downloads detection + recognition models** (hundreds of MB) into `~/.paddleocr/`. Need network. If you are offline, copy that folder from another machine.

For Hindi/Devanagari land records:

```python
PaddleOCR(use_angle_cls=True, lang='hi')
```

`lang='en'` is Latin. `lang='hi'` is Hindi. Mixed pages: run both and merge lines, or use `lang='en'` if the khasra digits are Arabic numerals (they usually are).

### 5b. GPU Paddle (only after CPU works)

Look up the exact wheel on https://www.paddlepaddle.org.cn/install/quick (Linux, pip, CUDA 11.8 or 12.3). Example shape (versions change — copy from the official matrix, do not invent):

```bash
pip uninstall -y paddlepaddle
pip install paddlepaddle-gpu==2.6.2  # plus the CUDA extra they specify
```

Then:

```bash
python -c "import paddle; print(paddle.device.is_compiled_with_cuda()); print(paddle.device.get_device())"
```

You want `True` and `gpu:0`. If you see `cpu`, the wheel does not match the driver. Revert to CPU paddle rather than debugging CUDA for days.

---

## 6. Folder layout on disk (create these)

From `ai-service/`:

```bash
mkdir -p data/raw data/images data/annotations data/splits
```

| Folder | What goes here |
|--------|----------------|
| `data/raw/` | Original PDFs from the tehsil (never commit real names to git) |
| `data/images/` | One PNG/JPG per page, **300 DPI**, named `jamabandi_001.jpg` |
| `data/annotations/` | One JSON per image (boxes + field names) |
| `data/splits/train.txt` | Filenames for training |
| `data/splits/val.txt` | Filenames you do not train on (measure quality) |
| `data/splits/test.txt` | Final held-out pages |

**How to rasterize a PDF to 300 DPI (macOS/Linux, ImageMagick or pdftoppm):**

```bash
# poppler
pdftoppm -png -r 300 data/raw/deed.pdf data/images/deed
```

Windows: install Poppler, then the same command from `bin`.

Scan paper with a phone: use Adobe Scan or Microsoft Lens, export PDF, then rasterize. Avoid screenshots of WhatsApp photos (too much JPEG damage).

---

## 7. Install Label Studio (drawing boxes)

Keep using the same venv or a second venv named `labelvenv`. Same venv is fine.

```bash
pip install label-studio==1.13.2
label-studio start
```

Browser: `http://localhost:8080` (Label Studio’s own port). **Stop it before running Spring Boot**, or start Label Studio on another port:

```bash
label-studio start --port 8082
```

Create a project:

1. Name: `Bhumi jamabandi fields`
2. Labeling config (paste this):

```xml
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="ownerName"/>
    <Label value="khasraNumber"/>
    <Label value="village"/>
    <Label value="tehsil"/>
    <Label value="district"/>
    <Label value="state"/>
    <Label value="areaAcres"/>
    <Label value="landType"/>
  </RectangleLabels>
  <TextArea name="transcription" toName="image" perRegion="true"/>
</View>
```

3. Import images from `data/images/`.
4. For each page: draw a box, pick the field, type the text **exactly as on paper** (including `123/4`).
5. Export JSON. Convert export → one file per page matching `data/annotations/example_jamabandi_001.json`.

**How many pages:** 80–150 of **one** printed template. Mix states later, not now.

Anonymize: replace real owner names in the transcription if you will share the dataset.

---

## 8. Train vs not train (honest path)

### Path A — no training (week 8 demo)

Use pretrained PaddleOCR. Map lines with keywords (`Khasra`, `खासरा`, `Owner`). This is what `src/extract.py` should do first.

You still need **5–10 sample scans** to tune keywords. You do not need Label Studio.

### Path B — fine-tune field detector (LayoutLMv3)

Only after Path A mis-reads your template.

1. Install PyTorch CPU or CUDA from https://pytorch.org (pick the command for your OS). Example CPU:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install transformers==4.44.2 datasets==2.21.0
```

2. Convert your box JSON to Hugging Face document layout format (words + bboxes + labels).
3. Fine-tune `microsoft/layoutlmv3-base` for token classification or a visual question setup. Expect several hours on GPU, overnight on CPU for a tiny set.
4. Save the checkpoint under `ai-service/models/layoutlm-bhumi/`.

**Do not train PaddleOCR from scratch.** Fine-tune recognition only if digits in khasra are systematically wrong, using Paddle’s official rec fine-tune recipe and at least a few thousand cropped text lines.

### Path C — handwriting (TrOCR)

```bash
pip install transformers
```

Use `microsoft/trocr-base-handwritten` on cropped handwriting regions. If accuracy is poor, send those cases to `NEEDS_HUMAN`. Do not block the project on this.

---

## 9. Run the agent as an HTTP service

Implement `POST /extract` in `src/app.py` to:

1. Accept `multipart/form-data` file
2. Preprocess (deskew) with OpenCV
3. OCR
4. Fill `schema/extraction.schema.json`
5. Return `{ "ownerName": "...", "khasraNumber": "...", "confidence": 0.81 }`

Run:

```bash
source .venv/bin/activate
cd /Users/kmishra/land-registry/ai-service
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

Test:

```bash
curl -F "file=@data/images/jamabandi_001.jpg" http://localhost:8000/extract
```

Spring Boot `app.ai.base-url` is already `http://localhost:8000`. Wire `AiClient` when you replace the in-memory matcher. Until then, Java simulates match on khasra `123/4` in Ballabgarh so the product can be demoed without Python.

**Port map (avoid clashes)**

| App | Port |
|-----|------|
| Spring Boot | 8080 |
| Vite | 5173 |
| FastAPI agent | 8000 |
| Label Studio | 8082 |

---

## 10. Quality check before you call it “trained”

On `data/splits/test.txt` (pages the model never trained on):

- Khasra exact match rate (after stripping spaces)
- Owner name normalized (ignore case, extra initials)
- If khasra wrong → Java must **not** auto-verify

Log 20 failures as images + expected vs got. That table belongs in the project report.

---

## 11. Common failures

| Symptom | Cause | Fix |
|---------|--------|-----|
| `Microsoft Visual C++` error on Windows | Missing build tools | Install “MSVC runtime” / VS Build Tools |
| `libGL.so.1` | Missing system OpenCV deps | `libgl1` (Ubuntu) |
| Paddle download hangs | Firewall | Retry; or copy `~/.paddleocr` |
| OCR empty | DPI too low | Re-export at 300 DPI |
| Python 3.13 + paddle | No wheel | Use 3.11 venv |
| Port 8080 busy | Label Studio or Tomcat | Change Label Studio port |
| Mac GPU paddle | Unsupported | CPU only |

---

## 12. Security

Training images are **PII**. Keep `data/raw` out of git (already gitignored for PDFs). Do not upload citizen deeds to public Colab without redaction.
