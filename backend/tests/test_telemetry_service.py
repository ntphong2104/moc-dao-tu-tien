import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.telemetry_service import process_telemetry
from app.models.device import Device
from app.models.plant import Plant
from app.models.config import PlantType
from app.schemas.telemetry import SensorData


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.mark.asyncio
async def test_process_telemetry_success(mock_db):
    device = Device(id=uuid4(), plant_code="TESTCODE", is_active=True, is_paired=True)
    plant_type = PlantType(
        soil_moisture_min=40,
        soil_moisture_max=60,
        light_min=1000,
        light_max=5000,
        temperature_min=20,
        temperature_max=30,
        humidity_min=50,
        humidity_max=80,
    )
    plant = Plant(id=uuid4(), device_id=device.id, plant_type=plant_type)

    mock_result_device = MagicMock()
    mock_result_device.scalar_one_or_none.return_value = device

    mock_result_plant = MagicMock()
    mock_result_plant.scalar_one_or_none.return_value = plant

    mock_db.execute.side_effect = [mock_result_device, mock_result_plant]

    sensors = [
        SensorData(key="soil_moisture", value=50),
        SensorData(key="light", value=3000),
        SensorData(key="temperature", value=25),
        SensorData(key="humidity", value=65),
    ]

    with patch(
        "app.services.telemetry_service.sse_manager.broadcast", new_callable=AsyncMock
    ) as mock_broadcast:
        res = await process_telemetry(mock_db, "TESTCODE", sensors)

    assert res["status"] == "ok"
    assert "EXCELLENT" in res["message"]
    assert mock_db.add.call_count == 4
    assert mock_broadcast.called


@pytest.mark.asyncio
async def test_process_telemetry_device_not_found(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Thiết bị không tồn tại"):
        await process_telemetry(mock_db, "TESTCODE", [])


@pytest.mark.asyncio
async def test_process_telemetry_device_inactive(mock_db):
    device = Device(id=uuid4(), is_active=False)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = device
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Thiết bị đã bị vô hiệu hóa"):
        await process_telemetry(mock_db, "TESTCODE", [])


@pytest.mark.asyncio
async def test_process_telemetry_device_not_paired(mock_db):
    device = Device(id=uuid4(), is_active=True, is_paired=False)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = device
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Thiết bị chưa được liên kết"):
        await process_telemetry(mock_db, "TESTCODE", [])


@pytest.mark.asyncio
async def test_process_telemetry_plant_not_found(mock_db):
    device = Device(id=uuid4(), is_active=True, is_paired=True)

    mock_result_device = MagicMock()
    mock_result_device.scalar_one_or_none.return_value = device

    mock_result_plant = MagicMock()
    mock_result_plant.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_result_device, mock_result_plant]

    with pytest.raises(ValueError, match="Không tìm thấy cây liên kết"):
        await process_telemetry(mock_db, "TESTCODE", [])


@pytest.mark.asyncio
async def test_process_telemetry_invalid_sensors(mock_db):
    device = Device(id=uuid4(), is_active=True, is_paired=True)
    plant = Plant(id=uuid4(), device_id=device.id, plant_type=PlantType())

    mock_result_device = MagicMock()
    mock_result_device.scalar_one_or_none.return_value = device

    mock_result_plant = MagicMock()
    mock_result_plant.scalar_one_or_none.return_value = plant

    mock_db.execute.side_effect = [mock_result_device, mock_result_plant]

    sensors = [SensorData(key="invalid_sensor", value=100)]

    with pytest.raises(ValueError, match="Không có dữ liệu cảm biến hợp lệ"):
        await process_telemetry(mock_db, "TESTCODE", sensors)
