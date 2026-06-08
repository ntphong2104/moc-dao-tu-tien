import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient

from main import app
from app.database import get_db
from app.models.plant import Plant
from app.models.user import User
from app.models.config import RankConfig


@pytest.fixture
def mock_db():
    return AsyncMock()


def test_get_leaderboard(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)

    plant = Plant(id=uuid4(), name="Test Plant", total_exp=100)
    plant.user = User(display_name="Player 1")
    plant.current_rank = RankConfig(name="Trúc Cơ")

    mock_result_plants = MagicMock()
    mock_result_plants.scalars.return_value.all.return_value = [plant]

    mock_result_count = MagicMock()
    mock_result_count.scalar.return_value = 1

    mock_db.execute.side_effect = [mock_result_plants, mock_result_count]

    response = client.get("/api/leaderboard?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert len(data["entries"]) == 1
    assert data["entries"][0]["plant_name"] == "Test Plant"
    assert data["entries"][0]["owner_display_name"] == "Player 1"

    app.dependency_overrides.clear()
