"""Dependencies — Các dependency chung cho FastAPI routes."""

import logging
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.auth_service import decode_token, get_user_by_id

logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/swagger-login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency: Xác thực JWT và trả về User hiện tại.

    Sử dụng OAuth2PasswordBearer để có form đăng nhập trực tiếp trên Swagger UI.
    """

    try:
        payload = decode_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không phải access token",
        )

    user_id = UUID(payload["sub"])
    user = await get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại",
        )

    return user


async def get_admin_user(
    user: User = Depends(get_current_user),
) -> User:
    """Dependency: Yêu cầu user phải là Admin.

    Sử dụng cho các route Admin-only.
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Admin mới có quyền truy cập",
        )
    return user
