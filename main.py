"""
RapidDeploy — Supply Chain Disruption & IoT Cold-Chain Temperature Excursion Analysis
FastAPI backend that exposes:
  • /api/shipments         — active shipments with live IoT temperature readings
  • /api/fleet             — fleet assets and idle-status summary
  • /api/alerts            — temperature excursion & disruption alerts
  • /api/disruptions       — supply-chain disruption events
  • /api/analytics/summary — aggregated KPI summary
  • /ws/telemetry          — WebSocket stream for real-time IoT telemetry push
Static files in ./static are served at /
"""

from __future__ import annotations

import asyncio
import json
import math
import random
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Launch background telemetry loop
    telemetry_task = asyncio.create_task(_telemetry_emitter())
    yield
    # Shutdown: Clean up background tasks
    telemetry_task.cancel()

app = FastAPI(
    title="RapidDeploy — Supply Chain & Cold-Chain API",
    lifespan=lifespan,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Enums / constants
# ---------------------------------------------------------------------------

class ShipmentStatus(str, Enum):
    IN_TRANSIT = "in_transit"
    DELAYED = "delayed"
    DELIVERED = "delivered"
    AT_RISK = "at_risk"


class FleetStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DisruptionType(str, Enum):
    WEATHER = "weather"
    PORT_CONGESTION = "port_congestion"
    CUSTOMS_DELAY = "customs_delay"
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    TEMP_EXCURSION = "temp_excursion"
    SUPPLIER_OUTAGE = "supplier_outage"


# Temperature thresholds (°C) per product category
TEMP_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "frozen":      {"min": -25.0, "max": -15.0},
    "refrigerated": {"min": 2.0,  "max": 8.0},
    "ambient":     {"min": 15.0,  "max": 30.0},
    "pharma":      {"min": 2.0,   "max": 8.0},
}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class IoTReading(BaseModel):
    sensor_id: str
    timestamp: datetime
    temperature_c: float
    humidity_pct: float
    latitude: float
    longitude: float
    battery_pct: float


class Shipment(BaseModel):
    shipment_id: str
    origin: str
    destination: str
    carrier: str
    vehicle_id: str
    product_category: str
    product_name: str
    status: ShipmentStatus
    eta: datetime
    departure_time: datetime
    current_location: str
    latest_reading: IoTReading
    temp_excursion: bool
    excursion_duration_min: int
    route_progress_pct: float


class FleetAsset(BaseModel):
    vehicle_id: str
    vehicle_type: str
    driver: Optional[str]
    status: FleetStatus
    location: str
    latitude: float
    longitude: float
    last_active: datetime
    idle_duration_min: int
    fuel_pct: float
    assigned_shipment: Optional[str]
    mileage_km: int


class Alert(BaseModel):
    alert_id: str
    severity: AlertSeverity
    type: str
    shipment_id: Optional[str]
    vehicle_id: Optional[str]
    message: str
    timestamp: datetime
    acknowledged: bool


class DisruptionEvent(BaseModel):
    disruption_id: str
    type: DisruptionType
    affected_shipments: List[str]
    region: str
    description: str
    impact_score: float = Field(..., ge=0, le=10)
    started_at: datetime
    estimated_resolution: datetime
    active: bool


class AnalyticsSummary(BaseModel):
    total_shipments: int
    in_transit: int
    delayed: int
    at_risk: int
    delivered_today: int
    temp_excursions_active: int
    avg_excursion_duration_min: float
    idle_fleet_count: int
    total_fleet: int
    fleet_utilisation_pct: float
    active_disruptions: int
    critical_alerts: int
    generated_at: datetime


# ---------------------------------------------------------------------------
# Seed data helpers
# ---------------------------------------------------------------------------

_RNG = random.Random(42)

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _past(minutes: int) -> datetime:
    return _now() - timedelta(minutes=minutes)


def _future(hours: int) -> datetime:
    return _now() + timedelta(hours=hours)


def _iot(sensor_id: str, lat: float, lon: float, category: str) -> IoTReading:
    thresholds = TEMP_THRESHOLDS[category]
    mid = (thresholds["min"] + thresholds["max"]) / 2
    spread = (thresholds["max"] - thresholds["min"]) / 2 + 3  # occasionally exceed
    temp = mid + _RNG.uniform(-spread, spread)
    return IoTReading(
        sensor_id=sensor_id,
        timestamp=_past(_RNG.randint(1, 10)),
        temperature_c=round(temp, 2),
        humidity_pct=round(_RNG.uniform(40, 90), 1),
        latitude=round(lat + _RNG.uniform(-0.5, 0.5), 5),
        longitude=round(lon + _RNG.uniform(-0.5, 0.5), 5),
        battery_pct=round(_RNG.uniform(20, 100), 1),
    )


def _is_excursion(reading: IoTReading, category: str) -> bool:
    t = TEMP_THRESHOLDS[category]
    return reading.temperature_c < t["min"] or reading.temperature_c > t["max"]


# ---------------------------------------------------------------------------
# In-memory data store (simulates a live database / message broker)
# ---------------------------------------------------------------------------

SHIPMENTS: List[Shipment] = []
FLEET: List[FleetAsset] = []
ALERTS: List[Alert] = []
DISRUPTIONS: List[DisruptionEvent] = []


def _build_shipments() -> List[Shipment]:
    raw = [
        ("SH-001", "Mumbai",    "Delhi",     "BlueDart",   "VH-101", "refrigerated", "Dairy Products",       ShipmentStatus.IN_TRANSIT, 6,  120, "Surat",         28.67, 77.21, 60),
        ("SH-002", "Chennai",   "Bangalore", "DTDC",       "VH-102", "frozen",       "Ice Cream",            ShipmentStatus.DELAYED,    3,  240, "Vellore",       12.97, 77.59, 35),
        ("SH-003", "Kolkata",   "Hyderabad", "Delhivery",  "VH-103", "pharma",       "Vaccines",             ShipmentStatus.AT_RISK,    8,  300, "Bhubaneswar",   17.38, 78.48, 80),
        ("SH-004", "Pune",      "Mumbai",    "Ecom Express","VH-104","ambient",      "Packaged Snacks",      ShipmentStatus.IN_TRANSIT, 2,  60,  "Lonavala",      18.52, 73.86, 90),
        ("SH-005", "Ahmedabad", "Jaipur",    "BlueDart",   "VH-105", "refrigerated", "Fresh Juice",          ShipmentStatus.IN_TRANSIT, 5,  90,  "Udaipur",       26.91, 75.79, 55),
        ("SH-006", "Delhi",     "Lucknow",   "Delhivery",  "VH-106", "frozen",       "Frozen Vegetables",    ShipmentStatus.DELAYED,    4,  180, "Agra",          26.85, 80.95, 45),
        ("SH-007", "Hyderabad", "Vijayawada","DTDC",       "VH-107", "pharma",       "Insulin",              ShipmentStatus.AT_RISK,    7,  420, "Nalgonda",      16.51, 80.62, 70),
        ("SH-008", "Bangalore", "Mysore",    "Ecom Express","VH-108","ambient",      "Electronics",          ShipmentStatus.IN_TRANSIT, 1,  30,  "Mandya",        12.30, 76.65, 95),
        ("SH-009", "Jaipur",    "Jodhpur",   "BlueDart",   "VH-109", "refrigerated", "Paneer",               ShipmentStatus.IN_TRANSIT, 3,  150, "Ajmer",         26.29, 73.02, 65),
        ("SH-010", "Mumbai",    "Goa",       "DTDC",       "VH-110", "frozen",       "Seafood",              ShipmentStatus.AT_RISK,    9,  360, "Pune",          15.49, 73.82, 40),
    ]
    shipments = []
    for (sid, orig, dest, carrier, vid, cat, prod, status, eta_h, dep_m, loc, lat, lon, prog) in raw:
        reading = _iot(f"SNS-{sid}", lat, lon, cat)
        excursion = _is_excursion(reading, cat)
        shipments.append(Shipment(
            shipment_id=sid,
            origin=orig,
            destination=dest,
            carrier=carrier,
            vehicle_id=vid,
            product_category=cat,
            product_name=prod,
            status=status,
            eta=_future(eta_h),
            departure_time=_past(dep_m),
            current_location=loc,
            latest_reading=reading,
            temp_excursion=excursion,
            excursion_duration_min=_RNG.randint(0, 45) if excursion else 0,
            route_progress_pct=float(prog),
        ))
    return shipments


def _build_fleet() -> List[FleetAsset]:
    raw = [
        ("VH-101", "Refrigerated Truck", "Ramesh Kumar",   FleetStatus.ACTIVE,      "Surat",       21.17, 72.83,  0,   85, "SH-001"),
        ("VH-102", "Freezer Van",        "Suresh Patel",   FleetStatus.ACTIVE,      "Vellore",     12.92, 79.13,  0,   60, "SH-002"),
        ("VH-103", "Pharma Reefer",      "Anil Sharma",    FleetStatus.ACTIVE,      "Bhubaneswar", 20.29, 85.82,  0,   90, "SH-003"),
        ("VH-104", "Standard Truck",     "Priya Singh",    FleetStatus.ACTIVE,      "Lonavala",    18.75, 73.40,  0,   75, "SH-004"),
        ("VH-105", "Refrigerated Truck", "Vijay Rao",      FleetStatus.ACTIVE,      "Udaipur",     24.57, 73.70,  0,   55, "SH-005"),
        ("VH-106", "Freezer Van",        "Deepak Verma",   FleetStatus.ACTIVE,      "Agra",        27.17, 78.01,  0,   70, "SH-006"),
        ("VH-107", "Pharma Reefer",      "Nisha Joshi",    FleetStatus.ACTIVE,      "Nalgonda",    17.05, 79.26,  0,   80, "SH-007"),
        ("VH-108", "Standard Truck",     "Karan Mehta",    FleetStatus.ACTIVE,      "Mandya",      12.52, 76.89,  0,   95, "SH-008"),
        ("VH-109", "Refrigerated Truck", "Sunita Reddy",   FleetStatus.ACTIVE,      "Ajmer",       26.45, 74.64,  0,   65, "SH-009"),
        ("VH-110", "Freezer Van",        "Mohan Das",      FleetStatus.ACTIVE,      "Pune",        18.52, 73.86,  0,   40, "SH-010"),
        ("VH-111", "Standard Truck",     None,             FleetStatus.IDLE,        "Mumbai Depot",19.07, 72.87,  95,  30, None),
        ("VH-112", "Refrigerated Truck", None,             FleetStatus.IDLE,        "Delhi Depot", 28.63, 77.22,  210, 50, None),
        ("VH-113", "Freezer Van",        None,             FleetStatus.IDLE,        "Chennai Depot",13.08,80.27,  30,  90, None),
        ("VH-114", "Pharma Reefer",      None,             FleetStatus.MAINTENANCE, "Bangalore HQ",12.97,77.59,  480, 20, None),
        ("VH-115", "Standard Truck",     None,             FleetStatus.OFFLINE,     "Kolkata Depot",22.57,88.36,  720, 5,  None),
    ]
    assets = []
    for (vid, vtype, driver, status, loc, lat, lon, idle_m, fuel, assigned) in raw:
        assets.append(FleetAsset(
            vehicle_id=vid,
            vehicle_type=vtype,
            driver=driver,
            status=status,
            location=loc,
            latitude=lat,
            longitude=lon,
            last_active=_past(idle_m if idle_m else _RNG.randint(1, 30)),
            idle_duration_min=idle_m,
            fuel_pct=float(fuel),
            assigned_shipment=assigned,
            mileage_km=_RNG.randint(50_000, 250_000),
        ))
    return assets


def _build_alerts(shipments: List[Shipment]) -> List[Alert]:
    alerts = []
    for i, s in enumerate(shipments):
        if s.temp_excursion:
            t = s.latest_reading.temperature_c
            thresh = TEMP_THRESHOLDS[s.product_category]
            direction = "above maximum" if t > thresh["max"] else "below minimum"
            alerts.append(Alert(
                alert_id=f"ALT-T{i+1:03d}",
                severity=AlertSeverity.CRITICAL if s.status == ShipmentStatus.AT_RISK else AlertSeverity.WARNING,
                type="temperature_excursion",
                shipment_id=s.shipment_id,
                vehicle_id=s.vehicle_id,
                message=(
                    f"Temp excursion on {s.shipment_id}: {t}°C is {direction} "
                    f"({thresh['min']}–{thresh['max']}°C) for {s.product_name}"
                ),
                timestamp=s.latest_reading.timestamp,
                acknowledged=False,
            ))
        if s.status == ShipmentStatus.DELAYED:
            alerts.append(Alert(
                alert_id=f"ALT-D{i+1:03d}",
                severity=AlertSeverity.WARNING,
                type="shipment_delayed",
                shipment_id=s.shipment_id,
                vehicle_id=s.vehicle_id,
                message=f"Shipment {s.shipment_id} ({s.product_name}) is delayed — ETA pushed by 2h+",
                timestamp=_past(_RNG.randint(30, 120)),
                acknowledged=False,
            ))
    return alerts


# Each row: (id, type, affected_shipments, region, description, impact_score, started_at_min, resolution, active)
# resolution: positive int → hours in the future; negative int → minutes in the past (already resolved).
_DISRUPTION_SPECS: List[tuple] = [
    ("DIS-001", DisruptionType.WEATHER,          ["SH-002", "SH-006"],          "North India",        "Heavy fog and low visibility on NH-44 corridor causing multi-hour delays.",                7.5,  180,   6,    True),
    ("DIS-002", DisruptionType.TEMP_EXCURSION,   ["SH-003", "SH-007", "SH-010"],"East & South India", "Reefer unit malfunctions detected on three pharma/frozen routes; quality at risk.",       9.2,   90,   4,    True),
    ("DIS-003", DisruptionType.PORT_CONGESTION,  ["SH-010"],                    "Goa Port",           "Port congestion delaying seafood shipment clearance by 12+ hours.",                       6.0,  300,  12,    True),
    ("DIS-004", DisruptionType.VEHICLE_BREAKDOWN,["SH-002"],                    "Vellore, Tamil Nadu","Freezer van VH-102 reported compressor failure; replacement dispatched.",                  8.0,   60,   3,    True),
    ("DIS-005", DisruptionType.CUSTOMS_DELAY,    [],                            "Chennai Port",       "Customs documentation backlog cleared; no current active impact.",                        2.0, 1440, -120,   False),
]


def _build_disruptions() -> List[DisruptionEvent]:
    now = _now()
    return [
        DisruptionEvent(
            disruption_id=did,
            type=dtype,
            affected_shipments=affected,
            region=region,
            description=desc,
            impact_score=score,
            started_at=now - timedelta(minutes=start_m),
            estimated_resolution=(
                now + timedelta(hours=res) if res >= 0
                else now - timedelta(minutes=-res)
            ),
            active=active,
        )
        for (did, dtype, affected, region, desc, score, start_m, res, active) in _DISRUPTION_SPECS
    ]


# Populate on startup
SHIPMENTS = _build_shipments()
FLEET     = _build_fleet()
ALERTS    = _build_alerts(SHIPMENTS)
DISRUPTIONS = _build_disruptions()


# ---------------------------------------------------------------------------
# WebSocket connection manager
# ---------------------------------------------------------------------------

class _ConnectionManager:
    def __init__(self) -> None:
        self._connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._connections = [c for c in self._connections if c is not ws]

    async def broadcast(self, data: Dict[str, Any]) -> None:
        dead: List[WebSocket] = []
        for ws in list(self._connections):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


_manager = _ConnectionManager()


async def _telemetry_emitter() -> None:
    """Background task: every 5 s emit simulated IoT readings for a random shipment."""
    while True:
        await asyncio.sleep(5)
        if not SHIPMENTS:
            continue
        s = _RNG.choice(SHIPMENTS)
        new_reading = _iot(s.latest_reading.sensor_id, s.latest_reading.latitude, s.latest_reading.longitude, s.product_category)
        s.latest_reading = new_reading
        s.temp_excursion = _is_excursion(new_reading, s.product_category)
        payload = {
            "event": "iot_reading",
            "shipment_id": s.shipment_id,
            "product": s.product_name,
            "category": s.product_category,
            "reading": {
                "sensor_id": new_reading.sensor_id,
                "timestamp": new_reading.timestamp.isoformat(),
                "temperature_c": new_reading.temperature_c,
                "humidity_pct": new_reading.humidity_pct,
                "latitude": new_reading.latitude,
                "longitude": new_reading.longitude,
                "battery_pct": new_reading.battery_pct,
            },
            "temp_excursion": s.temp_excursion,
            "thresholds": TEMP_THRESHOLDS[s.product_category],
        }
        await _manager.broadcast(payload)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/index.html")


@app.get("/api/shipments", response_model=List[Shipment], tags=["Shipments"])
async def get_shipments(
    status: Optional[ShipmentStatus] = None,
    category: Optional[str] = None,
    excursion_only: bool = False,
):
    """Return all active shipments, with optional filters."""
    result = list(SHIPMENTS)
    if status:
        result = [s for s in result if s.status == status]
    if category:
        result = [s for s in result if s.product_category == category]
    if excursion_only:
        result = [s for s in result if s.temp_excursion]
    return result


@app.get("/api/shipments/{shipment_id}", response_model=Shipment, tags=["Shipments"])
async def get_shipment(shipment_id: str):
    """Return a single shipment by ID."""
    for s in SHIPMENTS:
        if s.shipment_id == shipment_id:
            return s
    raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")


@app.get("/api/fleet", response_model=List[FleetAsset], tags=["Fleet"])
async def get_fleet(status: Optional[FleetStatus] = None):
    """Return all fleet assets, optionally filtered by status."""
    if status:
        return [v for v in FLEET if v.status == status]
    return FLEET


@app.get("/api/fleet/{vehicle_id}", response_model=FleetAsset, tags=["Fleet"])
async def get_fleet_asset(vehicle_id: str):
    """Return a single fleet asset by vehicle ID."""
    for v in FLEET:
        if v.vehicle_id == vehicle_id:
            return v
    raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")


@app.get("/api/alerts", response_model=List[Alert], tags=["Alerts"])
async def get_alerts(
    severity: Optional[AlertSeverity] = None,
    unacknowledged_only: bool = False,
):
    """Return all alerts, optionally filtered by severity or acknowledgement state."""
    result = list(ALERTS)
    if severity:
        result = [a for a in result if a.severity == severity]
    if unacknowledged_only:
        result = [a for a in result if not a.acknowledged]
    return result


@app.post("/api/alerts/{alert_id}/acknowledge", tags=["Alerts"])
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert by ID."""
    for a in ALERTS:
        if a.alert_id == alert_id:
            a.acknowledged = True
            return {"status": "acknowledged", "alert_id": alert_id}
    raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")


@app.get("/api/disruptions", response_model=List[DisruptionEvent], tags=["Disruptions"])
async def get_disruptions(active_only: bool = False):
    """Return supply-chain disruption events."""
    if active_only:
        return [d for d in DISRUPTIONS if d.active]
    return DISRUPTIONS


@app.get("/api/analytics/summary", response_model=AnalyticsSummary, tags=["Analytics"])
async def get_analytics_summary():
    """Return aggregated KPI summary across shipments and fleet."""
    in_transit   = sum(1 for s in SHIPMENTS if s.status == ShipmentStatus.IN_TRANSIT)
    delayed      = sum(1 for s in SHIPMENTS if s.status == ShipmentStatus.DELAYED)
    at_risk      = sum(1 for s in SHIPMENTS if s.status == ShipmentStatus.AT_RISK)
    delivered    = sum(1 for s in SHIPMENTS if s.status == ShipmentStatus.DELIVERED)
    excursions   = [s for s in SHIPMENTS if s.temp_excursion]
    avg_exc_dur  = (
        sum(s.excursion_duration_min for s in excursions) / len(excursions)
        if excursions else 0.0
    )
    idle_fleet   = sum(1 for v in FLEET if v.status == FleetStatus.IDLE)
    active_fleet = sum(1 for v in FLEET if v.status == FleetStatus.ACTIVE)
    utilisation  = round(active_fleet / len(FLEET) * 100, 1) if FLEET else 0.0
    return AnalyticsSummary(
        total_shipments=len(SHIPMENTS),
        in_transit=in_transit,
        delayed=delayed,
        at_risk=at_risk,
        delivered_today=delivered,
        temp_excursions_active=len(excursions),
        avg_excursion_duration_min=round(avg_exc_dur, 1),
        idle_fleet_count=idle_fleet,
        total_fleet=len(FLEET),
        fleet_utilisation_pct=utilisation,
        active_disruptions=sum(1 for d in DISRUPTIONS if d.active),
        critical_alerts=sum(1 for a in ALERTS if a.severity == AlertSeverity.CRITICAL and not a.acknowledged),
        generated_at=_now(),
    )


# ---------------------------------------------------------------------------
# WebSocket — real-time IoT telemetry
# ---------------------------------------------------------------------------

@app.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket):
    """
    Connect to receive a continuous stream of live IoT temperature readings.
    Each message is a JSON object with event='iot_reading'.
    """
    await _manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; actual data pushed by _telemetry_emitter
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        _manager.disconnect(websocket)


# ---------------------------------------------------------------------------
# Static files (must be last — catch-all)
# ---------------------------------------------------------------------------

app.mount("/", StaticFiles(directory="static", html=True), name="static")
