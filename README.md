# Bhumi — Land Registry & Marketplace

AI-assisted land registry and marketplace. Sellers post land, houses and flats with registry papers. An AI service extracts fields from the papers, the backend matches them against government-style land records, and a city authenticator (Patwari / Tehsildar) approves listings and ownership transfers. After a sale is finalized, a transfer-of-ownership certificate PDF is issued.

**Stack:** React (Vite) · Spring Boot 3 · FastAPI (OCR / extract)

---

## What you need before running

| Requirement | Docker path | Manual path |
|-------------|-------------|-------------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose v2) | Required | Optional |
| [JDK 21](https://adoptium.net/) + [Maven 3.9+](https://maven.apache.org/) | Not needed | Required |
| [Node.js 20+](https://nodejs.org/) + npm | Not needed | Required |
| [Python 3.11+](https://www.python.org/) | Not needed | Required (AI service) |
| [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (`eng` + `hin` languages) | Bundled in the AI image | Recommended for phone-photo OCR |
| Free ports **5173**, **8090**, **8000** | Required | Required |

**Notes**

- Default backend storage is **in memory**. Restarting the backend clears listings you posted; government seed records and demo logins are loaded again on startup.
- You do **not** need to seed data yourself. The app boots with demo government records and demo accounts.
- Sample jamabandi images live under `samples/printed/` (useful when posting a listing).
- First Docker build can take several minutes (Maven + npm downloads).

---

## Option A — Run with Docker (recommended)

From the project root:

```bash
docker compose up --build
```

Then open:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend health | http://localhost:8090/actuator/health |
| AI health | http://localhost:8000/health |

Stop:

```bash
docker compose down
```

Rebuild one service after a code change:

```bash
docker compose up --build backend
```

Optional Postgres only (not required for the default demo):

```bash
cp .env.example .env   # edit passwords if you want
docker compose --profile postgres up -d postgres
```

---

## Option B — Run manually (three terminals)

### 1. AI service

```bash
cd ai-service
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-docker.txt
# Optional full OCR stack (TrOCR / Paddle / YOLO — large download):
# pip install -r requirements.txt
python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Backend

```bash
cd backend
mvn spring-boot:run
# Optional file DB teachers can inspect:
# mvn spring-boot:run -Dspring-boot.run.profiles=sqlite
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://localhost:5173 (Vite proxies `/api` to the backend on port 8090).

---

## Demo accounts (seeded on startup)

| Role | Email | Password |
|------|--------|----------|
| User (buy + sell) | `user@bhumi.test` | `User@123` |
| Seller (demo listings) | `seller@bhumi.test` | `Seller@123` |
| Authenticator (Ballabgarh) | `auth.ballabgarh@bhumi.gov.in` | `Auth@123` |
| State admin (Haryana) | `HR12345RH@bhumi.gov.in` | `AdminHR123@` |

Quick AI check:

```bash
curl -F "file=@samples/printed/jamabandi_123_4.png" http://localhost:8000/extract
```

---

## Project layout

```
ai-service/   FastAPI — POST /extract (paper image → JSON)
backend/      Spring Boot — auth, matching, marketplace, certificates
frontend/     React marketplace + officer / admin desks
samples/      Example jamabandi images for demos
docs/         Reports and presentation materials
```

More AI / OCR notes: `ai-service/ENVIRONMENT.md` and `ai-service/TRAINING.md`.
