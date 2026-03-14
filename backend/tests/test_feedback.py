"""Feedback endpoint testleri - auth gerekli."""


async def test_interaction_requires_auth(client):
    r = await client.post(
        "/api/feedback/interaction",
        json={"recipe_title": "Karnıyarık", "interaction_type": "like"},
    )
    assert r.status_code == 401


async def test_consumption_requires_auth(client):
    r = await client.post(
        "/api/feedback/consumption",
        json={
            "recipe_title": "Karnıyarık",
            "meal_type": "dinner",
            "portion_size": 1.0,
        },
    )
    assert r.status_code == 401


async def test_features_requires_auth(client):
    r = await client.get("/api/feedback/features")
    assert r.status_code == 401


async def test_feedback_flow_with_auth(client):
    # 1. Magic link al
    r1 = await client.post(
        "/api/auth/magic-link",
        json={"email": "feedback-test@example.com"},
    )
    assert r1.status_code == 200
    token = r1.json().get("dev_token")
    assert token

    # 2. Doğrula - cookie set edilir
    r2 = await client.post("/api/auth/verify", json={"token": token})
    assert r2.status_code == 200

    # 3. Etkileşim kaydet
    r3 = await client.post(
        "/api/feedback/interaction",
        json={
            "recipe_title": "Karnıyarık",
            "interaction_type": "like",
            "context_ingredients": ["patlıcan", "kıyma"],
        },
    )
    assert r3.status_code == 200

    # 4. Tüketim kaydet
    r4 = await client.post(
        "/api/feedback/consumption",
        json={
            "recipe_title": "Karnıyarık",
            "meal_type": "dinner",
            "portion_size": 1.5,
        },
    )
    assert r4.status_code == 200

    # 5. Özellikleri getir
    r5 = await client.get("/api/feedback/features")
    assert r5.status_code == 200
    data = r5.json()
    assert data["total_likes"] >= 1
    assert data["avg_portion"] == 1.5
