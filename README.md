## AI Risk Scoring Engine Stub (ARSES)

ARSES is a small “AI-style” risk scoring system with:
- **Backend**: Python FastAPI API (`POST /evaluate-risk`)
- **Frontend**: HTML + JavaScript dashboard (TailwindCSS via CDN)
- **Database**: Optional. If `DATABASE_URL` is set, it can use PostgreSQL; otherwise it will use a local SQLite file so it runs immediately.

### Project structure

```
arses-risk-engine/
├── backend/
│   ├── main.py
│   ├── scoring_engine.py
│   ├── models.py
│   ├── database.py
│   ├── routes.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── README.md
```

### Setup

From the project root:

```bash
cd backend
python -m venv .venv
```

Activate the venv:

- **PowerShell (Windows)**:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run backend

From `backend/`:

```bash
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`.

frontend

Open `frontend/index.html` in your browser:

- Windows: open the file directly in Explorer, or run:

```powershell
start ..\frontend\index.html
```

### API documentation

FastAPI docs:
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

#### Endpoint

`POST /evaluate-risk`

Example request:

```json
{
  "user_id": "12345",
  "transaction_amount": 5000,
  "location_risk": 0.6,
  "activity_type": "transfer"
}
```

Example response:

```json
{
  "user_id": "12345",
  "risk_score": 72,
  "risk_level": "HIGH",
  "metadata": {
    "confidence": 84,
    "timestamp": "2026-03-10T10:30:21Z",
    "model_version": "ARS-1.0",
    "data_completeness": 100
  }
}
```

### Scoring logic (summary)

Weights:
- `transaction_amount`: 0.4
- `location_risk`: 0.3
- `activity_risk`: 0.3

Activity risk mapping:
- `transfer`: 0.7
- `withdrawal`: 0.5
- `deposit`: 0.2
- `unknown`: 0.6

Transaction normalization:
- 0–1000 → 0.1
- 1000–10000 → 0.5
- 10000+ → 1.0

Risk level:
- 0–33 → LOW
- 34–66 → MEDIUM
- 67–100 → HIGH

