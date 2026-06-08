from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient

from main import app
from app.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.config import settings
from datetime import datetime, UTC

client = TestClient(app)


@patch("app.routers.auth.verify_google_token", new_callable=AsyncMock)
@patch("app.routers.auth.get_or_create_user", new_callable=AsyncMock)
def test_login_with_google(mock_get_user, mock_verify):
    mock_verify.return_value = {"email": "test@moctu.com"}
    mock_user = User(id=uuid4(), role="user", email="test@moctu.com")
    mock_get_user.return_value = mock_user

    response = client.post("/api/auth/google", json={"id_token": "valid_token"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


@patch("app.routers.auth.verify_google_token", new_callable=AsyncMock)
def test_login_with_google_invalid(mock_verify):
    mock_verify.side_effect = ValueError("Invalid token")
    response = client.post("/api/auth/google", json={"id_token": "invalid_token"})
    assert response.status_code == 401


@patch("app.routers.auth.decode_token")
@patch("app.routers.auth.get_user_by_id", new_callable=AsyncMock)
def test_refresh_token(mock_get_user, mock_decode):
    user_id = uuid4()
    mock_decode.return_value = {"type": "refresh", "sub": str(user_id)}
    mock_get_user.return_value = User(id=user_id, role="user")

    response = client.post("/api/auth/refresh", json={"refresh_token": "valid_refresh"})
    assert response.status_code == 200
    assert "access_token" in response.json()


@patch("app.routers.auth.decode_token")
def test_refresh_token_invalid_type(mock_decode):
    mock_decode.return_value = {"type": "access", "sub": str(uuid4())}
    response = client.post("/api/auth/refresh", json={"refresh_token": "valid_access"})
    assert response.status_code == 401


@patch("app.routers.auth.decode_token")
def test_refresh_token_decode_error(mock_decode):
    mock_decode.side_effect = ValueError("Hết hạn")
    response = client.post("/api/auth/refresh", json={"refresh_token": "invalid"})
    assert response.status_code == 401


@patch("app.routers.auth.decode_token")
@patch("app.routers.auth.get_user_by_id", new_callable=AsyncMock)
def test_refresh_token_user_not_found(mock_get_user, mock_decode):
    user_id = uuid4()
    mock_decode.return_value = {"type": "refresh", "sub": str(user_id)}
    mock_get_user.return_value = None
    response = client.post("/api/auth/refresh", json={"refresh_token": "valid"})
    assert response.status_code == 401


def test_get_me():
    user_id = uuid4()

    async def override_get_current_user():
        u = User(id=user_id, email="test@moctu.com", display_name="Test", role="user")
        u.plants = []
        u.created_at = datetime.now(UTC)
        return u

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@moctu.com"
    app.dependency_overrides.clear()


def test_swagger_login():
    # Setup test env
    old_env = settings.app_env
    settings.app_env = "development"

    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_result = MagicMock()
    user = User(id=uuid4(), email="test@moctu.com", role="user")
    mock_result.scalar_one_or_none.return_value = user
    mock_db.execute.return_value = mock_result

    response = client.post(
        "/api/auth/swagger-login",
        data={"username": "test@moctu.com", "password": "user"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

    # Restore env
    settings.app_env = old_env
    app.dependency_overrides.clear()


def test_swagger_login_production():
    old_env = settings.app_env
    settings.app_env = "production"

    response = client.post(
        "/api/auth/swagger-login", data={"username": "test", "password": "pwd"}
    )
    assert response.status_code == 403

    settings.app_env = "development"

    # test without @
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None  # create new user
    mock_db.execute.return_value = mock_result

    response2 = client.post(
        "/api/auth/swagger-login", data={"username": "test", "password": "pwd"}
    )
    assert response2.status_code == 200

    # test change role
    user = User(id=uuid4(), email="admin@moctu.com", role="user")
    mock_result.scalar_one_or_none.return_value = user
    response3 = client.post(
        "/api/auth/swagger-login",
        data={"username": "admin@moctu.com", "password": "admin"},
    )
    assert response3.status_code == 200
    assert user.role == "admin"

    settings.app_env = old_env
    app.dependency_overrides.clear()
