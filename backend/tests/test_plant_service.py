import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, UTC

from app.services.plant_service import (
    pair_plant,
    get_dashboard,
    get_plant_history,
    update_plant,
)
from app.models.device import Device
from app.models.plant import Plant
from app.models.user import User
from app.models.config import PlantType, RankConfig
from app.models.sensor_reading import SensorReading


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def mock_user():
    return User(id=uuid4(), email="test@test.com")


@pytest.mark.asyncio
async def test_pair_plant_success(mock_db, mock_user):
    device = Device(
        id=uuid4(),
        plant_code="ABCDEFGH",
        is_active=True,
        is_paired=False,
        verify_hash="hash",
    )
    plant_type = PlantType(id=uuid4(), name="Xương Rồng")
    rank = RankConfig(id=uuid4(), order=1, name="Phàm Mộc")

    mock_result_no_plant = MagicMock()
    mock_result_no_plant.scalar_one_or_none.return_value = None

    mock_result_device = MagicMock()
    mock_result_device.scalar_one_or_none.return_value = device

    mock_result_pt = MagicMock()
    mock_result_pt.scalar_one_or_none.return_value = plant_type

    mock_result_rank = MagicMock()
    mock_result_rank.scalar_one_or_none.return_value = rank

    mock_db.execute.side_effect = [
        mock_result_no_plant,
        mock_result_device,
        mock_result_pt,
        mock_result_rank,
    ]

    with patch("bcrypt.checkpw", return_value=True):
        plant = await pair_plant(
            mock_db, mock_user, "ABCDEFGH", "123456", "Cây của tôi", plant_type.id
        )

    assert plant.name == "Cây của tôi"
    assert plant.user_id == mock_user.id
    assert device.is_paired is True
    assert mock_db.add.called
    assert mock_db.flush.called


@pytest.mark.asyncio
async def test_pair_plant_already_has_plant(mock_db, mock_user):
    existing_plant = Plant(id=uuid4(), name="My Plant")
    mock_result_has_plant = MagicMock()
    mock_result_has_plant.scalar_one_or_none.return_value = existing_plant
    mock_db.execute.return_value = mock_result_has_plant

    with pytest.raises(ValueError, match="Mỗi tài khoản chỉ được liên kết 1 chậu cây"):
        await pair_plant(mock_db, mock_user, "ABCDEFGH", "123456", "Name", uuid4())


@pytest.mark.asyncio
async def test_pair_plant_invalid_code(mock_db, mock_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Plant Code không hợp lệ"):
        await pair_plant(mock_db, mock_user, "WRONG", "123456", "Name", uuid4())


@pytest.mark.asyncio
async def test_pair_plant_inactive_device(mock_db, mock_user):
    device = Device(id=uuid4(), is_active=False)
    mock_result_no_plant = MagicMock()
    mock_result_no_plant.scalar_one_or_none.return_value = None
    mock_result_device = MagicMock()
    mock_result_device.scalar_one_or_none.return_value = device
    mock_db.execute.side_effect = [mock_result_no_plant, mock_result_device]

    with pytest.raises(ValueError, match="Thiết bị đã bị vô hiệu hóa"):
        await pair_plant(mock_db, mock_user, "ABCDEFGH", "123456", "Name", uuid4())


@pytest.mark.asyncio
async def test_pair_plant_already_paired(mock_db, mock_user):
    device = Device(id=uuid4(), is_active=True, is_paired=True)
    mock_result_no_plant = MagicMock()
    mock_result_no_plant.scalar_one_or_none.return_value = None
    mock_result_device = MagicMock()
    mock_result_device.scalar_one_or_none.return_value = device
    mock_db.execute.side_effect = [mock_result_no_plant, mock_result_device]

    with pytest.raises(
        ValueError, match="Thiết bị đã được liên kết với tài khoản khác"
    ):
        await pair_plant(mock_db, mock_user, "ABCDEFGH", "123456", "Name", uuid4())


@pytest.mark.asyncio
async def test_pair_plant_wrong_verify_code(mock_db, mock_user):
    device = Device(id=uuid4(), is_active=True, is_paired=False, verify_hash="hash")
    mock_result_no_plant = MagicMock()
    mock_result_no_plant.scalar_one_or_none.return_value = None
    mock_result_device = MagicMock()
    mock_result_device.scalar_one_or_none.return_value = device
    mock_db.execute.side_effect = [mock_result_no_plant, mock_result_device]

    with patch("bcrypt.checkpw", return_value=False):
        with pytest.raises(ValueError, match="Verify Code không chính xác"):
            await pair_plant(mock_db, mock_user, "ABCDEFGH", "WRONG", "Name", uuid4())


@pytest.mark.asyncio
async def test_pair_plant_missing_type(mock_db, mock_user):
    device = Device(id=uuid4(), is_active=True, is_paired=False, verify_hash="hash")
    mock_result_no_plant = MagicMock()
    mock_result_no_plant.scalar_one_or_none.return_value = None

    mock_result_device = MagicMock()
    mock_result_device.scalar_one_or_none.return_value = device

    mock_result_pt = MagicMock()
    mock_result_pt.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [
        mock_result_no_plant,
        mock_result_device,
        mock_result_pt,
    ]

    with patch("bcrypt.checkpw", return_value=True):
        with pytest.raises(ValueError, match="Loại cây không tồn tại"):
            await pair_plant(mock_db, mock_user, "ABCDEFGH", "123456", "Name", uuid4())


@pytest.mark.asyncio
async def test_pair_plant_missing_rank(mock_db, mock_user):
    device = Device(id=uuid4(), is_active=True, is_paired=False, verify_hash="hash")
    mock_result_no_plant = MagicMock()
    mock_result_no_plant.scalar_one_or_none.return_value = None

    mock_result_device = MagicMock()
    mock_result_device.scalar_one_or_none.return_value = device

    mock_result_pt = MagicMock()
    mock_result_pt.scalar_one_or_none.return_value = PlantType()

    mock_result_rank = MagicMock()
    mock_result_rank.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [
        mock_result_no_plant,
        mock_result_device,
        mock_result_pt,
        mock_result_rank,
    ]

    with patch("bcrypt.checkpw", return_value=True):
        with pytest.raises(ValueError, match="Chưa có cấu hình Cảnh Giới"):
            await pair_plant(mock_db, mock_user, "ABCDEFGH", "123456", "Name", uuid4())


@pytest.mark.asyncio
async def test_get_plant_history_success(mock_db, mock_user):
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
    plant = Plant(id=uuid4(), plant_type=plant_type)

    reading = SensorReading(value=50, quality="GOOD", created_at=datetime.now(UTC))

    mock_result_plant = MagicMock()
    mock_result_plant.scalar_one_or_none.return_value = plant

    mock_result_readings = MagicMock()
    mock_result_readings.scalars.return_value.all.return_value = [reading]

    mock_db.execute.side_effect = [mock_result_plant, mock_result_readings]

    res = await get_plant_history(mock_db, mock_user, "soil_moisture", 24)
    assert res["sensor_key"] == "soil_moisture"
    assert len(res["readings"]) == 1
    assert res["ideal_min"] == 40
    assert res["ideal_max"] == 60


@pytest.mark.asyncio
async def test_get_plant_history_no_plant(mock_db, mock_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Chưa liên kết"):
        await get_plant_history(mock_db, mock_user, "soil_moisture")


@pytest.mark.asyncio
async def test_update_plant_success(mock_db, mock_user):
    plant = Plant(id=uuid4(), name="Old")
    pt = PlantType(id=uuid4(), name="T1")

    mock_result_plant = MagicMock()
    mock_result_plant.scalar_one_or_none.return_value = plant

    mock_result_pt = MagicMock()
    mock_result_pt.scalar_one_or_none.return_value = pt

    mock_db.execute.side_effect = [mock_result_plant, mock_result_pt, mock_result_plant]

    res = await update_plant(mock_db, mock_user, name="New", plant_type_id=pt.id)
    assert res.name == "New"
    assert res.plant_type_id == pt.id

    res2 = await update_plant(mock_db, mock_user)
    assert res2.name == "New"


@pytest.mark.asyncio
async def test_update_plant_no_plant(mock_db, mock_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Chưa liên kết"):
        await update_plant(mock_db, mock_user, name="New")


@pytest.mark.asyncio
async def test_update_plant_invalid_type(mock_db, mock_user):
    plant = Plant(id=uuid4(), name="Old")

    mock_result_plant = MagicMock()
    mock_result_plant.scalar_one_or_none.return_value = plant

    mock_result_pt = MagicMock()
    mock_result_pt.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_result_plant, mock_result_pt]

    with pytest.raises(ValueError, match="Loại cây không tồn tại"):
        await update_plant(mock_db, mock_user, plant_type_id=uuid4())


@pytest.mark.asyncio
async def test_get_dashboard_not_paired(mock_db, mock_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Chưa liên kết chậu cây"):
        await get_dashboard(mock_db, mock_user)


@pytest.mark.asyncio
async def test_get_dashboard_success(mock_db, mock_user):
    plant = Plant(id=uuid4(), name="Test Plant", total_exp=100)
    plant.plant_type = PlantType(id=uuid4(), name="Cây Test")
    plant.current_rank = RankConfig(id=uuid4(), order=1, name="T1", min_exp=0)
    plant.device = Device(last_seen_at=datetime.now(UTC))  # hit false branch

    mock_result_plant = MagicMock()
    mock_result_plant.scalar_one_or_none.return_value = plant

    reading = SensorReading(value=50, quality="GOOD", created_at=datetime.now(UTC))
    mock_result_reading = MagicMock()
    mock_result_reading.scalar_one_or_none.return_value = reading

    next_rank = RankConfig(id=uuid4(), order=2, name="T2", min_exp=200)
    mock_result_next_rank = MagicMock()
    mock_result_next_rank.scalar_one_or_none.return_value = next_rank

    # 1 for plant, 4 for sensors, 1 for next_rank
    mock_db.execute.side_effect = [
        mock_result_plant,
        mock_result_reading,
        mock_result_reading,
        mock_result_reading,
        mock_result_reading,
        mock_result_next_rank,
    ]

    res = await get_dashboard(mock_db, mock_user)
    assert res["plant_id"] == str(plant.id)
    assert res["overall_quality"] == "GOOD"
    assert len(res["sensors"]) == 4


@pytest.mark.asyncio
async def test_get_dashboard_branches(mock_db, mock_user):
    plant = Plant(id=uuid4(), name="Test Plant", total_exp=100)
    plant.plant_type = PlantType(id=uuid4(), name="Cây Test")
    plant.current_rank = RankConfig(id=uuid4(), order=1, name="T1", min_exp=0)
    plant.device = Device(last_seen_at=None)  # hit last_seen_at is None

    plant2 = Plant(id=uuid4(), name="Test Plant 2", total_exp=100)
    plant2.plant_type = PlantType(id=uuid4(), name="Cây Test")
    plant2.current_rank = RankConfig(id=uuid4(), order=1, name="T1", min_exp=0)
    plant2.device = Device(last_seen_at=datetime.now())  # naive datetime

    mock_result_plant = MagicMock()
    mock_result_plant.scalar_one_or_none.return_value = plant

    mock_result_plant2 = MagicMock()
    mock_result_plant2.scalar_one_or_none.return_value = plant2

    mock_result_empty_reading = MagicMock()
    mock_result_empty_reading.scalar_one_or_none.return_value = None

    mock_result_no_next_rank = MagicMock()
    mock_result_no_next_rank.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [
        mock_result_plant,
        mock_result_empty_reading,
        mock_result_empty_reading,
        mock_result_empty_reading,
        mock_result_empty_reading,
        mock_result_no_next_rank,
        mock_result_plant2,
        mock_result_empty_reading,
        mock_result_empty_reading,
        mock_result_empty_reading,
        mock_result_empty_reading,
        mock_result_no_next_rank,
    ]

    res = await get_dashboard(mock_db, mock_user)
    assert res["next_rank"] is None
    assert res["device_last_seen"] is None
    assert len(res["sensors"]) == 0

    res2 = await get_dashboard(mock_db, mock_user)
    assert res2["device_last_seen"] is not None
