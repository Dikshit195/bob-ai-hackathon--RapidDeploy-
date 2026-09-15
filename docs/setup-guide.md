# Setup Guide

> **This file is read by the automated evaluation pipeline. Be precise and complete.**

## Prerequisites

Before you begin, ensure you have the following installed:

- [x] **Python 3.10+** — the only runtime requirement
- [x] **pip** — Python package manager (included with Python)
- [ ] Node.js, Docker, or any cloud account — **not required**

No environment variables, no `.env` file, no database, no external services.

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/ibm-hackathon/bob-ai-hackathon--RapidDeploy-.git
cd bob-ai-hackathon--RapidDeploy-

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install fastapi uvicorn[standard] pydantic
```

### Dependencies

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | ≥ 0.100 | Web framework — REST + WebSocket |
| `uvicorn[standard]` | ≥ 0.23 | ASGI server |
| `pydantic` | ≥ 2.0 | Data validation and serialisation |

No frontend build step is required. The dashboard (`static/index.html`) loads ECharts and
Leaflet.js from CDN at runtime.

## Running the Application

```bash
# Start the development server (with auto-reload)
uvicorn main:app --reload

# Or on a specific port
uvicorn main:app --reload --port 8080
```

The application will be available at: **`http://localhost:8000`**

The browser will automatically redirect from `/` to `/index.html` (the dashboard).

### What starts automatically

- All seed data is generated at module load (deterministic, seed=42)
- The background IoT telemetry emitter starts via the `lifespan` handler
- WebSocket endpoint `/ws/telemetry` is immediately available
- Static files served from `./static/` at `/`

## Verifying It Works

Open `http://localhost:8000` in a browser. You should see:

1. **Overview tab** — 9 KPI cards, a Leaflet map of India with 10 shipment markers, and 4 charts
2. **Active Shipments tab** — a 10-row table (click column headers to sort)
3. **Fleet Assets tab** — 15 vehicle cards with fuel bars
4. **Alerts tab** — 4–6 alert rows including CRITICAL temperature excursions
5. **Disruptions tab** — 4 active disruption cards with impact score bars
6. **Live Telemetry tab** — pre-seeded with 10 rows; a new row appears every ~5 seconds

The green "Connected" indicator in the top-right confirms the WebSocket is active.

## Running Tests

```bash
# Install test dependency
pip install pytest httpx

# Run all tests
pytest test_main.py -v
```

Expected output:

```
test_main.py::test_get_all_shipments          PASSED
test_main.py::test_get_shipment_by_id_success PASSED
test_main.py::test_get_shipment_by_id_not_found PASSED
test_main.py::test_filter_shipments_by_status PASSED
test_main.py::test_get_fleet                  PASSED
test_main.py::test_get_fleet_vehicle_not_found PASSED
test_main.py::test_acknowledge_alert_success  PASSED
test_main.py::test_acknowledge_alert_not_found PASSED
test_main.py::test_analytics_summary          PASSED
test_main.py::test_disruptions_endpoint       PASSED

10 passed in ~0.5s
```

## API Documentation (Interactive)

FastAPI's built-in Swagger UI is available while the server is running:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

All 9 endpoints are documented with request/response schemas and can be tested directly
from the browser.

## Project Structure

```
bob-ai-hackathon--RapidDeploy-/
├── main.py                  # Entire backend — FastAPI app, models, seed data, routes
├── test_main.py             # pytest integration tests (10 tests)
├── static/
│   └── index.html           # Entire frontend — single-page dashboard (SPA)
├── docs/
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md       ← you are here
├── demo/
│   ├── screenshots/         # 6 HTML screenshot files, one per tab
│   ├── demo-video-link.txt
│   └── live-demo-url.txt
├── presentation/
│   └── RapidDeploy.pptx     # 15-slide deck
└── submission.yaml          # Hackathon submission metadata
```

## Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | Dependencies not installed | Run `pip install fastapi uvicorn[standard] pydantic` |
| `Address already in use` on port 8000 | Another process on port 8000 | Use `uvicorn main:app --reload --port 8080` |
| Map tiles not loading | No internet connection | The Leaflet map requires internet for CartoDB tiles; the rest of the app works offline |
| Charts appear blank | ECharts CDN not loaded | Check internet connection; ECharts is loaded from `cdn.jsdelivr.net` |
| WebSocket shows "WS Error" | Browser blocks `ws://` on `https://` pages | Use `http://localhost:8000` (not https) in local development |
| `ImportError: cannot import name 'asynccontextmanager'` | Python < 3.10 | Upgrade to Python 3.10 or later |
| Tests fail with `ModuleNotFoundError: No module named 'httpx'` | `httpx` not installed | Run `pip install httpx` |

## Environment Variables

None required. The application has zero mandatory configuration.

The following optional values can be set if desired, but the app runs without them:

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | Override via `--port` flag on the uvicorn command |
| `RELOAD` | `true` (dev) | Pass `--no-reload` for production deployment |

## Production Deployment (optional)

For deploying beyond localhost (e.g., IBM Cloud Code Engine, Railway, Render):

```bash
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

> **Note:** With multiple workers, each process has its own in-memory data store and
> WebSocket connections are not shared across workers. For multi-worker production use,
> replace the in-memory store with a database and use Redis pub/sub for WebSocket broadcast.
