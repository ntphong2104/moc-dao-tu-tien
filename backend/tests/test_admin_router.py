import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient

from main import app
from app.dependencies import get_admin_user, get_current_user

# Setup TestClient with mocked dependencies
client = TestClient(app)


# Bypass auth and admin dependencies
async def override_get_admin_user():
    return {"id": str(uuid4()), "role": "admin"}


app.dependency_overrides[get_admin_user] = override_get_admin_user
app.dependency_overrides[get_current_user] = override_get_admin_user


@pytest.fixture
def mock_db():
    return AsyncMock()


@patch("app.routers.admin.get_dashboard_stats", new_callable=AsyncMock)
def test_admin_dashboard(mock_get_dashboard):
    mock_get_dashboard.return_value = {"total_users": 100}
    response = client.get("/api/admin/dashboard")
    assert response.status_code == 200
    assert response.json() == {"total_users": 100}


@patch("app.routers.admin.get_devices_list", new_callable=AsyncMock)
def test_list_devices(mock_get_devices):
    mock_get_devices.return_value = [{"id": str(uuid4()), "plant_code": "ABC"}]
    response = client.get("/api/admin/devices")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("app.routers.admin.provision_device", new_callable=AsyncMock)
def test_create_device(mock_provision):
    mock_provision.return_value = {
        "id": str(uuid4()),
        "plant_code": "ABC",
        "verify_code": "123",
    }
    response = client.post("/api/admin/devices")
    assert response.status_code == 200
    assert response.json()["plant_code"] == "ABC"


@patch("app.routers.admin.update_device_status", new_callable=AsyncMock)
def test_update_device(mock_update):
    mock_update.return_value.plant_code = "ABC"
    mock_update.return_value.is_active = False

    device_id = str(uuid4())
    response = client.put(f"/api/admin/devices/{device_id}", json={"is_active": False})

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@patch("app.routers.admin.update_device_status", new_callable=AsyncMock)
def test_update_device_not_found(mock_update):
    mock_update.side_effect = ValueError("Thiết bị không tồn tại")

    device_id = str(uuid4())
    response = client.put(f"/api/admin/devices/{device_id}", json={"is_active": False})

    assert response.status_code == 404
    assert "Thiết bị không tồn tại" in response.json()["detail"]


@patch("app.routers.admin.create_plant_type", new_callable=AsyncMock)
def test_create_plant_type(mock_create_pt):
    mock_create_pt.return_value.id = uuid4()
    mock_create_pt.return_value.name = "Hoa Hồng"
    mock_create_pt.return_value.water_capacity = 100
    mock_create_pt.return_value.light_requirement = 50
    mock_create_pt.return_value.temperature_min = 10.0
    mock_create_pt.return_value.temperature_max = 30.0
    mock_create_pt.return_value.humidity_min = 40.0
    mock_create_pt.return_value.humidity_max = 80.0
    mock_create_pt.return_value.description = ""

    response = client.post(
        "/api/admin/plant-types",
        json={
            "name": "Hoa Hồng",
            "water_capacity": 100,
            "light_requirement": 50,
            "temperature_min": 10,
            "temperature_max": 30,
            "humidity_min": 40,
            "humidity_max": 80,
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Hoa Hồng"


@patch("app.routers.admin.create_plant_type", new_callable=AsyncMock)
def test_create_plant_type_error(mock_create_pt):
    mock_create_pt.side_effect = ValueError("Loại cây đã tồn tại")
    response = client.post(
        "/api/admin/plant-types",
        json={
            "name": "Hoa Hồng",
            "water_capacity": 100,
            "light_requirement": 50,
            "temperature_min": 10,
            "temperature_max": 30,
            "humidity_min": 40,
            "humidity_max": 80,
        },
    )

    assert response.status_code == 400
    assert "tồn tại" in response.json()["detail"]


@patch("app.routers.admin.delete_plant_type", new_callable=AsyncMock)
def test_delete_plant_type(mock_delete):
    type_id = str(uuid4())
    response = client.delete(f"/api/admin/plant-types/{type_id}")
    assert response.status_code == 204


@patch("app.routers.admin.delete_plant_type", new_callable=AsyncMock)
def test_delete_plant_type_error(mock_delete):
    mock_delete.side_effect = ValueError("Không thể xóa")
    type_id = str(uuid4())
    response = client.delete(f"/api/admin/plant-types/{type_id}")
    assert response.status_code == 400


@patch("app.routers.admin.update_exp_configs", new_callable=AsyncMock)
def test_update_exp_config(mock_update_exp):
    mock_update_exp.return_value = [1]
    response = client.put(
        "/api/admin/exp-config",
        json={"configs": [{"quality_level": "GOOD", "exp_delta": 10}]},
    )
    assert response.status_code == 200


@patch("app.routers.admin.update_rank_configs", new_callable=AsyncMock)
def test_update_rank_config(mock_update_rank):
    mock_update_rank.return_value = [1]
    response = client.put(
        "/api/admin/rank-config",
        json={"ranks": [{"order": 1, "name": "Luyện Khí", "min_exp": 0}]},
    )
    assert response.status_code == 200


@patch("app.routers.admin.get_plant_types", new_callable=AsyncMock)
def test_list_plant_types(mock_get_pt):
    pt = MagicMock()
    pt.id = uuid4()
    pt.name = "Xương Rồng"
    pt.water_capacity = 100
    pt.light_requirement = 50
    pt.temperature_min = 10.0
    pt.temperature_max = 30.0
    pt.humidity_min = 40.0
    pt.humidity_max = 80.0
    pt.description = ""
    mock_get_pt.return_value = [pt]
    response = client.get("/api/admin/plant-types")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("app.routers.admin.update_plant_type", new_callable=AsyncMock)
def test_update_plant_type(mock_update_pt):
    pt = MagicMock()
    pt.id = uuid4()
    pt.name = "Hoa Hồng"
    pt.water_capacity = 100
    pt.light_requirement = 50
    pt.temperature_min = 10.0
    pt.temperature_max = 30.0
    pt.humidity_min = 40.0
    pt.humidity_max = 80.0
    pt.description = ""
    mock_update_pt.return_value = pt
    response = client.put(f"/api/admin/plant-types/{pt.id}", json={"name": "Hoa Hồng"})
    assert response.status_code == 200

    mock_update_pt.side_effect = ValueError("Not found")
    response2 = client.put(f"/api/admin/plant-types/{pt.id}", json={"name": "Hoa Hồng"})
    assert response2.status_code == 404


@patch("app.routers.admin.get_exp_configs", new_callable=AsyncMock)
def test_get_exp_config(mock_get_exp):
    c = MagicMock()
    c.id = uuid4()
    c.quality_level = "GOOD"
    c.exp_delta = 10
    c.description = "Tốt"
    mock_get_exp.return_value = [c]
    response = client.get("/api/admin/exp-config")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("app.routers.admin.get_rank_configs", new_callable=AsyncMock)
def test_get_rank_config(mock_get_rank):
    r = MagicMock()
    r.id = uuid4()
    r.order = 1
    r.name = "Luyện Khí"
    r.min_exp = 0
    mock_get_rank.return_value = [r]
    response = client.get("/api/admin/rank-config")
    assert response.status_code == 200
    assert len(response.json()) == 1
