# Solution Overview

## What We Built

**RapidDeploy** is a real-time supply chain and cold-chain operations dashboard that gives logistics
and operations teams a single unified command centre for monitoring temperature-sensitive shipments,
fleet assets, IoT sensor readings, disruption events, and alerts — all updating live without page reloads.

It simulates a production-grade IoT sensor network across 10 active shipments spanning routes across
India, with a background process emitting realistic temperature, humidity, GPS, and battery readings
every 5 seconds over a WebSocket connection to every connected browser client simultaneously.

The system requires no external database, no cloud account, and no configuration — it runs entirely
from a single Python file and a single HTML file, making it instantly demonstrable on any machine.

## How It Works

### Data Flow

```
IoT Sensors (simulated)
        │
        ▼
_telemetry_emitter()  ←─── asyncio background task, runs every 5 s
        │
        ├──► Updates in-memory SHIPMENTS store (latest_reading, temp_excursion)
        │
        └──► WebSocket broadcast → ALL connected browser clients
                    │
                    └──► Live Telemetry Tab: feed row + chart update + KPI increment

Browser (on tab open)
        │
        ├──► GET /api/analytics/summary  → Overview KPI cards + 30 s polling
        ├──► GET /api/shipments          → Active Shipments table (sortable, filterable)
        ├──► GET /api/fleet              → Fleet Assets grid
        ├──► GET /api/alerts             → Alerts list with acknowledge action
        ├──► GET /api/disruptions        → Disruption event cards
        └──► GET /api/shipments + WS     → Live Telemetry pre-seed + live updates
```

### Step-by-step

1. **Server starts** — `uvicorn main:app --reload` launches the FastAPI application. At module load
   time, 5 seed functions run: `_build_shipments()`, `_build_fleet()`, `_build_alerts()`,
   `_build_disruptions()`, populating four in-memory lists (`SHIPMENTS`, `FLEET`, `ALERTS`,
   `DISRUPTIONS`). The `lifespan` context manager starts `_telemetry_emitter()` as a background task.

2. **Browser opens** — The SPA (`/index.html`) loads. The boot IIFE immediately calls
   `loadOverview()` and `loadCharts()`, rendering 9 KPI cards and 4 ECharts visualisations.
   `connectWS()` opens a WebSocket to `/ws/telemetry`. `initMap()` draws a Leaflet map with
   live shipment markers colour-coded by excursion state.

3. **Every 5 seconds** — `_telemetry_emitter()` picks a random shipment, generates a new
   `IoTReading` (temperature within ±spread of the category threshold, random humidity, GPS drift,
   battery decay), updates the in-memory shipment's `latest_reading` and `temp_excursion` flag,
   and broadcasts a JSON payload over WebSocket to all connected clients.

4. **Browser receives WS push** — `ws.onmessage` updates the live temperature line chart (last 20
   readings), the category donut chart, the feed list (newest first, max 100 rows), and the 4 KPI
   counters (total readings, excursions detected, active sensors, last reading).

5. **User opens a tab** — clicking any tab fires its dedicated loader:
   - **Active Shipments** → `loadShipments()` fetches `/api/shipments` and renders a sortable table.
     Clicking any of 9 column headers re-sorts client-side without re-fetching.
   - **Fleet Assets** → `loadFleet()` renders vehicle cards with fuel bars, idle time, driver info.
   - **Alerts** → `loadAlerts()` renders severity-banded alert rows; clicking Acknowledge calls
     `POST /api/alerts/{id}/acknowledge` and updates the button state inline.
   - **Disruptions** → `loadDisruptions()` renders impact-score cards with colour-coded bars.
   - **Live Telemetry** → `loadTelemetry()` pre-seeds from `/api/shipments` instantly, then
     continues updating via WebSocket.

6. **KPI polling** — `loadOverview()` is called every 30 seconds via `setInterval` so the 9 KPI
   cards stay fresh even when the user stays on the Overview tab.

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Single `main.py` file for entire backend | Zero configuration, instantly runnable, fits hackathon scope cleanly |
| In-memory data store (no database) | Eliminates setup friction; seed functions are deterministic and readable |
| WebSocket for telemetry, REST for everything else | WS is the right tool for push; REST is simpler and more cacheable for query endpoints |
| Vanilla JS frontend (no React/Vue) | No build step, no `npm install`, works by opening a file; keeps the demo frictionless |
| ECharts + Leaflet via CDN | Professional-grade visualisations with zero local dependencies |
| `_DISRUPTION_SPECS` data table | Separates domain data from constructor logic; mirrors `_build_shipments` pattern; all timestamps computed from single `_now()` call for consistency |
| Client-side sort (no re-fetch) | Sorting stores `_shipData` in JS memory and re-renders — instant response, zero server load |
| Telemetry pre-seed from REST API | User sees real data the moment the tab opens rather than waiting up to 5 s for first WS push |
| `requestAnimationFrame` resize for ECharts | ECharts must be resized after the tab panel becomes visible (`display:block`); rAF defers the resize to the next paint frame |

## API Reference

| Method | Endpoint | Query params | Description |
|---|---|---|---|
| `GET` | `/api/shipments` | `status`, `category`, `excursion_only` | All shipments, optionally filtered |
| `GET` | `/api/shipments/{id}` | — | Single shipment by ID |
| `GET` | `/api/fleet` | `status` | All fleet assets, optionally filtered |
| `GET` | `/api/fleet/{id}` | — | Single fleet asset by vehicle ID |
| `GET` | `/api/alerts` | `severity`, `unacknowledged_only` | All alerts, optionally filtered |
| `POST` | `/api/alerts/{id}/acknowledge` | — | Acknowledge an alert by ID |
| `GET` | `/api/disruptions` | `active_only` | All disruption events |
| `GET` | `/api/analytics/summary` | — | Aggregated KPI summary |
| `WS` | `/ws/telemetry` | — | Real-time IoT push stream |

Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI) when the server is running.

## IBM Technologies Used

- **IBM Bob:** Used throughout the development of this project as the AI coding assistant.
  IBM Bob was used to:
  - Refactor `_build_disruptions()` from a 57-line constructor list into the `_DISRUPTION_SPECS`
    data table pattern, eliminating the unused `shipments` parameter and ensuring timestamp consistency.
  - Diagnose and fix the HTML structural bug where all 5 tab panels were nested inside `#tab-overview`
    instead of being siblings of it — making all tabs invisible.
  - Implement the column-sortable shipments table (`_shipSort`, `_shipData`, `renderShipmentsRows()`).
  - Build the `loadTelemetry()` pre-seed function and the `_telemetryInited` ECharts guard.
  - Generate all project documentation, screenshot HTML files, and the PowerPoint presentation.
  - Write and maintain the full test suite in `test_main.py`.
