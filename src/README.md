# Source Code — RapidDeploy

Supply Chain & Cold-Chain Operations Dashboard.

## Project Layout

```
/                           ← Repo root
├── main.py                 ← FastAPI application (API + WebSocket server)
├── static/
│   └── index.html          ← Single-page dashboard (vanilla HTML / JS / CSS)
├── src/
│   ├── README.md           ← This file
│   └── .env.example        ← Environment variable template
├── docs/
│   ├── architecture.md     ← System architecture overview
│   ├── setup-guide.md      ← How to run locally
│   ├── problem-statement.md
│   └── solution-overview.md
├── demo/                   ← Screenshots and demo video link
├── presentation/           ← Slide deck
├── test_main.py            ← pytest test suite
└── submission.yaml         ← Hackathon submission metadata
```

## Backend — `main.py`

Single-file FastAPI app. Key sections:

| Section | What it does |
|---|---|
| Enums / constants | `ShipmentStatus`, `FleetStatus`, `AlertSeverity`, `DisruptionType`, temperature thresholds |
| Pydantic models | `IoTReading`, `Shipment`, `FleetAsset`, `Alert`, `DisruptionEvent`, `AnalyticsSummary` |
| Seed data helpers | `_build_shipments()`, `_build_fleet()`, `_build_alerts()`, `_build_disruptions()` |
| WebSocket manager | `_ConnectionManager` + `_telemetry_emitter()` background task (5 s interval) |
| REST routes | `GET /api/shipments`, `/api/fleet`, `/api/alerts`, `/api/disruptions`, `/api/analytics/summary` |
| WebSocket route | `WS /ws/telemetry` — live IoT reading push to all connected clients |
| Static files | `static/` mounted at `/` (catch-all, served last) |

## Frontend — `static/index.html`

Vanilla HTML + JavaScript single-page dashboard. Tabs:

- **Dashboard** — KPI cards, fleet summary, top alerts
- **Shipments** — sortable table of all active shipments with excursion badges
- **Fleet** — fleet asset list with status indicators
- **Alerts** — filterable alert feed with one-click acknowledgement
- **Disruptions** — supply-chain disruption events with impact score bars
- **Live Telemetry** — real-time IoT temperature/humidity line chart (WebSocket feed)

## Environment Variables

Copy `src/.env.example` → `.env` in the repo root and fill in your values.
See [`docs/setup-guide.md`](../docs/setup-guide.md) for full setup instructions.
