"""Health ve root endpoint testleri."""


async def test_health_ok(client):
    r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "database" in data
    assert data["database"]["type"] == "SQLite"


async def test_root(client):
    r = await client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert "version" in data
