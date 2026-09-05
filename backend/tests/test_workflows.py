import pytest

from .conftest import auth_headers


def setup_supply_chain(client, token):
    headers = auth_headers(token)
    assert client.post(
        "/api/farms",
        headers=headers,
        json={
            "id": "FRM-001",
            "name": "North Farm",
            "owner": "Farmer One",
            "location": "Nashik",
            "crop_type": "Grapes",
            "area_acres": 20,
            "expected_yield_tons": 50,
        },
    ).status_code == 200
    assert client.post(
        "/api/harvest-lots",
        headers=headers,
        json={"id": "LOT-001", "farm_id": "FRM-001", "weight_tons": 10},
    ).status_code == 200
    assert client.post(
        "/api/quality-inspections",
        headers=headers,
        json={"id": "QI-001", "lot_id": "LOT-001", "grade": "A", "passed": True},
    ).status_code == 200
    assert client.post(
        "/api/warehouses",
        headers=headers,
        json={"id": "WH-001", "name": "Main Warehouse", "location": "Nashik", "capacity_tons": 100},
    ).status_code == 200
    assert client.post(
        "/api/inventory",
        headers=headers,
        json={"id": "INV-001", "lot_id": "LOT-001", "warehouse_id": "WH-001", "quantity_tons": 10},
    ).status_code == 200
    assert client.post(
        "/api/buyers",
        headers=headers,
        json={
            "id": "BYR-001",
            "company_name": "Fresh Buyer",
            "country": "India",
            "contact_name": "Buyer One",
            "email": "buyer@example.com",
            "ltv": "$0",
        },
    ).status_code == 200
    return headers


def test_write_role_can_create_farm(client, admin_token):
    response = client.post(
        "/api/farms",
        headers=auth_headers(admin_token),
        json={
            "id": "FRM-002",
            "name": "South Farm",
            "owner": "Farmer Two",
            "location": "Pune",
            "crop_type": "Mango",
            "area_acres": 12,
            "expected_yield_tons": 30,
        },
    )
    assert response.status_code == 200
    assert response.json()["id"] == "FRM-002"


def test_quality_required_before_inventory(client, admin_token):
    headers = auth_headers(admin_token)
    client.post(
        "/api/farms",
        headers=headers,
        json={"id": "FRM-001", "name": "Farm", "owner": "Owner", "location": "Pune", "crop_type": "Mango", "area_acres": 10, "expected_yield_tons": 20},
    )
    client.post(
        "/api/harvest-lots",
        headers=headers,
        json={"id": "LOT-001", "farm_id": "FRM-001", "weight_tons": 5},
    )
    client.post(
        "/api/warehouses",
        headers=headers,
        json={"id": "WH-001", "name": "Warehouse", "location": "Pune", "capacity_tons": 50},
    )
    response = client.post(
        "/api/inventory",
        headers=headers,
        json={"id": "INV-001", "lot_id": "LOT-001", "warehouse_id": "WH-001", "quantity_tons": 5},
    )
    assert response.status_code == 400
    assert "quality inspection" in response.json()["detail"]


def test_order_reserves_inventory(client, admin_token):
    headers = setup_supply_chain(client, admin_token)
    response = client.post(
        "/api/orders",
        headers=headers,
        json={"id": "ORD-001", "buyer_id": "BYR-001", "lines": [{"inventory_batch_id": "INV-001", "quantity_tons": 4}]},
    )
    assert response.status_code == 200
    inventory = client.get("/api/inventory", headers=headers).json()[0]
    assert inventory["reserved_tons"] == 4
    assert inventory["available_tons"] == 6


def test_insufficient_inventory_is_rejected_without_reservation(client, admin_token):
    headers = setup_supply_chain(client, admin_token)
    response = client.post(
        "/api/orders",
        headers=headers,
        json={"id": "ORD-001", "buyer_id": "BYR-001", "lines": [{"inventory_batch_id": "INV-001", "quantity_tons": 11}]},
    )
    assert response.status_code == 400
    inventory = client.get("/api/inventory", headers=headers).json()[0]
    assert inventory["reserved_tons"] == 0
    assert client.get("/api/orders", headers=headers).json() == []


def test_cancel_order_releases_inventory(client, admin_token):
    headers = setup_supply_chain(client, admin_token)
    client.post(
        "/api/orders",
        headers=headers,
        json={"id": "ORD-001", "buyer_id": "BYR-001", "lines": [{"inventory_batch_id": "INV-001", "quantity_tons": 4}]},
    )
    response = client.patch("/api/orders/ORD-001/cancel", headers=headers)
    assert response.status_code == 200
    inventory = client.get("/api/inventory", headers=headers).json()[0]
    assert inventory["reserved_tons"] == 0
    assert response.json()["status"] == "Cancelled"


def test_shipment_requires_reserved_order(client, admin_token):
    headers = setup_supply_chain(client, admin_token)
    response = client.post(
        "/api/shipments",
        headers=headers,
        json={"id": "SHP-001", "order_id": "ORD-MISSING", "container_number": "MSCU1234567"},
    )
    assert response.status_code == 400
    assert "Order not found" in response.json()["detail"]


def test_shipment_and_order_state_transitions(client, admin_token):
    headers = setup_supply_chain(client, admin_token)
    client.post(
        "/api/orders",
        headers=headers,
        json={"id": "ORD-001", "buyer_id": "BYR-001", "lines": [{"inventory_batch_id": "INV-001", "quantity_tons": 4}]},
    )
    created = client.post(
        "/api/shipments",
        headers=headers,
        json={"id": "SHP-001", "order_id": "ORD-001", "container_number": "MSCU1234567"},
    )
    assert created.status_code == 200
    assert created.json()["status"] == "Planned"
    transit = client.patch("/api/shipments/SHP-001/advance", headers=headers)
    assert transit.status_code == 200
    assert transit.json()["status"] == "In Transit"
    delivered = client.patch("/api/shipments/SHP-001/advance", headers=headers)
    assert delivered.status_code == 200
    assert delivered.json()["status"] == "Delivered"
    order = client.get("/api/orders", headers=headers).json()[0]
    assert order["status"] == "Delivered"


def test_invalid_shipment_transition_is_rejected(client, admin_token):
    headers = setup_supply_chain(client, admin_token)
    client.post(
        "/api/orders",
        headers=headers,
        json={"id": "ORD-001", "buyer_id": "BYR-001", "lines": [{"inventory_batch_id": "INV-001", "quantity_tons": 4}]},
    )
    client.post(
        "/api/shipments",
        headers=headers,
        json={"id": "SHP-001", "order_id": "ORD-001", "container_number": "MSCU1234567"},
    )
    client.patch("/api/shipments/SHP-001/advance", headers=headers)
    client.patch("/api/shipments/SHP-001/advance", headers=headers)
    response = client.patch("/api/shipments/SHP-001/advance", headers=headers)
    assert response.status_code == 400


def test_traceability_returns_related_chain(client, admin_token):
    headers = setup_supply_chain(client, admin_token)
    client.post(
        "/api/orders",
        headers=headers,
        json={"id": "ORD-001", "buyer_id": "BYR-001", "lines": [{"inventory_batch_id": "INV-001", "quantity_tons": 4}]},
    )
    client.post(
        "/api/shipments",
        headers=headers,
        json={"id": "SHP-001", "order_id": "ORD-001", "container_number": "MSCU1234567"},
    )
    response = client.get("/api/traceability/LOT-001", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["farm"]["id"] == "FRM-001"
    assert body["harvest_lot"]["id"] == "LOT-001"
    assert body["quality_inspections"][0]["id"] == "QI-001"
    assert body["inventory_batches"][0]["id"] == "INV-001"
    assert body["orders"][0]["id"] == "ORD-001"
    assert body["shipments"][0]["id"] == "SHP-001"


def test_analytics_summary_uses_database_records(client, admin_token):
    headers = setup_supply_chain(client, admin_token)
    response = client.get("/api/analytics/summary", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["procurement_volume_tons"] == 10
    assert body["inventory_available_tons"] == 10
    assert body["warehouse_utilization"][0]["utilization_percent"] == 10


def test_duplicate_inventory_batch_is_rejected(client, admin_token):
    headers = setup_supply_chain(client, admin_token)
    response = client.post(
        "/api/inventory",
        headers=headers,
        json={"id": "INV-002", "lot_id": "LOT-001", "warehouse_id": "WH-001", "quantity_tons": 2},
    )
    assert response.status_code == 400
