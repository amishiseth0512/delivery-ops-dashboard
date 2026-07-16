import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext

from app.main import app
from app.database import Base, get_db
from app.models import User, UserRole

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Session = sessionmaker(bind=engine)
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def override_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def seed_users(fresh_db):
    db = Session()
    db.add(User(name="Alice", email="alice@test.com", hashed_password=pwd.hash("pass123"), role=UserRole.dispatcher))
    db.add(User(name="Bob", email="bob@test.com", hashed_password=pwd.hash("pass456"), role=UserRole.driver))
    db.commit()
    db.close()


def get_token(email, password):
    res = client.post("/login", json={"email": email, "password": password})
    return res.json()["access_token"]


def test_login_valid(seed_users):
    res = client.post("/login", json={"email": "alice@test.com", "password": "pass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(seed_users):
    res = client.post("/login", json={"email": "alice@test.com", "password": "wrong"})
    assert res.status_code == 401


def test_login_unknown_email():
    res = client.post("/login", json={"email": "nobody@test.com", "password": "pass123"})
    assert res.status_code == 401


def test_get_orders_no_token():
    res = client.get("/orders/")
    assert res.status_code == 401


def test_get_orders_with_token(seed_users):
    tok = get_token("alice@test.com", "pass123")
    res = client.get("/orders/", headers={"Authorization": f"Bearer {tok}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_create_order(seed_users):
    tok = get_token("alice@test.com", "pass123")
    res = client.post(
        "/orders/",
        json={"description": "Test order"},
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert res.status_code == 201
    assert res.json()["description"] == "Test order"


def test_reassign_as_driver(seed_users):
    d_tok = get_token("alice@test.com", "pass123")
    order = client.post(
        "/orders/",
        json={"description": "Test order"},
        headers={"Authorization": f"Bearer {d_tok}"},
    ).json()

    b_tok = get_token("bob@test.com", "pass456")
    res = client.patch(
        f"/orders/{order['id']}/reassign",
        json={"driver_id": 1},
        headers={"Authorization": f"Bearer {b_tok}"},
    )
    assert res.status_code == 403


def test_ai_assistant_empty_question(seed_users, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    tok = get_token("alice@test.com", "pass123")
    res = client.post(
        "/api/ai/assistant",
        json={"question": "   "},
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert res.status_code == 400


def test_ai_assistant_without_api_key(seed_users, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    tok = get_token("alice@test.com", "pass123")
    res = client.post(
        "/api/ai/assistant",
        json={"question": "Which deliveries need attention?"},
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert res.status_code == 503


def test_ai_assistant_success(seed_users, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    class FakeMessage:
        content = "Order #1 needs attention because it has been in transit the longest."

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, *args, **kwargs):
            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        def __init__(self, api_key):
            self.chat = FakeChat()

    monkeypatch.setattr("app.services.ai_assistant.OpenAI", FakeClient)

    tok = get_token("alice@test.com", "pass123")
    res = client.post(
        "/api/ai/assistant",
        json={"question": "Which orders need attention?"},
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "answer" in body
    assert "generated_at" in body
