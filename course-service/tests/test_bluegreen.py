"""Tests for the blue/green additions (Task 10.3HD)."""

import app.main as main


def test_health_reports_colour_and_version(client, monkeypatch):
    monkeypatch.setattr(main, "COLOUR", "green")
    monkeypatch.setattr(main, "APP_VERSION", "abc123")

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["colour"] == "green"
    assert body["version"] == "abc123"


def test_no_fault_by_default(client, admin_headers):
    assert main.DEMO_FAULT == "none"

    response = client.get("/courses", headers=admin_headers)

    assert response.status_code == 200


def test_broken_api_fails_api_but_not_health(client, admin_headers, monkeypatch):
    monkeypatch.setattr(main, "DEMO_FAULT", "broken-api")

    assert client.get("/health").status_code == 200
    assert client.get("/courses", headers=admin_headers).status_code == 500


def test_late_errors_start_after_threshold(client, admin_headers, monkeypatch):
    monkeypatch.setattr(main, "DEMO_FAULT", "late-errors")
    monkeypatch.setattr(main, "FAULT_AFTER_REQUESTS", 3)
    monkeypatch.setattr(main, "api_request_count", 0)

    first = [client.get("/courses", headers=admin_headers).status_code for _ in range(3)]
    later = [client.get("/courses", headers=admin_headers).status_code for _ in range(2)]

    assert first == [200, 200, 200]
    assert later == [500, 500]
    assert client.get("/health").status_code == 200


def test_simulated_errors_are_counted_by_prometheus(client, admin_headers, monkeypatch):
    monkeypatch.setattr(main, "DEMO_FAULT", "broken-api")

    client.get("/courses", headers=admin_headers)
    metrics = client.get("/metrics").text

    assert 'status="5xx"' in metrics
