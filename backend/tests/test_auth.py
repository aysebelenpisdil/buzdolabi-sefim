"""Auth (magic link, session) endpoint testleri."""


async def test_magic_link_request(client):
    r = await client.post(
        "/api/auth/magic-link",
        json={"email": "test@example.com"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert "dev_token" in data  # development modda token döner


async def test_magic_link_invalid_email(client):
    r = await client.post(
        "/api/auth/magic-link",
        json={"email": "gecersiz"},
    )
    assert r.status_code == 422


async def test_verify_magic_link(client):
    # Önce magic link al
    r1 = await client.post(
        "/api/auth/magic-link",
        json={"email": "verify-test@example.com"},
    )
    assert r1.status_code == 200
    token = r1.json().get("dev_token")
    assert token

    # Token ile doğrula
    r2 = await client.post(
        "/api/auth/verify",
        json={"token": token},
    )
    assert r2.status_code == 200
    data = r2.json()
    assert data["user"]["email"] == "verify-test@example.com"
    assert "session_id" in r2.cookies or "Set-Cookie" in str(r2.headers)


async def test_me_requires_auth(client):
    r = await client.get("/api/auth/me")
    assert r.status_code == 401
