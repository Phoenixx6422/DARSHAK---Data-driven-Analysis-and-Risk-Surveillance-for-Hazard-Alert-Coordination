# Pre-Disaster Management & Early Warning System (PDEWS)
**Integrated Academic Software Engineering Project — Complete Team Collaboration Hub**

---

### Team Allocation & Integrated Sub-Project Architecture

| Member | Primary Responsibility | Integrated Directory | Key Components & Artifacts |
| :--- | :--- | :--- | :--- |
| **Yash Raj** | Project Lead + System Architecture | Root (`/`) | System architecture, Docker compose coordination, integration |
| **Himanshu Shukla** | Database & Monitoring | `db/`, `monitoring/`, `backend/app/notifications/` | PostgreSQL + PostGIS, Prometheus, Grafana, Notification Gateway |
| **Vaibhav Rawat** | Backend & APIs | `backend/` | FastAPI REST endpoints, WebSockets, data models, `/ui` static mount |
| **Magai Akash Jagdish** | Data Engineering & GIS | `data_pipeline/` | ETL pipelines, GeoJSON risk zones, PostGIS spatial queries |
| **Sanskar Dave** | Frontend & Dashboard | `frontend/` | Complete desktop dashboard UI (`index.html`, `map.html`, `news.html`, `profile.html`) + Mock Data |
| **Mune Harshvardhan Jagdish** | Hazard/Domain & Research | `ml_engine/` | Cyclone (IBTrACS) & Flood (CWC) ML pipelines, multi-hazard aggregator |
| **Tushar Kanaujiya** | Testing & Deployment | `backend/tests/`, `frontend/tests/` | 23 Python backend unit tests + 67 JavaScript Jest unit tests (90 tests total) |

---

### Critical Architectural Rule (Fixed)
> **The Disaster Management Authority has NO involvement in generating, approving, modifying, or influencing predictions, risk assessments, or alerts.**
> If risk is **High** or **Critical**, emergency warnings are dispatched **automatically** without any manual or authority approval.

---

### Folder Hierarchy

```text
pdews_integrated/
├── docker-compose.yml              # [Himanshu & Yash] PostGIS, Prometheus, Grafana, Backend
├── README.md                       # Master Architecture & Integration Guide
│
├── db/                             # [Himanshu Shukla] Database & Persistence
│   ├── migrations/                 # Core tables + PostGIS spatial tables
│   └── seed/                       # Sample data & SQL seeds
│
├── monitoring/                     # [Himanshu Shukla] Observability Stack
│   ├── prometheus/                 # Scrape targets
│   └── grafana/datasources/        # Auto-provisioned Prometheus datasource
│
├── backend/                        # [Vaibhav Rawat] Core API & WebSockets
│   ├── app/
│   │   ├── notifications/          # [Himanshu] Automated Notification Gateway
│   │   └── main.py                 # REST endpoints, WebSockets & UI mount
│   └── tests/                      # [Tushar & Himanshu] 23 Pytest Unit Tests
│
├── data_pipeline/                  # [Magai Akash Jagdish] GIS & ETL
│   ├── sample_zones.geojson        # Regional boundary layers & shapefiles
│   └── README.md
│
├── ml_engine/                      # [Mune Harshvardhan Jagdish] AI/ML Hazard Pipelines
│   ├── hazard_cyclone/             # IBTrACS North Indian Ocean Cyclone Model
│   ├── hazard_flood/               # CWC River Basin Hydrology Model
│   ├── risk_engine/                # Multi-Hazard SafetyScore Aggregator
│   ├── data/                       # Active storm & river gauge feeds
│   ├── models/                     # Trained .joblib model artifacts
│   └── notebooks/                  # Training Jupyter notebooks
│
└── frontend/                       # [Sanskar Dave & Tushar Kanaujiya]
    ├── css/styles.css              # Desktop-first styles
    ├── data/mock/                  # Mock JSONs (alerts, weather, news, profile, zones)
    ├── js/                         # api.js, utils.js, layout.js, home.js, map.js, news.js, profile.js
    ├── index.html, map.html, news.html, profile.html
    └── tests/                      # 67 Jest Unit Tests (utils, api, file-protocol)
```

---

### How to Run and Test the Integrated System

#### 1. Run All Backend Unit Tests (Python / Pytest)
```powershell
cd C:\Users\Himanshu\Downloads\pdews_integrated\backend
python -m pytest tests -v
```
*(All 23 backend tests pass covering APIs, WebSockets, PostGIS models, Automated Notification Gateway, and Cyclone/Flood ML pipelines).*

#### 2. Run All Frontend Unit Tests (Node / Jest)
```powershell
cd C:\Users\Himanshu\Downloads\pdews_integrated\frontend
npm test
```
*(All 67 frontend tests pass across 3 test suites covering utils, mock fallbacks, and boundary conditions).*

#### 3. Run the Full Integrated Server
```powershell
cd C:\Users\Himanshu\Downloads\pdews_integrated\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Interactive Frontend UI:** [http://localhost:8000/ui](http://localhost:8000/ui)
* **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Real-time WebSockets:** `ws://localhost:8000/ws/alerts`
* **Automated Notification Logs:** [http://localhost:8000/api/v1/notifications/logs](http://localhost:8000/api/v1/notifications/logs)

#### 4. Run via Docker Compose (With PostGIS & Grafana)
```powershell
cd C:\Users\Himanshu\Downloads\pdews_integrated
docker compose up --build
```
* PostGIS Database on port `5432`
* Prometheus on port `9090`
* Grafana on port `3001` (user: `admin`, pass: `admin`)
