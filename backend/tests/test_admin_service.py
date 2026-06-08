import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, UTC

from app.services.admin_service import (
    provision_device,
    get_dashboard_stats,
    get_devices_list,
    update_device_status,
    get_plant_types,
    create_plant_type,
    update_plant_type,
    delete_plant_type,
    get_exp_configs,
    update_exp_configs,
    get_rank_configs,
    update_rank_configs,
)
from app.models.device import Device
from app.models.config import PlantType, ExpConfig, RankConfig
from app.models.plant import Plant
from app.models.user import User


@pytest.fixture
def mock_db():
    db = AsyncMock()
    # db.add is synchronous in SQLAlchemy, so we use MagicMock
    db.add = MagicMock()

    def mock_add(obj):
        if hasattr(obj, "created_at") and obj.created_at is None:
            obj.created_at = datetime.now(UTC)

    db.add.side_effect = mock_add
    return db


@pytest.mark.asyncio
async def test_provision_device(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    res = await provision_device(mock_db)

    assert mock_db.add.called
    assert mock_db.flush.called
    assert "plant_code" in res
    assert "verify_code" in res
    assert len(res["plant_code"]) == 8
    assert len(res["verify_code"]) == 6


@pytest.mark.asyncio
async def test_provision_device_duplicate_retry(mock_db):
    mock_result_duplicate = MagicMock()
    mock_result_duplicate.scalar_one_or_none.return_value = Device()

    mock_result_success = MagicMock()
    mock_result_success.scalar_one_or_none.return_value = None

    # 2 lần đầu trùng, lần 3 thành công
    mock_db.execute.side_effect = [
        mock_result_duplicate,
        mock_result_duplicate,
        mock_result_success,
    ]

    res = await provision_device(mock_db)

    assert mock_db.execute.call_count == 3
    assert mock_db.add.called
    assert "plant_code" in res


@pytest.mark.asyncio
async def test_provision_device_fail_after_10_retries(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Device()
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Không thể sinh Plant Code duy nhất"):
        await provision_device(mock_db)


@pytest.mark.asyncio
async def test_update_device_status(mock_db):
    device = Device(id=uuid4(), plant_code="PLANT123", is_active=False)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = device
    mock_db.execute.return_value = mock_result

    updated_device = await update_device_status(mock_db, str(device.id), True)

    assert updated_device.is_active is True
    assert mock_db.flush.called


@pytest.mark.asyncio
async def test_update_device_status_not_found(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Thiết bị không tồn tại"):
        await update_device_status(mock_db, str(uuid4()), True)


@pytest.mark.asyncio
async def test_create_plant_type_success(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    data = {"name": "Xương Rồng", "soil_moisture_min": 40.0}
    pt = await create_plant_type(mock_db, data)

    assert pt.name == "Xương Rồng"
    assert mock_db.add.called
    assert mock_db.flush.called


@pytest.mark.asyncio
async def test_create_plant_type_duplicate(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = PlantType(name="Xương Rồng")
    mock_db.execute.return_value = mock_result

    data = {"name": "Xương Rồng", "soil_moisture_min": 40.0}
    with pytest.raises(ValueError, match="Loại cây 'Xương Rồng' đã tồn tại"):
        await create_plant_type(mock_db, data)


@pytest.mark.asyncio
async def test_delete_plant_type_success(mock_db):
    pt = PlantType(id=uuid4(), name="Xương Rồng")

    mock_result_pt = MagicMock()
    mock_result_pt.scalar_one_or_none.return_value = pt

    mock_result_count = MagicMock()
    mock_result_count.scalar.return_value = 0

    mock_db.execute.side_effect = [mock_result_pt, mock_result_count]

    await delete_plant_type(mock_db, str(pt.id))

    assert mock_db.delete.called
    assert mock_db.flush.called


@pytest.mark.asyncio
async def test_delete_plant_type_has_plants(mock_db):
    pt = PlantType(id=uuid4(), name="Xương Rồng")

    mock_result_pt = MagicMock()
    mock_result_pt.scalar_one_or_none.return_value = pt

    mock_result_count = MagicMock()
    mock_result_count.scalar.return_value = 5

    mock_db.execute.side_effect = [mock_result_pt, mock_result_count]

    with pytest.raises(
        ValueError, match="Không thể xóa: có 5 cây đang sử dụng loại cây này"
    ):
        await delete_plant_type(mock_db, str(pt.id))


@pytest.mark.asyncio
async def test_get_dashboard_stats(mock_db):
    mock_count = MagicMock()
    mock_count.scalar.return_value = 10

    mock_dist = MagicMock()
    mock_dist.all.return_value = [("Trúc Cơ", 5), ("Kết Đan", 5)]

    mock_db.execute.side_effect = [
        mock_count,  # total_users
        mock_count,  # total_devices
        mock_count,  # devices_online
        mock_count,  # total_plants
        mock_dist,  # rank_distribution
    ] + [mock_count] * 7  # new_users_daily (7 days)

    stats = await get_dashboard_stats(mock_db)

    assert stats["total_users"] == 10
    assert stats["devices_online"] == 10
    assert stats["devices_offline"] == 0
    assert len(stats["rank_distribution"]) == 2
    assert len(stats["new_users_daily"]) == 7


@pytest.mark.asyncio
async def test_get_devices_list(mock_db):
    device = Device(
        id=uuid4(), plant_code="ABC", is_paired=True, created_at=datetime.now(UTC)
    )
    device2 = Device(
        id=uuid4(), plant_code="DEF", is_paired=False, created_at=datetime.now(UTC)
    )
    device3 = Device(
        id=uuid4(), plant_code="GHI", is_paired=True, created_at=datetime.now(UTC)
    )
    plant = Plant(name="Cây test")
    plant.user = User(email="test@moctu.com")

    mock_result_device = MagicMock()
    mock_result_device.scalars.return_value.all.return_value = [
        device,
        device2,
        device3,
    ]

    mock_result_plant = MagicMock()
    mock_result_plant.scalar_one_or_none.return_value = plant

    mock_result_noplant = MagicMock()
    mock_result_noplant.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [
        mock_result_device,
        mock_result_plant,
        mock_result_noplant,
    ]

    res = await get_devices_list(mock_db)
    assert len(res) == 3
    assert res[0]["plant_code"] == "ABC"
    assert res[0]["paired_plant_name"] == "Cây test"
    assert res[0]["paired_user_email"] == "test@moctu.com"


@pytest.mark.asyncio
async def test_get_plant_types(mock_db):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [PlantType(name="T1")]
    mock_db.execute.return_value = mock_result

    res = await get_plant_types(mock_db)
    assert len(res) == 1
    assert res[0].name == "T1"


@pytest.mark.asyncio
async def test_update_plant_type(mock_db):
    pt = PlantType(id=uuid4(), name="T1")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = pt
    mock_db.execute.return_value = mock_result

    res = await update_plant_type(
        mock_db, str(pt.id), {"name": "T2", "description": None}
    )
    assert res.name == "T2"


@pytest.mark.asyncio
async def test_update_plant_type_not_found(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Loại cây không tồn tại"):
        await update_plant_type(mock_db, str(uuid4()), {"name": "T2"})


@pytest.mark.asyncio
async def test_get_exp_configs(mock_db):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [ExpConfig()]
    mock_db.execute.return_value = mock_result

    res = await get_exp_configs(mock_db)
    assert len(res) == 1


@pytest.mark.asyncio
async def test_get_rank_configs(mock_db):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [RankConfig()]
    mock_db.execute.return_value = mock_result

    res = await get_rank_configs(mock_db)
    assert len(res) == 1


@pytest.mark.asyncio
async def test_update_rank_configs(mock_db):
    # Test both existing and new ranks
    existing_rank = RankConfig(order=1, name="Old", min_exp=0)

    mock_result_exist = MagicMock()
    mock_result_exist.scalar_one_or_none.return_value = existing_rank

    mock_result_new = MagicMock()
    mock_result_new.scalar_one_or_none.return_value = None

    # get_rank_configs call at the end
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [
        existing_rank,
        RankConfig(order=2, name="T2", min_exp=100),
    ]

    mock_db.execute.side_effect = [mock_result_exist, mock_result_new, mock_result_all]

    ranks = [
        {"order": 1, "name": "T1", "min_exp": 0},
        {"order": 2, "name": "T2", "min_exp": 100},
    ]
    res = await update_rank_configs(mock_db, ranks)
    assert existing_rank.name == "T1"
    assert len(res) == 2


@pytest.mark.asyncio
async def test_delete_plant_type_error(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Loại cây không tồn tại"):
        await delete_plant_type(mock_db, str(uuid4()))


@pytest.mark.asyncio
async def test_update_exp_configs(mock_db):
    # Test both existing and new configs
    # Test both existing and new configs
    existing_config = ExpConfig(quality_level="GOOD", exp_delta=10)
    mock_result_exist = MagicMock()
    mock_result_exist.scalar_one_or_none.return_value = existing_config

    mock_result_new = MagicMock()
    mock_result_new.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_result_exist, mock_result_new]

    configs = [
        {"quality_level": "GOOD", "exp_delta": 15, "description": "Good"},
        {"quality_level": "BAD", "exp_delta": -5, "description": "Bad"},
    ]
    res = await update_exp_configs(mock_db, configs)
    assert len(res) == 2
    assert existing_config.exp_delta == 15
