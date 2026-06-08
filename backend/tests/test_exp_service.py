import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, UTC, timedelta

from app.services.exp_service import (
    classify_sensor_quality,
    get_overall_quality,
    get_exp_delta,
    check_anti_spam,
    determine_rank,
    process_exp,
    classify_sensors_for_plant_type,
)
from app.models.plant import Plant
from app.models.config import ExpConfig, RankConfig, PlantType


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    return db


def test_classify_sensor_quality():
    # EXCELLENT
    assert classify_sensor_quality(50, 40, 60) == "EXCELLENT"
    # GOOD (deviation <= 0.10) - range = 20, 10% is 2. 62 -> 2 deviation -> 10%
    assert classify_sensor_quality(62, 40, 60) == "GOOD"
    # FAIR (deviation <= 0.25) - 25% is 5. 65 -> 5 deviation -> 25%
    assert classify_sensor_quality(65, 40, 60) == "FAIR"
    # POOR (deviation <= 0.50) - 50% is 10. 70 -> 10 deviation -> 50%
    assert classify_sensor_quality(70, 40, 60) == "POOR"
    # DANGER (deviation > 0.50)
    assert classify_sensor_quality(71, 40, 60) == "DANGER"
    # value < ideal_min
    assert classify_sensor_quality(30, 40, 60) == "POOR"
    # ideal_range <= 0
    assert classify_sensor_quality(50, 60, 40) == "DANGER"


def test_get_overall_quality():
    assert get_overall_quality(["EXCELLENT", "GOOD", "EXCELLENT"]) == "GOOD"
    assert get_overall_quality(["EXCELLENT", "DANGER", "EXCELLENT"]) == "DANGER"
    assert get_overall_quality(["POOR", "FAIR", "GOOD"]) == "POOR"
    assert get_overall_quality([]) == "FAIR"


@pytest.mark.asyncio
async def test_get_exp_delta_from_db(mock_db):
    config = ExpConfig(quality_level="GOOD", exp_delta=7.0)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = config
    mock_db.execute.return_value = mock_result

    delta = await get_exp_delta(mock_db, "GOOD")
    assert delta == 7.0


@pytest.mark.asyncio
async def test_get_exp_delta_fallback(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    delta = await get_exp_delta(mock_db, "DANGER")
    assert delta == -8.0


@pytest.mark.asyncio
async def test_check_anti_spam():
    plant = Plant(last_exp_reward_at=None)
    assert await check_anti_spam(plant) is True

    plant.last_exp_reward_at = datetime.now(UTC) - timedelta(seconds=10)
    assert await check_anti_spam(plant) is False

    plant.last_exp_reward_at = datetime.now()  # naive datetime
    assert await check_anti_spam(plant) is False

    plant.last_exp_reward_at = datetime.now(UTC) - timedelta(seconds=60)
    assert await check_anti_spam(plant) is True


@pytest.mark.asyncio
async def test_determine_rank(mock_db):
    rank = RankConfig(order=2, name="Trúc Cơ")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = rank
    mock_db.execute.return_value = mock_result

    res = await determine_rank(mock_db, 150)
    assert res.name == "Trúc Cơ"


@pytest.mark.asyncio
async def test_determine_rank_fallback(mock_db):
    mock_result_none = MagicMock()
    mock_result_none.scalar_one_or_none.return_value = None

    mock_result_lowest = MagicMock()
    mock_result_lowest.scalar_one.return_value = RankConfig(order=1, name="Lowest")

    mock_db.execute.side_effect = [mock_result_none, mock_result_lowest]

    res = await determine_rank(mock_db, 0)
    assert res.name == "Lowest"


@patch("app.services.exp_service.sse_manager.broadcast", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_process_exp_breakthrough(mock_broadcast, mock_db):
    plant = Plant(id=uuid4(), name="Test Plant", total_exp=90, last_exp_reward_at=None)

    # Mock rank
    old_rank = RankConfig(id=uuid4(), order=1, name="Phàm Mộc", min_exp=0)
    new_rank = RankConfig(id=uuid4(), order=2, name="Trúc Cơ", min_exp=100)
    plant.current_rank = old_rank

    mock_result_config = MagicMock()
    mock_result_config.scalar_one_or_none.return_value = ExpConfig(
        quality_level="EXCELLENT", exp_delta=20.0
    )

    mock_result_rank = MagicMock()
    mock_result_rank.scalar_one_or_none.return_value = new_rank

    mock_db.execute.side_effect = [mock_result_config, mock_result_rank]

    result = await process_exp(mock_db, plant, "EXCELLENT")

    assert result["exp_awarded"] is True
    assert result["delta"] == 20.0
    assert result["total_exp"] == 110.0
    assert result["breakthrough"] is not None
    assert result["breakthrough"]["to_rank"] == "Trúc Cơ"

    assert mock_db.add.call_count == 2  # 1 cho ExpLog, 1 cho BreakthroughEvent
    assert mock_db.flush.called
    assert mock_broadcast.called


@patch("app.services.exp_service.sse_manager.broadcast", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_process_exp_no_breakthrough(mock_broadcast, mock_db):
    plant = Plant(id=uuid4(), name="Test Plant", total_exp=10, last_exp_reward_at=None)

    # Mock rank
    rank = RankConfig(id=uuid4(), order=1, name="Phàm Mộc", min_exp=0)
    plant.current_rank = rank

    mock_result_config = MagicMock()
    mock_result_config.scalar_one_or_none.return_value = ExpConfig(
        quality_level="GOOD", exp_delta=5.0
    )

    mock_result_rank = MagicMock()
    mock_result_rank.scalar_one_or_none.return_value = rank

    mock_db.execute.side_effect = [mock_result_config, mock_result_rank]

    result = await process_exp(mock_db, plant, "GOOD")

    assert result["exp_awarded"] is True
    assert result["breakthrough"] is None
    assert mock_db.add.call_count == 1  # Only ExpLog


@pytest.mark.asyncio
async def test_process_exp_anti_spam(mock_db):
    plant = Plant(id=uuid4(), total_exp=10, last_exp_reward_at=datetime.now(UTC))
    result = await process_exp(mock_db, plant, "EXCELLENT")

    assert result["exp_awarded"] is False
    assert result["total_exp"] == 10


def test_classify_sensors_for_plant_type():
    pt = PlantType(
        soil_moisture_min=40,
        soil_moisture_max=60,
        light_min=40,
        light_max=60,
        temperature_min=20,
        temperature_max=30,
        humidity_min=50,
        humidity_max=70,
    )

    data = {
        "soil_moisture": 50.0,  # EXCELLENT
        "light": 65.0,  # FAIR (5 deviation over 20 range -> 25%)
        "unknown_sensor": 100.0,  # Default to FAIR
    }

    res = classify_sensors_for_plant_type(data, pt)
    assert res["soil_moisture"] == "EXCELLENT"
    assert res["light"] == "FAIR"
    assert res["unknown_sensor"] == "FAIR"
