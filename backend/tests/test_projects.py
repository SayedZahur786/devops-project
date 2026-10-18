def test_create_project(client):
    resp = client.post(
        "/api/projects",
        json={
            "title": "RaktSetu",
            "team_name": "BloodLine",
            "hackathon": "Goa Hacks",
            "track": "healthtech",
            "status": "submitted",
            "priority": "medium",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "RaktSetu"
    assert body["status"] == "submitted"
    assert body["id"] >= 1


def test_create_project_rejects_bad_status(client):
    resp = client.post(
        "/api/projects",
        json={
            "title": "Bad",
            "team_name": "X",
            "hackathon": "Y",
            "status": "archived",
        },
    )
    assert resp.status_code == 422


def test_list_and_filter_projects(client, sample_project):
    all_projects = client.get("/api/projects").json()
    assert len(all_projects) == 1
    building = client.get("/api/projects", params={"status": "building"}).json()
    assert len(building) == 1
    won = client.get("/api/projects", params={"status": "won"}).json()
    assert won == []


def test_get_update_delete_project(client, sample_project):
    pid = sample_project["id"]

    got = client.get(f"/api/projects/{pid}")
    assert got.status_code == 200
    assert got.json()["team_name"] == "ChainRunners"

    updated = client.put(f"/api/projects/{pid}", json={"status": "won", "priority": "low"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "won"
    assert updated.json()["priority"] == "low"

    deleted = client.delete(f"/api/projects/{pid}")
    assert deleted.status_code == 204
    assert client.get(f"/api/projects/{pid}").status_code == 404


def test_update_missing_project_returns_404(client):
    resp = client.put("/api/projects/9999", json={"status": "won"})
    assert resp.status_code == 404


def test_stats_endpoint_counts(client, sample_project):
    stats = client.get("/api/projects/stats").json()
    assert stats["total"] == 1
    assert stats["by_status"]["building"] == 1
    assert stats["high_priority_open"] == 1
    assert "Zyura" in stats["upcoming_deadlines"]
