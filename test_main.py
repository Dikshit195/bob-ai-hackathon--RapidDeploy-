import pytest
from fastapi.testclient import TestClient

from main import app, SHIPMENTS, FLEET, ALERTS

client = TestClient(app)

# ---------------------------------------------------------------------------
# Shipments Endpoint Tests
# ---------------------------------------------------------------------------

def test_get_all_shipments():
    """Verify fetching all shipments returns 200 and a non-empty list."""
    response = client.get("/api/shipments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(SHIPMENTS)
    # Check payload structure on first item
    first = data[0]
    assert "shipment_id" in first
    assert "latest_reading" in first
    assert "temperature_c" in first["latest_reading"]


def test_get_shipment_by_id_success():
    """Verify fetching a specific shipment by valid ID returns 200."""
    target_id = SHIPMENTS[0].shipment_id
    response = client.get(f"/api/shipments/{target_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["shipment_id"] == target_id


def test_get_shipment_by_id_not_found():
    """Verify non-existent shipment returns 404 error state."""
    response = client.get("/api/shipments/SH-99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Shipment SH-99999 not found"


def test_filter_shipments_by_status():
    """Verify filtering shipments by status query parameter."""
    response = client.get("/api/shipments?status=in_transit")
    assert response.status_code == 200
    data = response.json()
    assert all(s["status"] == "in_transit" for s in data)


# ---------------------------------------------------------------------------
# Fleet Endpoint Tests
# ---------------------------------------------------------------------------

def test_get_fleet():
    """Verify fleet endpoint payload integrity."""
    response = client.get("/api/fleet")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(FLEET)
    assert "vehicle_id" in data[0]


def test_get_fleet_vehicle_not_found():
    """Verify 404 for invalid vehicle ID."""
    response = client.get("/api/fleet/VH-INVALID")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Alerts & Acknowledgment Tests
# ---------------------------------------------------------------------------

def test_acknowledge_alert_success():
    """Verify alert acknowledgment updates state properly."""
    target_alert = ALERTS[0]
    response = client.post(f"/api/alerts/{target_alert.alert_id}/acknowledge")
    assert response.status_code == 200
    assert response.json() == {
        "status": "acknowledged",
        "alert_id": target_alert.alert_id,
    }

    # Confirm state update
    res = client.get("/api/alerts")
    updated_alerts = res.json()
    ack_alert = next(a for a in updated_alerts if a["alert_id"] == target_alert.alert_id)
    assert ack_alert["acknowledged"] is True


def test_acknowledge_alert_not_found():
    """Verify 404 when acknowledging missing alert."""
    response = client.post("/api/alerts/ALT-INVALID/acknowledge")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Analytics & Disruptions Tests
# ---------------------------------------------------------------------------

def test_analytics_summary():
    """Verify analytics summary KPIs are calculated correctly."""
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_shipments" in data
    assert "fleet_utilisation_pct" in data
    assert data["total_shipments"] == len(SHIPMENTS)


def test_disruptions_endpoint():
    """Verify disruption events endpoint response."""
    response = client.get("/api/disruptions?active_only=true")
    assert response.status_code == 200
    data = response.json()
    assert all(d["active"] is True for d in data)