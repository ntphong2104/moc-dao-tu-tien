import bcrypt
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from main import app
from app.database import get_db
from app.services.auth_service import create_device_token

client = TestClient(app)


@pytest.fixture
def valid_device_token():
    return create_device_token("TEST_PLANT")


def test_authenticate_device_success():
    # Mock DB
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_result = MagicMock()
    mock_device = MagicMock()
    mock_device.verify_hash = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode("utf-8")
    mock_result.scalar_one_or_none.return_value = mock_device
    mock_db.execute.return_value = mock_result

    response = client.post(
        "/api/devices/TEST_PLANT/auth",
        json={"verify_code": "123456"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    app.dependency_overrides.clear()


def test_authenticate_device_not_found():
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    response = client.post(
        "/api/devices/TEST_PLANT/auth",
        json={"verify_code": "123456"},
    )
    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_authenticate_device_wrong_code():
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_result = MagicMock()
    mock_device = MagicMock()
    mock_device.verify_hash = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode("utf-8")
    mock_result.scalar_one_or_none.return_value = mock_device
    mock_db.execute.return_value = mock_result

    response = client.post(
        "/api/devices/TEST_PLANT/auth",
        json={"verify_code": "654321"},
    )
    assert response.status_code == 401
    app.dependency_overrides.clear()


@patch("app.routers.devices.process_telemetry", new_callable=AsyncMock)
def test_receive_telemetry_success(mock_process, valid_device_token):
    mock_process.return_value = {
        "status": "success",
        "exp_awarded": True,
        "message": "OK",
    }
    response = client.post(
        "/api/devices/TEST_PLANT/telemetry",
        json={"token": valid_device_token, "sensors": [{"key": "light", "value": 100}]},
    )
    assert response.status_code == 200, response.json()
    assert response.json()["exp_awarded"] is True


@patch("app.routers.devices.process_telemetry", new_callable=AsyncMock)
def test_receive_telemetry_invalid_token(mock_process):
    response = client.post(
        "/api/devices/TEST_PLANT/telemetry",
        json={"token": "invalid_token", "sensors": [{"key": "light", "value": 100}]},
    )
    assert response.status_code == 401
    assert not mock_process.called


@patch("app.routers.devices.process_telemetry", new_callable=AsyncMock)
def test_receive_telemetry_wrong_plant_token(mock_process):
    wrong_token = create_device_token("OTHER_PLANT")
    response = client.post(
        "/api/devices/TEST_PLANT/telemetry",
        json={"token": wrong_token, "sensors": [{"key": "light", "value": 100}]},
    )
    assert response.status_code == 401
    assert not mock_process.called


@patch("app.routers.devices.process_telemetry", new_callable=AsyncMock)
def test_receive_telemetry_error(mock_process, valid_device_token):
    mock_process.side_effect = ValueError("Thiết bị chưa được cấu hình")
    response = client.post(
        "/api/devices/TEST_PLANT/telemetry",
        json={"token": valid_device_token, "sensors": [{"key": "light", "value": 100}]},
    )
    assert response.status_code == 400
