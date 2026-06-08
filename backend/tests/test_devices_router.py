from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@patch("app.routers.devices.process_telemetry", new_callable=AsyncMock)
def test_receive_telemetry_success(mock_process):
    mock_process.return_value = {
        "status": "success",
        "exp_awarded": True,
        "message": "OK",
    }
    response = client.post(
        "/api/devices/TEST_PLANT/telemetry",
        json={"sensors": [{"key": "light", "value": 100}]},
        headers={"X-Plant-Code": "TEST_PLANT"},
    )
    assert response.status_code == 200, response.json()
    assert response.json()["exp_awarded"] is True


@patch("app.routers.devices.process_telemetry", new_callable=AsyncMock)
def test_receive_telemetry_header_mismatch(mock_process):
    response = client.post(
        "/api/devices/TEST_PLANT/telemetry",
        json={"sensors": [{"key": "light", "value": 100}]},
        headers={"X-Plant-Code": "WRONG_PLANT"},
    )
    assert response.status_code == 403
    assert not mock_process.called


@patch("app.routers.devices.process_telemetry", new_callable=AsyncMock)
def test_receive_telemetry_error(mock_process):
    mock_process.side_effect = ValueError("Thiết bị chưa được cấu hình")
    response = client.post(
        "/api/devices/TEST_PLANT/telemetry",
        json={"sensors": [{"key": "light", "value": 100}]},
        headers={"X-Plant-Code": "TEST_PLANT"},
    )
    assert response.status_code == 400
