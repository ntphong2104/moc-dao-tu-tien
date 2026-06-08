import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.mqtt.client import (
    on_connect,
    on_disconnect,
    on_message,
    start_mqtt,
    stop_mqtt,
)
from app.config import settings


@pytest.fixture
def mock_mqtt_client():
    client = MagicMock()
    return client


def test_on_connect(mock_mqtt_client):
    on_connect(mock_mqtt_client, None, 0, None)
    mock_mqtt_client.subscribe.assert_called_with("devices/+/telemetry", qos=1)


def test_on_disconnect(mock_mqtt_client):
    # Just to ensure it doesn't crash
    on_disconnect(mock_mqtt_client, None, None)


@pytest.mark.asyncio
async def test_on_message_success():
    payload = json.dumps({"sensors": [{"key": "light", "value": 100}]}).encode("utf-8")

    with patch(
        "app.mqtt.client.process_telemetry", new_callable=AsyncMock
    ) as mock_process:
        mock_process.return_value = {"exp_awarded": 10}
        with patch("app.mqtt.client.async_session_factory") as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session

            await on_message(None, "devices/TEST_PLANT/telemetry", payload, 0, None)

            mock_process.assert_called_once()
            mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_on_message_invalid_topic():
    # Should ignore quietly
    await on_message(None, "invalid/topic", b"{}", 0, None)


@pytest.mark.asyncio
async def test_on_message_empty_sensors():
    payload = json.dumps({"sensors": []}).encode("utf-8")
    await on_message(None, "devices/TEST_PLANT/telemetry", payload, 0, None)


@pytest.mark.asyncio
async def test_on_message_invalid_json():
    await on_message(None, "devices/TEST_PLANT/telemetry", b"invalid json", 0, None)


@pytest.mark.asyncio
async def test_on_message_process_value_error():
    payload = json.dumps({"sensors": [{"key": "light", "value": 100}]}).encode("utf-8")

    with patch(
        "app.mqtt.client.process_telemetry", new_callable=AsyncMock
    ) as mock_process:
        mock_process.side_effect = ValueError("Thiết bị không tồn tại")
        with patch("app.mqtt.client.async_session_factory") as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session

            await on_message(None, "devices/TEST_PLANT/telemetry", payload, 0, None)
            # Should catch ValueError and not crash


@pytest.mark.asyncio
async def test_on_message_process_exception():
    payload = json.dumps({"sensors": [{"key": "light", "value": 100}]}).encode("utf-8")

    with patch(
        "app.mqtt.client.process_telemetry", new_callable=AsyncMock
    ) as mock_process:
        mock_process.side_effect = Exception("Unknown error")
        with patch("app.mqtt.client.async_session_factory") as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session

            await on_message(None, "devices/TEST_PLANT/telemetry", payload, 0, None)
            # Should rollback
            mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_start_mqtt_disabled():
    old_host = settings.mqtt_broker_host
    settings.mqtt_broker_host = ""
    res = await start_mqtt()
    assert res is None
    settings.mqtt_broker_host = old_host


@pytest.mark.asyncio
async def test_start_mqtt_success():
    old_host = settings.mqtt_broker_host
    settings.mqtt_broker_host = "localhost"
    settings.mqtt_username = "test"

    with patch("app.mqtt.client.MQTTClient") as mock_client_class:
        mock_instance = MagicMock()
        mock_instance.connect = AsyncMock()
        mock_client_class.return_value = mock_instance

        res = await start_mqtt()
        assert res is not None
        mock_instance.connect.assert_called_once()
        mock_instance.set_auth_credentials.assert_called_once()

    settings.mqtt_broker_host = old_host


@pytest.mark.asyncio
async def test_start_mqtt_success_no_auth():
    old_host = settings.mqtt_broker_host
    old_user = settings.mqtt_username
    settings.mqtt_broker_host = "localhost"
    settings.mqtt_username = ""

    with patch("app.mqtt.client.MQTTClient") as mock_client_class:
        mock_instance = MagicMock()
        mock_instance.connect = AsyncMock()
        mock_client_class.return_value = mock_instance

        res = await start_mqtt()
        assert res is not None
        mock_instance.connect.assert_called_once()
        mock_instance.set_auth_credentials.assert_not_called()

    settings.mqtt_broker_host = old_host
    settings.mqtt_username = old_user


@pytest.mark.asyncio
async def test_start_mqtt_exception():
    old_host = settings.mqtt_broker_host
    settings.mqtt_broker_host = "localhost"

    with patch("app.mqtt.client.MQTTClient") as mock_client_class:
        mock_instance = MagicMock()
        mock_instance.connect = AsyncMock(side_effect=Exception("Failed"))
        mock_client_class.return_value = mock_instance

        res = await start_mqtt()
        assert res is None

    settings.mqtt_broker_host = old_host


@pytest.mark.asyncio
async def test_stop_mqtt():
    # Force mock client into global state
    import app.mqtt.client as client_module

    mock_instance = MagicMock()
    mock_instance.disconnect = AsyncMock()
    client_module.mqtt_client = mock_instance

    await stop_mqtt()
    mock_instance.disconnect.assert_called_once()
    assert client_module.mqtt_client is None

    # Test stop when already None
    await stop_mqtt()  # Should not crash
