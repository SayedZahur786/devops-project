def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_ready_checks_database(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ready"}


def test_metrics_endpoint_exposes_prometheus_format(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "http_requests" in resp.text
