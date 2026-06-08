import asyncio
import logging
from sqlalchemy import select

from app.database import async_session_factory
from app.services.admin_service import provision_device
from app.services.plant_service import pair_plant
from app.models.user import User
from app.models.config import PlantType, RankConfig

logging.basicConfig(level=logging.INFO)


async def test_diy_provision_and_multi_plant():
    async with async_session_factory() as db:
        # Lấy hoặc tạo user test
        stmt = select(User).limit(1)
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user:
            user = User(
                google_id="test_g_id", email="test@test.com", display_name="Test User"
            )
            db.add(user)
            await db.flush()

        # Lấy plant_type
        stmt = select(PlantType).limit(1)
        plant_type = (await db.execute(stmt)).scalar_one_or_none()
        if not plant_type:
            plant_type = PlantType(
                name="Sen Đá",
                soil_moisture_min=10,
                soil_moisture_max=50,
                light_min=100,
                light_max=1000,
                temperature_min=20,
                temperature_max=30,
                humidity_min=30,
                humidity_max=70,
            )
            db.add(plant_type)
            await db.flush()

        # Đảm bảo có RankConfig (Phàm Mộc)
        stmt = select(RankConfig).limit(1)
        rank = (await db.execute(stmt)).scalar_one_or_none()
        if not rank:
            rank = RankConfig(order=1, name="Phàm Mộc", min_exp=0)
            db.add(rank)
            await db.flush()

        # 1. Test cấp mã mạch (DIY Provisioning)
        print("--- TEST 1: Cấp mã (DIY) ---")
        device_info = await provision_device(db)
        print(f"Device Info: {device_info}")

        # 2. Test Pairing (Gỡ giới hạn 1 cây)
        print("--- TEST 2: Liên kết cây ---")
        plant1 = await pair_plant(
            db,
            user,
            device_info["plant_code"],
            device_info["verify_code"],
            "Cây 1",
            plant_type.id,
        )
        print(
            f"Đã liên kết Cây 1: {plant1.name}, Quality: {plant1.current_overall_quality}"
        )

        # Cấp mã 2
        device_info_2 = await provision_device(db)

        # Liên kết cây 2 (sẽ không bị lỗi 1 người 1 cây nữa)
        plant2 = await pair_plant(
            db,
            user,
            device_info_2["plant_code"],
            device_info_2["verify_code"],
            "Cây 2",
            plant_type.id,
        )
        print(
            f"Đã liên kết Cây 2: {plant2.name}, Quality: {plant2.current_overall_quality}"
        )

        await db.commit()
        print("✅ Tất cả bài test (DIY, Đa chậu, Model) hoàn tất xuất sắc!")


if __name__ == "__main__":
    asyncio.run(test_diy_provision_and_multi_plant())
