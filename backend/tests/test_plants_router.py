import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from fastapi.testclient import TestClient

from main import app
from app.dependencies import get_current_user
from app.models.user import User

# Setup TestClient with mocked dependencies
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_auth():
    async def override_get_current_user():
        return User(
            id=uuid4(), email="test@moctu.com", display_name="Test", role="user"
        )

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()


@patch("app.routers.plants.provision_device", new_callable=AsyncMock)
def test_diy_provision(mock_provision):
    mock_provision.return_value = {"plant_code": "TEST"}
    response = client.post("/api/plants/diy-provision")
    assert response.status_code == 200
    assert response.json()["data"]["plant_code"] == "TEST"


@patch("app.routers.plants.provision_device", new_callable=AsyncMock)
def test_diy_provision_error(mock_provision):
    mock_provision.side_effect = ValueError("Error")
    response = client.post("/api/plants/diy-provision")
    assert response.status_code == 400


@patch("app.routers.plants.get_plant_types", new_callable=AsyncMock)
def test_get_all_plant_types(mock_get_types):
    mock_get_types.return_value = []
    response = client.get("/api/plants/types")
    assert response.status_code == 200
    assert response.json() == []


@patch("app.routers.plants.pair_plant", new_callable=AsyncMock)
def test_pair_plant_endpoint(mock_pair):
    mock_pair.return_value.id = uuid4()
    mock_pair.return_value.name = "Test Plant"
    response = client.post(
        "/api/plants/pair",
        json={
            "plant_code": "ABC",
            "verify_code": "123",
            "name": "Test Plant",
            "plant_type_id": str(uuid4()),
        },
    )
    assert response.status_code == 200
    assert "thành công" in response.json()["message"]


@patch("app.routers.plants.pair_plant", new_callable=AsyncMock)
def test_pair_plant_error(mock_pair):
    mock_pair.side_effect = ValueError("Code sai")
    response = client.post(
        "/api/plants/pair",
        json={
            "plant_code": "ABC",
            "verify_code": "123",
            "name": "Test Plant",
            "plant_type_id": str(uuid4()),
        },
    )
    assert response.status_code == 400


@patch("app.routers.plants.get_dashboard", new_callable=AsyncMock)
def test_get_dashboard_endpoint(mock_dashboard):
    mock_dashboard.return_value = {"plant_id": "123"}
    response = client.get("/api/plants/me/dashboard")
    assert response.status_code == 200


@patch("app.routers.plants.get_dashboard", new_callable=AsyncMock)
def test_get_dashboard_error(mock_dashboard):
    mock_dashboard.side_effect = ValueError("Chưa liên kết")
    response = client.get("/api/plants/me/dashboard")
    assert response.status_code == 404


@patch("app.routers.plants.get_plant_history", new_callable=AsyncMock)
def test_get_history_endpoint(mock_history):
    mock_history.return_value = {"readings": []}
    response = client.get("/api/plants/me/history?sensor_key=light")
    assert response.status_code == 200


@patch("app.routers.plants.get_plant_history", new_callable=AsyncMock)
def test_get_history_invalid_key(mock_history):
    response = client.get("/api/plants/me/history?sensor_key=invalid")
    assert response.status_code == 400


@patch("app.routers.plants.get_plant_history", new_callable=AsyncMock)
def test_get_history_error(mock_history):
    mock_history.side_effect = ValueError("Lỗi")
    response = client.get("/api/plants/me/history?sensor_key=light")
    assert response.status_code == 404


@patch("app.routers.plants.update_plant", new_callable=AsyncMock)
def test_update_plant_endpoint(mock_update):
    mock_update.return_value.name = "New Name"
    response = client.put("/api/plants/me", json={"name": "New Name"})
    assert response.status_code == 200


@patch("app.routers.plants.update_plant", new_callable=AsyncMock)
def test_update_plant_error(mock_update):
    mock_update.side_effect = ValueError("Chưa liên kết")
    response = client.put("/api/plants/me", json={"name": "New Name"})
    assert response.status_code == 400
