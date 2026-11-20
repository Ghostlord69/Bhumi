FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Core API + image stack first (fast, enough for digital demo papers with bhumi_meta)
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Optional heavy OCR (TrOCR / Paddle / YOLO). Comment out for a smaller image.
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY schema ./schema

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
