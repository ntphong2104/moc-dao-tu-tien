import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, UTC
from uuid import uuid4

from app.scheduler import calculate_exp_batch, start_scheduler, stop_scheduler
from app.models.plant import Plant
from app.models.device import Device


@pytest.mark.asyncio
async def test_calculate_exp_batch_success():
    # Online plant
    plant1 = Plant(id=uuid4(), current_overall_quality="GOOD")
    plant1.device = Device(last_seen_at=datetime.now(UTC))

    # Offline plant (should be skipped)
    plant2 = Plant(id=uuid4(), current_overall_quality="GOOD")
    plant2.device = Device(last_seen_at=datetime.now(UTC) - timedelta(minutes=20))

    # No device plant (should be skipped)
    plant3 = Plant(id=uuid4(), current_overall_quality="GOOD")
    # Device will naturally be None since not assigned

    with patch("app.scheduler.async_session_factory") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [plant1, plant2, plant3]
        mock_session.execute.return_value = mock_result

        with patch(
            "app.scheduler.process_exp", new_callable=AsyncMock
        ) as mock_process_exp:
            await calculate_exp_batch()

            # process_exp should be called only for plant1
            mock_process_exp.assert_called_once_with(mock_session, plant1, "GOOD")
            mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_calculate_exp_batch_exception():
    with patch("app.scheduler.async_session_factory") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_session.execute.side_effect = Exception("DB error")

        await calculate_exp_batch()

        mock_session.rollback.assert_called_once()


def test_start_stop_scheduler():
    with patch("app.scheduler.scheduler") as mock_scheduler:
        start_scheduler()
        mock_scheduler.add_job.assert_called_once()
        mock_scheduler.start.assert_called_once()

        stop_scheduler()
        mock_scheduler.shutdown.assert_called_once()
