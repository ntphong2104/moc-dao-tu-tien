#!/usr/bin/env python3
"""Mộc Đạo Tu Tiên — IoT Device Telemetry Simulator Bot.

Script này đóng vai trò như một thiết bị cảm biến thực tế (ESP32) cắm ở chậu cây.
Nó gửi dữ liệu cảm biến định kỳ lên Backend qua REST API hoặc MQTT.

Chạy:
    uv run python tests/bot_simulator.py --code <PLANT_CODE>
"""

import argparse
import asyncio
import json
import random
import sys
import time
from datetime import datetime
import httpx

# Màu sắc terminal
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


class PlantTypeRanges:
    """Ngưỡng lý tưởng mặc định của các loại cây mẫu để bot giả lập chuẩn xác."""

    PLANTS = {
        "KIM_TIEN": {
            "soil_moisture": (30.0, 60.0),
            "light": (500.0, 5000.0),
            "temperature": (18.0, 30.0),
            "humidity": (40.0, 70.0),
        },
        "LUOI_HO": {
            "soil_moisture": (20.0, 50.0),
            "light": (1000.0, 15000.0),
            "temperature": (15.0, 35.0),
            "humidity": (30.0, 70.0),
        },
        "TRAU_BA": {
            "soil_moisture": (40.0, 70.0),
            "light": (1000.0, 8000.0),
            "temperature": (20.0, 32.0),
            "humidity": (50.0, 80.0),
        },
    }


def print_banner():
    """Hiển thị ASCII Art siêu xịn xò của Mộc Đạo Tu Tiên Bot."""
    banner = f"""
{GREEN}{BOLD}      ___           ___           ___     
     /__/\\         /  /\\         /__/\\    
     \\  \\:\\       /  /::\\        \\  \\:\\   
      \\  \\:\\     /  /:/\\:\\        \\  \\:\\  
  {YELLOW}___  \\  \\:\\   /  /:/  \\:\\   {GREEN}____  \\  \\:\\ 
 /__/\\  \\__\\:\\ /__/:/ \\__\\:\\ /__/\\  \\__\\:\\
 \\  \\:\\ /  /:/ \\  \\:\\ /  /:/ \\  \\:\\ /  /:/
  \\  \\:\\  /:/   \\  \\:\\  /:/   \\  \\:\\  /:/ 
   \\  \\:\\/:/     \\  \\:\\/:/     \\  \\:\\/:/  
    \\  \\::/       \\  \\::/       \\  \\::/   
     \\__\\/         \\__\\/         \\__\\/    {RESET}

   {CYAN}{BOLD}MỘC ĐẠO TU TIÊN — THIẾT BỊ GIẢ LẬP IOT (TEST BOT){RESET}
   --------------------------------------------------
    Giả lập ESP32 đo chỉ số môi trường & tu luyện Tu Vi
"""
    print(banner)


def generate_sensor_value(min_val, max_val, condition="excellent"):
    """Sinh chỉ số cảm biến ngẫu nhiên theo chế độ mong muốn.

    Chế độ:
    - excellent: Nằm chuẩn xác ở trung tâm khoảng lý tưởng.
    - good: Lệch nhẹ ra ngoài khoảng lý tưởng (lệch <= 10%).
    - fair: Lệch trung bình (lệch <= 25%).
    - poor: Lệch nhiều, gây tổn hao nhẹ Tu Vi (lệch <= 50%).
    - danger: Lệch cực kỳ nặng, gây tẩu hỏa nhập ma (lệch > 50%).
    - dynamic: Biến động tự nhiên ngẫu nhiên.
    """
    ideal_range = max_val - min_val
    center_val = min_val + ideal_range / 2.0

    if condition == "excellent":
        # Nằm hoàn hảo ở trung tâm lý tưởng
        return round(
            random.uniform(min_val + ideal_range * 0.2, max_val - ideal_range * 0.2), 1
        )

    elif condition == "good":
        # Lệch nhẹ bên ngoài (khoảng 5% đến 8%)
        side = random.choice([-1, 1])
        if side == -1:
            return round(min_val - (ideal_range * random.uniform(0.01, 0.09)), 1)
        else:
            return round(max_val + (ideal_range * random.uniform(0.01, 0.09)), 1)

    elif condition == "fair":
        # Lệch trung bình (khoảng 15% đến 20%)
        side = random.choice([-1, 1])
        if side == -1:
            return round(min_val - (ideal_range * random.uniform(0.12, 0.22)), 1)
        else:
            return round(max_val + (ideal_range * random.uniform(0.12, 0.22)), 1)

    elif condition == "poor":
        # Lệch nặng (khoảng 35% đến 45%)
        side = random.choice([-1, 1])
        if side == -1:
            return round(min_val - (ideal_range * random.uniform(0.30, 0.48)), 1)
        else:
            return round(max_val + (ideal_range * random.uniform(0.30, 0.48)), 1)

    elif condition == "danger":
        # Lệch cực kỳ nghiêm trọng (> 50%)
        side = random.choice([-1, 1])
        if side == -1:
            val = min_val - (ideal_range * random.uniform(0.55, 0.85))
            return round(max(0.0, val), 1)
        else:
            return round(max_val + (ideal_range * random.uniform(0.55, 0.85)), 1)

    else:
        # Ngẫu nhiên bất kỳ, xung quanh trung tâm lý tưởng
        return round(
            random.uniform(
                center_val - ideal_range * 0.6, center_val + ideal_range * 0.6
            ),
            1,
        )


def generate_payload(plant_type="KIM_TIEN", condition="excellent"):
    """Tạo payload telemetry gồm 4 cảm biến cốt lõi."""
    ranges = PlantTypeRanges.PLANTS.get(plant_type, PlantTypeRanges.PLANTS["KIM_TIEN"])

    soil_val = generate_sensor_value(
        ranges["soil_moisture"][0], ranges["soil_moisture"][1], condition
    )
    light_val = generate_sensor_value(ranges["light"][0], ranges["light"][1], condition)
    temp_val = generate_sensor_value(
        ranges["temperature"][0], ranges["temperature"][1], condition
    )
    humid_val = generate_sensor_value(
        ranges["humidity"][0], ranges["humidity"][1], condition
    )

    return {
        "sensors": [
            {"key": "soil_moisture", "value": soil_val},
            {"key": "light", "value": light_val},
            {"key": "temperature", "value": temp_val},
            {"key": "humidity", "value": humid_val},
        ]
    }


async def run_rest_simulator(
    url, plant_code, plant_type, condition, interval, duration
):
    """Giả lập thiết bị gửi dữ liệu qua REST API fallback."""
    headers = {"X-Plant-Code": plant_code, "Content-Type": "application/json"}
    endpoint = f"{url.rstrip('/')}/api/devices/{plant_code}/telemetry"

    print(f"{BLUE}[REST SIMULATOR]{RESET} Khởi động thành công!")
    print(f"👉 Endpoint: {endpoint}")
    print(f"👉 Plant Code: {BOLD}{plant_code}{RESET}")
    print(f"👉 Loại cây giả lập: {BOLD}{plant_type}{RESET}")
    print(f"👉 Chế độ môi trường: {BOLD}{condition.upper()}{RESET}")
    print(f"👉 Chu kỳ gửi: {interval} giây")
    print("--------------------------------------------------\n")

    client = httpx.AsyncClient(timeout=10.0)
    start_time = time.time()
    count = 0

    try:
        while True:
            # Kiểm tra thời gian kết thúc (nếu cấu hình)
            if duration and (time.time() - start_time) > duration:
                print(
                    f"{YELLOW}Đã đạt giới hạn thời gian giả lập ({duration}s). Dừng bot.{RESET}"
                )
                break

            count += 1
            payload = generate_payload(plant_type, condition)
            timestamp = datetime.now().strftime("%H:%M:%S")

            print(f"[{timestamp}] 📡 Đang gửi Telemetry lần #{count}...")
            for s in payload["sensors"]:
                # In chỉ số kèm màu sắc trực quan
                print(f"  - {s['key']}: {BOLD}{s['value']}{RESET}")

            try:
                response = await client.post(endpoint, json=payload, headers=headers)

                if response.status_code == 200:
                    res_data = response.json()
                    status_text = res_data.get("status", "ok")
                    exp_awarded = res_data.get("exp_awarded", False)
                    msg = res_data.get("message", "")

                    color = (
                        GREEN
                        if "thành công" in msg or "EXCELLENT" in msg or "GOOD" in msg
                        else YELLOW
                    )
                    if "DANGER" in msg or "POOR" in msg:
                        color = RED

                    print(
                        f"✨ {GREEN}Kết quả từ Server: {BOLD}HTTP {response.status_code}{RESET}"
                    )
                    print(f"   └ Trạng thái: {BOLD}{status_text.upper()}{RESET}")
                    print(
                        f"   └ Nhận EXP kỳ này: {BOLD}{GREEN if exp_awarded else RED}{exp_awarded}{RESET}"
                    )
                    print(f"   └ Thông điệp: {color}{msg}{RESET}\n")

                elif response.status_code == 403:
                    print(
                        f"❌ {RED}Lỗi xác thực (HTTP 403): X-Plant-Code không khớp.{RESET}"
                    )
                    print("Vui lòng kiểm tra lại `--code` của bạn.\n")
                    break
                elif response.status_code == 400:
                    res_data = response.json()
                    detail = res_data.get("detail", "")
                    print(f"⚠️ {YELLOW}Yêu cầu bị từ chối (HTTP 400): {detail}{RESET}")
                    if "chưa được liên kết" in detail:
                        print(
                            f"💡 {CYAN}Mẹo: Thiết bị cần được liên kết (pair) với một chậu cây của người dùng trước khi gửi telemetry!{RESET}"
                        )
                        print(
                            f"    Vui lòng đăng nhập ứng dụng web và pair Plant Code: {BOLD}{plant_code}{RESET}\n"
                        )
                        break
                    print("")
                else:
                    print(
                        f"❌ {RED}Lỗi Server (HTTP {response.status_code}): {response.text}{RESET}\n"
                    )

            except httpx.RequestError as e:
                print(f"❌ {RED}Không kết nối được tới Backend Server: {e}{RESET}\n")

            await asyncio.sleep(interval)

    finally:
        await client.aclose()


async def run_mqtt_simulator(
    broker_host,
    broker_port,
    username,
    password,
    plant_code,
    plant_type,
    condition,
    interval,
    duration,
):
    """Giả lập thiết bị gửi dữ liệu qua MQTT broker (gmqtt)."""
    try:
        from gmqtt import Client as MQTTClient
        from gmqtt.mqtt.constants import MQTTv311
    except ImportError:
        print(
            f"❌ {RED}Thư viện gmqtt chưa được cài đặt. Vui lòng chạy: uv sync{RESET}"
        )
        return

    topic = f"devices/{plant_code}/telemetry"

    print(
        f"{BLUE}[MQTT SIMULATOR]{RESET} Đang kết nối tới broker {broker_host}:{broker_port}..."
    )

    client = MQTTClient("sim-device-" + plant_code)
    if username:
        client.set_auth_credentials(username, password)

    connected = asyncio.Event()

    def on_connect(c, flags, rc, properties):
        print(f"✅ {GREEN}Kết nối MQTT thành công! (rc={rc}){RESET}")
        connected.set()

    def on_disconnect(c, packet, exc=None):
        print(f"⚠️ {YELLOW}Mất kết nối MQTT Broker{RESET}")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        await client.connect(broker_host, broker_port, version=MQTTv311)
    except Exception as e:
        print(
            f"❌ {RED}Không thể kết nối tới MQTT Broker {broker_host}:{broker_port}: {e}{RESET}"
        )
        return

    await connected.wait()

    print(f"👉 Topic xuất bản: {BOLD}{topic}{RESET}")
    print(f"👉 Plant Code: {BOLD}{plant_code}{RESET}")
    print(f"👉 Loại cây giả lập: {BOLD}{plant_type}{RESET}")
    print(f"👉 Chế độ môi trường: {BOLD}{condition.upper()}{RESET}")
    print(f"👉 Chu kỳ gửi: {interval} giây")
    print("--------------------------------------------------\n")

    start_time = time.time()
    count = 0

    try:
        while True:
            if duration and (time.time() - start_time) > duration:
                print(
                    f"{YELLOW}Đã đạt giới hạn thời gian giả lập. Dừng MQTT simulator.{RESET}"
                )
                break

            count += 1
            payload = generate_payload(plant_type, condition)
            payload_str = json.dumps(payload)
            timestamp = datetime.now().strftime("%H:%M:%S")

            print(f"[{timestamp}] 📡 [MQTT] Đang xuất bản dữ liệu lần #{count}...")
            for s in payload["sensors"]:
                print(f"  - {s['key']}: {BOLD}{s['value']}{RESET}")

            client.publish(topic, payload_str, qos=1)
            print(f"✨ {GREEN}Đã gửi message lên topic thành công!{RESET}\n")

            await asyncio.sleep(interval)

    finally:
        await client.disconnect()


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Mộc Đạo Tu Tiên — Giả lập thiết bị cảm biến IoT"
    )

    # Cấu hình thiết bị
    parser.add_argument(
        "--code",
        type=str,
        required=True,
        help="Plant Code của thiết bị (ví dụ: ABC123XY)",
    )
    parser.add_argument(
        "--type",
        type=str,
        default="KIM_TIEN",
        choices=["KIM_TIEN", "LUOI_HO", "TRAU_BA"],
        help="Loại cây để giả lập chỉ số tối ưu",
    )

    # Chế độ gửi dữ liệu
    parser.add_argument(
        "--mode",
        type=str,
        default="rest",
        choices=["rest", "mqtt"],
        help="Giao thức gửi dữ liệu: rest (REST API) hoặc mqtt (MQTT Broker)",
    )
    parser.add_argument(
        "--condition",
        type=str,
        default="excellent",
        choices=["excellent", "good", "fair", "poor", "danger", "random"],
        help="Mức độ lý tưởng của môi trường cây",
    )

    # Tần suất gửi
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Chu kỳ gửi chỉ số (giây). Khuyến nghị >= 60 giây do anti-spam của Backend",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Thời gian giả lập (giây). 0 nghĩa là chạy vĩnh viễn",
    )

    # Địa chỉ kết nối
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="URL của Backend API (chỉ dùng ở chế độ rest)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Địa chỉ MQTT Broker (chỉ dùng ở chế độ mqtt)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=1883,
        help="Cổng MQTT Broker (chỉ dùng ở chế độ mqtt)",
    )
    parser.add_argument(
        "--username", type=str, default=None, help="Username MQTT Broker"
    )
    parser.add_argument(
        "--password", type=str, default=None, help="Password MQTT Broker"
    )

    args = parser.parse_args()

    # Cảnh báo chu kỳ gửi nhỏ hơn 55 giây
    if args.interval < 55:
        print(
            f"{YELLOW}⚠️ CẢNH BÁO: Khoảng thời gian gửi ({args.interval}s) nhỏ hơn 55 giây.{RESET}"
        )
        print(
            "Backend có cơ chế chống spam (anti-spam), nếu gửi quá nhanh sẽ bị từ chối cộng EXP!"
        )
        print("Nên để `--interval 60` để kiểm tra chu kỳ tính điểm hoàn chỉnh.\n")

    try:
        if args.mode == "rest":
            asyncio.run(
                run_rest_simulator(
                    url=args.url,
                    plant_code=args.code.upper(),
                    plant_type=args.type,
                    condition=args.condition,
                    interval=args.interval,
                    duration=args.duration,
                )
            )
        else:
            asyncio.run(
                run_mqtt_simulator(
                    broker_host=args.host,
                    broker_port=args.port,
                    username=args.username,
                    password=args.password,
                    plant_code=args.code.upper(),
                    plant_type=args.type,
                    condition=args.condition,
                    interval=args.interval,
                    duration=args.duration,
                )
            )
    except KeyboardInterrupt:
        print(
            f"\n{YELLOW}🛑 Đã nhận tín hiệu dừng (KeyboardInterrupt). Đang thoát bot giả lập...{RESET}"
        )
        print(
            "Tạm biệt đạo hữu, chúc cây của đạo hữu sớm ngày đắc đạo thành tiên! 🌸\n"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
