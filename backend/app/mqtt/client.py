"""MQTT Client — Kết nối MQTT Broker và xử lý telemetry.

Subscribe topic: devices/+/telemetry
Khi nhận message → parse JSON → gọi telemetry_service.process_telemetry()
"""

import json
import logging

from gmqtt import Client as MQTTClient
from gmqtt.mqtt.constants import MQTTv311

from app.config import settings
from app.database import async_session_factory
from app.schemas.telemetry import SensorData
from app.services.auth_service import decode_token
from app.services.telemetry_service import process_telemetry

logger = logging.getLogger(__name__)

# MQTT Topic pattern
TELEMETRY_TOPIC = "devices/+/telemetry"

# Global MQTT client instance
mqtt_client: MQTTClient | None = None


def on_connect(client, flags, rc, properties):
    """Callback khi kết nối MQTT Broker thành công."""
    logger.info("✅ MQTT connected to broker (rc=%d)", rc)
    client.subscribe(TELEMETRY_TOPIC, qos=1)
    logger.info("📡 Subscribed to topic: %s", TELEMETRY_TOPIC)


def on_disconnect(client, packet, exc=None):
    """Callback khi mất kết nối MQTT."""
    logger.warning("⚠️ MQTT disconnected from broker")


async def on_message(client, topic: str, payload: bytes, qos, properties):
    """Callback khi nhận message từ MQTT.

    Topic format: devices/{plant_code}/telemetry
    Payload format: {"sensors": [{"key": "...", "value": ...}, ...]}
    """
    try:
        # Parse topic để lấy plant_code
        parts = topic.split("/")
        if len(parts) != 3 or parts[0] != "devices" or parts[2] != "telemetry":
            logger.warning("MQTT topic không hợp lệ: %s", topic)
            return

        plant_code = parts[1]

        # Parse payload
        data = json.loads(payload.decode("utf-8"))
        # Kiểm tra token
        token = data.get("token")
        if not token:
            logger.warning("MQTT payload thiếu token: %s", topic)
            return

        try:
            token_data = decode_token(token)
            if (
                token_data.get("type") != "device"
                or token_data.get("sub") != plant_code
            ):
                raise ValueError("Token không thuộc về thiết bị này")
        except ValueError as e:
            logger.warning("Lỗi xác thực Telemetry (MQTT) cho %s: %s", plant_code, e)
            return

        sensors = [SensorData(**s) for s in data.get("sensors", [])]

        if not sensors:
            logger.warning("MQTT payload không có dữ liệu sensors: %s", topic)
            return

        # Xử lý telemetry trong DB session riêng
        async with async_session_factory() as session:
            try:
                result = await process_telemetry(session, plant_code, sensors)
                await session.commit()
                logger.debug(
                    "MQTT telemetry xử lý thành công: %s (EXP: %s)",
                    plant_code,
                    result.get("exp_awarded"),
                )
            except Exception:
                await session.rollback()
                raise

    except json.JSONDecodeError:
        logger.error("MQTT payload không phải JSON hợp lệ: %s", topic)
    except ValueError as e:
        logger.warning("MQTT telemetry bị từ chối: %s - %s", topic, e)
    except Exception:
        logger.exception("MQTT on_message lỗi không xác định: %s", topic)


async def start_mqtt() -> MQTTClient | None:
    """Khởi tạo và kết nối MQTT client.

    Được gọi trong FastAPI lifespan startup.
    Trả về None nếu không cấu hình MQTT.
    """
    global mqtt_client

    if not settings.mqtt_broker_host:
        logger.info("MQTT không được cấu hình, bỏ qua.")
        return None

    client = MQTTClient("moc-dao-backend")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Cấu hình auth nếu có
    if settings.mqtt_username:
        client.set_auth_credentials(settings.mqtt_username, settings.mqtt_password)

    try:
        await client.connect(
            settings.mqtt_broker_host,
            settings.mqtt_broker_port,
            version=MQTTv311,
        )
        mqtt_client = client
        logger.info(
            "🔌 MQTT client kết nối tới %s:%d",
            settings.mqtt_broker_host,
            settings.mqtt_broker_port,
        )
        return client
    except Exception:
        logger.exception(
            "❌ Không thể kết nối MQTT broker %s:%d",
            settings.mqtt_broker_host,
            settings.mqtt_broker_port,
        )
        return None


async def stop_mqtt() -> None:
    """Ngắt kết nối MQTT client. Gọi trong shutdown."""
    global mqtt_client
    if mqtt_client:
        await mqtt_client.disconnect()
        mqtt_client = None
        logger.info("🔌 MQTT client đã ngắt kết nối")
