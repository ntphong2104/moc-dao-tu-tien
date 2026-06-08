"""Background Scheduler for Gamification (Batch EXP calculation)."""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import UTC, datetime, timedelta
from app.database import async_session_factory
from app.models.plant import Plant
from app.services.exp_service import process_exp

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def calculate_exp_batch():
    """Lặp qua tất cả các cây và cộng Tu Vi định kỳ."""
    logger.info("⏱️ Bắt đầu tiến trình cộng Tu Vi định kỳ...")
    async with async_session_factory() as db:
        try:
            # Lấy tất cả các cây đang Active kèm rank và device
            stmt = select(Plant).options(
                selectinload(Plant.current_rank), selectinload(Plant.device)
            )
            result = await db.execute(stmt)
            plants = result.scalars().all()

            # Ngưỡng offline là 15 phút không gửi dữ liệu
            offline_threshold = datetime.now(UTC) - timedelta(minutes=15)

            for plant in plants:
                # Bỏ qua nếu không có thiết bị hoặc thiết bị đã offline
                if (
                    not plant.device
                    or not plant.device.last_seen_at
                    or plant.device.last_seen_at < offline_threshold
                ):
                    continue

                # Tính điểm dựa trên current_overall_quality
                await process_exp(db, plant, plant.current_overall_quality)

            # Flush changes to DB
            await db.commit()
            logger.info(f"✅ Đã cộng Tu Vi cho {len(plants)} chậu cây.")
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Lỗi khi cộng Tu Vi định kỳ: {e}")


def start_scheduler():
    """Khởi động bộ lập lịch."""
    # Chạy mỗi 1 phút để thử nghiệm (có thể đổi thành 1 giờ trên production)
    scheduler.add_job(
        calculate_exp_batch,
        "interval",
        minutes=1,
        id="exp_batch_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("🚀 Đã khởi động Background Scheduler (APScheduler).")


def stop_scheduler():
    """Dừng bộ lập lịch."""
    scheduler.shutdown()
    logger.info("🛑 Đã dừng Background Scheduler.")
