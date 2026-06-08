"""Router Auth — Xác thực Google OAuth & JWT."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    GoogleLoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_or_create_user,
    get_user_by_id,
    verify_google_token,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/google", response_model=TokenResponse)
async def login_with_google(
    body: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Đăng nhập bằng Google ID Token.

    Frontend gửi Google ID token → Backend xác thực → trả JWT.
    """
    try:
        google_info = await verify_google_token(body.id_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e

    user = await get_or_create_user(db, google_info)

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh JWT access token."""
    try:
        payload = decode_token(body.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không phải refresh token",
        )

    from uuid import UUID

    user = await get_user_by_id(db, UUID(payload["sub"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại",
        )

    access_token = create_access_token(user.id, user.role)
    new_refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
) -> UserResponse:
    """Lấy thông tin user hiện tại."""
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=user.role,
        has_plant=len(user.plants) > 0,
        created_at=user.created_at,
    )


@router.post("/swagger-login", include_in_schema=False)
async def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint ẩn dành riêng cho Swagger UI đăng nhập nhanh.
    - Username: nhập email
    - Password: 'admin' để được cấp quyền admin, nhập tùy ý để làm user thường.
    """
    email = form_data.username
    if settings.app_env != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint này chỉ khả dụng trong môi trường Development",
        )

    if "@" not in email:
        email = f"{email}@moctu.com"

    role = "admin" if form_data.password == "admin" else "user"

    from sqlalchemy import select

    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            google_id=f"dev-{email}",
            display_name=email.split("@")[0],
            role=role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif user.role != role:
        user.role = role
        await db.commit()

    access_token = create_access_token(user.id, user.role)
    return {"access_token": access_token, "token_type": "bearer"}
