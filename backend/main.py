"""Mộc Đạo Tu Tiên — Backend Entry Point.

FastAPI application với:
- CORS middleware
- Lifespan: startup (DB, MQTT) / shutdown
- Tất cả API routers
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.mqtt.client import start_mqtt, stop_mqtt
from app.scheduler import start_scheduler, stop_scheduler
from app.routers import admin, auth, devices, leaderboard, plants, sse

# Cấu hình logging
logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý vòng đời ứng dụng: startup & shutdown."""
    # --- Startup ---
    logger.info("🌱 Mộc Đạo Tu Tiên Backend đang khởi động...")

    # Kết nối MQTT (non-blocking, bỏ qua nếu không cấu hình)
    try:
        await start_mqtt()
    except Exception:
        logger.exception("MQTT khởi tạo thất bại, tiếp tục chạy không MQTT")

    try:
        start_scheduler()
    except Exception:
        logger.exception("Scheduler khởi tạo thất bại")

    logger.info("✅ Backend sẵn sàng phục vụ!")

    yield

    # --- Shutdown ---
    logger.info("🛑 Đang tắt Backend...")
    stop_scheduler()
    await stop_mqtt()
    logger.info("👋 Backend đã tắt hoàn toàn")


# Khởi tạo FastAPI app
app = FastAPI(
    title="Mộc Đạo Tu Tiên API",
    description=(
        "Backend API cho hệ thống IoT + Gamification 'Mộc Đạo Tu Tiên'. "
        "Biến việc chăm sóc cây xanh thành hành trình tu tiên đắc đạo."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(plants.router)
app.include_router(devices.router)
app.include_router(leaderboard.router)
app.include_router(admin.router)
app.include_router(sse.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "name": "Mộc Đạo Tu Tiên API",
        "version": "1.0.0",
        "status": "running",
        "message": "🌱 Hành trình tu tiên bắt đầu tại đây!",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Kiểm tra trạng thái hệ thống."""
    return {"status": "healthy"}
