# 🚀 RapidDeploy — Supply Chain & Cold-Chain Operations Dashboard

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | RapidDeploy |
| **Track** | Open |
| **Team Lead** | Patel Dikshit — 26mca115@gmail.com |
| **Members** | Parekh Rudra, Patel Dhruv, Patel Jainil |

---

## 🎯 Problem Statement

Supply chain and cold-chain logistics teams struggle to monitor temperature-sensitive shipments in real time, detect IoT excursions before product damage occurs, and correlate fleet idle time, disruption events, and delayed shipments in a single view. Operations managers and fleet coordinators currently rely on disconnected tools, leading to delayed responses to critical events such as reefer failures or port congestion.

---

## 💡 Solution

RapidDeploy is a real-time supply chain and cold-chain monitoring dashboard built with FastAPI and a vanilla HTML/JS frontend. It simulates a live IoT sensor network across 10 active shipments, streaming temperature and humidity readings over WebSocket every 5 seconds, and surfaces KPI summaries, fleet status, temperature excursion alerts, and supply-chain disruption events — all in a single unified dashboard with sortable tables and live charts.

---

## ✨ Key Features

- **Real-time IoT Telemetry:** Live temperature and humidity readings streamed via WebSocket (`/ws/telemetry`) with a live line chart and category donut chart updating every 5 seconds.
- **Temperature Excursion Detection:** Per-category thresholds (frozen, refrigerated, pharma, ambient) with automatic alert generation and one-click acknowledgement.
- **Sortable Shipments Table:** Interactive table of all active shipments with click-to-sort on 9 columns (ID, product, category, carrier, status, temperature, progress, ETA, excursion).
- **Supply-Chain Disruption Tracking:** Disruption event cards with impact score bars, affected shipment linkage, and active/resolved filter.
- **Aggregated KPI Dashboard:** Fleet utilisation, idle vehicle count, critical alert count, and excursion summary refreshed every 30 seconds.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python, HTML, CSS, JavaScript |
| **Frameworks** | FastAPI, Pydantic, pytest, Leaflet.js, Apache ECharts |
| **IBM Technologies** | IBM Bob |
| **Databases** | None (in-memory, seeded at startup) |
| **Other** | WebSocket, Uvicorn, CORS Middleware, CartoDB tile layer |

---

## 📁 Repository Structure

```
bob-ai-hackathon--RapidDeploy-/
├── main.py                  # FastAPI backend — models, seed data, REST + WebSocket routes
├── test_main.py             # pytest integration tests (10 tests)
├── static/
│   └── index.html           # Single-page dashboard (vanilla HTML / JS / CSS)
├── src/
│   ├── README.md            # Source code documentation
│   └── .env.example         # Environment variable template
├── docs/
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/
│   ├── screenshots/         # Per-tab HTML screenshots
│   ├── demo-video-link.txt
│   └── live-demo-url.txt
├── presentation/
│   └── RapidDeploy.pptx     # 15-slide deck
└── submission.yaml          # Hackathon submission metadata
```

---

## ⚡ How to Run

Full instructions: [`docs/setup-guide.md`](docs/setup-guide.md)

```bash
# 1. Clone the repo
git clone https://github.com/ibm-hackathon/bob-ai-hackathon--RapidDeploy-.git
cd bob-ai-hackathon--RapidDeploy-

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install fastapi uvicorn[standard] pydantic

# 4. Run the development server
uvicorn main:app --reload
```

Open **`http://localhost:8000`** in your browser. The dashboard loads immediately — no `.env` file or external services required.

To run tests:

```bash
pip install pytest httpx
pytest test_main.py -v
```

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/RapidDeploy.pptx](presentation/) |

---

## ⚠️ Known Limitations

- All shipment, fleet, alert, and disruption data is simulated in-memory at startup using a seeded RNG — there is no persistent database or real IoT device integration.
- The IoT telemetry is randomly generated rather than sourced from actual sensors.
- Authentication and authorisation are not implemented; all API endpoints are open.
- The dashboard has been tested on Chrome and Edge; mobile layout is functional but not fully optimised for small screens.

---

## 🏅 What We're Most Proud Of

The end-to-end real-time telemetry pipeline: a background `asyncio` task emits simulated IoT sensor readings every 5 seconds and broadcasts them over WebSocket to all connected clients simultaneously. The Live Telemetry tab pre-seeds itself instantly from the REST API on first open, then seamlessly continues with live WebSocket updates — giving users immediate visibility into the current cold-chain state without waiting for the next push cycle. The sortable shipments table and the clean separation of static seed data (via the `_DISRUPTION_SPECS` data table) from rendering logic were also highlights.

---
