"""Tarif API endpoint testleri."""


async def test_get_recipes(client):
    r = await client.get("/api/recipes/")
    assert r.status_code == 200
    data = r.json()
    assert "recipes" in data
    assert "total" in data


async def test_recommend_needs_ingredients(client):
    r = await client.post(
        "/api/recipes/recommend",
        json={"ingredients": []},
    )
    assert r.status_code == 400


async def test_recommend_with_ingredients(client):
    r = await client.post(
        "/api/recipes/recommend",
        json={"ingredients": ["soğan", "domates", "biber"]},
    )
    assert r.status_code == 200
    data = r.json()
    assert "recommendations" in data
    assert "search_method" in data
