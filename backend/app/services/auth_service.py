"""Auth Service — Xác thực Google OAuth & quản lý JWT tokens."""

import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

import httpx
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


async def verify_google_token(id_token: str) -> dict:
    """Xác thực Google ID token và trả về thông tin user.

    Gọi Google tokeninfo endpoint để validate token.
    Trả về dict chứa: sub, email, name, picture.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_TOKENINFO_URL,
            params={"id_token": id_token},
        )

    if response.status_code != 200:
        raise ValueError("Google ID token không hợp lệ")

    payload = response.json()

    # Kiểm tra audience (client_id)
    if settings.google_client_id and payload.get("aud") != settings.google_client_id:
        raise ValueError("Token audience không khớp với ứng dụng")

    return {
        "google_id": payload["sub"],
        "email": payload["email"],
        "display_name": payload.get("name", payload["email"]),
        "avatar_url": payload.get("picture"),
    }


async def get_or_create_user(db: AsyncSession, google_info: dict) -> User:
    """Tìm hoặc tạo user từ thông tin Google.

    - Nếu google_id đã tồn tại: cập nhật thông tin mới nhất và trả về.
    - Nếu chưa: tạo user mới với role "user".
    """
    stmt = select(User).where(User.google_id == google_info["google_id"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        # Cập nhật thông tin mới nhất từ Google
        user.display_name = google_info["display_name"]
        user.avatar_url = google_info.get("avatar_url")
        logger.info("User đăng nhập lại: %s", user.email)
    else:
        # Tạo user mới
        user = User(
            google_id=google_info["google_id"],
            email=google_info["email"],
            display_name=google_info["display_name"],
            avatar_url=google_info.get("avatar_url"),
            role="user",
        )
        db.add(user)
        await db.flush()
        logger.info("User mới được tạo: %s", user.email)

    return user


def create_access_token(user_id: UUID, role: str) -> str:
    """Tạo JWT access token."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_refresh_token(user_id: UUID) -> str:
    """Tạo JWT refresh token."""
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_device_token(plant_code: str) -> str:
    """Tạo JWT access token dành riêng cho thiết bị phần cứng.

    Hạn sử dụng: 10 năm (chuẩn cho thiết bị IoT ít cập nhật).
    """
    expire = datetime.now(UTC) + timedelta(days=3650)
    payload = {
        "sub": plant_code,
        "type": "device",
        "exp": expire,
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> dict:
    """Giải mã và xác thực JWT token.

    Raises:
        ValueError: Token không hợp lệ hoặc hết hạn.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token không hợp lệ: {e}") from e


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """Tìm user theo ID."""
    from sqlalchemy.orm import selectinload

    stmt = select(User).options(selectinload(User.plants)).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
