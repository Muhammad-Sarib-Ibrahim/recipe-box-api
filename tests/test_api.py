import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session

# Use an in-memory SQLite DB for tests, so we never touch recipes.db
# and each test run starts with a clean slate.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_session_override():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = get_session_override


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


client = TestClient(app)


def register_and_login(email="user@test.com", password="secret123"):
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def test_register_creates_user_without_exposing_password():
    response = client.post(
        "/auth/register", json={"email": "a@test.com", "password": "secret123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "a@test.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email_fails():
    client.post("/auth/register", json={"email": "dup@test.com", "password": "secret123"})
    response = client.post(
        "/auth/register", json={"email": "dup@test.com", "password": "other123"}
    )
    assert response.status_code == 400


def test_login_wrong_password_fails():
    client.post("/auth/register", json={"email": "b@test.com", "password": "secret123"})
    response = client.post(
        "/auth/login", json={"email": "b@test.com", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_create_and_list_recipe():
    token = register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/recipes",
        json={"title": "Pasta", "ingredients": "pasta, tomato", "instructions": "Boil it."},
        headers=headers,
    )
    assert create_response.status_code == 200

    list_response = client.get("/recipes", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["title"] == "Pasta"


def test_recipes_require_authentication():
    response = client.get("/recipes")
    assert response.status_code == 401


def test_user_cannot_access_another_users_recipe():
    token_a = register_and_login(email="ownerA@test.com")
    token_b = register_and_login(email="ownerB@test.com")

    create_response = client.post(
        "/recipes",
        json={"title": "Secret Recipe", "ingredients": "x", "instructions": "y"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    recipe_id = create_response.json()["id"]

    response = client.get(
        f"/recipes/{recipe_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    # 404, not 403 — we don't reveal that the recipe exists at all
    assert response.status_code == 404


def test_update_and_delete_recipe():
    token = register_and_login(email="updater@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/recipes",
        json={"title": "Soup", "ingredients": "water", "instructions": "Heat it."},
        headers=headers,
    )
    recipe_id = create_response.json()["id"]

    update_response = client.put(
        f"/recipes/{recipe_id}", json={"title": "Tomato Soup"}, headers=headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Tomato Soup"

    delete_response = client.delete(f"/recipes/{recipe_id}", headers=headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/recipes/{recipe_id}", headers=headers)
    assert get_response.status_code == 404
