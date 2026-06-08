import pytest
from uuid import uuid4
from fastapi import HTTPException, status
from unittest.mock import patch, AsyncMock

from app.dependencies import get_current_user, get_admin_user
from app.models.user import User


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_current_user_success(mock_db):
    user_id = uuid4()
    mock_user = User(id=user_id, role="user")

    with (
        patch("app.dependencies.decode_token") as mock_decode,
        patch(
            "app.dependencies.get_user_by_id", new_callable=AsyncMock
        ) as mock_get_user,
    ):
        mock_decode.return_value = {"sub": str(user_id), "type": "access"}
        mock_get_user.return_value = mock_user

        user = await get_current_user(token="valid_token", db=mock_db)
        assert user.id == user_id
        assert user.role == "user"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db):
    with patch("app.dependencies.decode_token") as mock_decode:
        mock_decode.side_effect = ValueError("Token không hợp lệ")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="invalid_token", db=mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Token không hợp lệ"


@pytest.mark.asyncio
async def test_get_current_user_wrong_token_type(mock_db):
    user_id = uuid4()
    with patch("app.dependencies.decode_token") as mock_decode:
        mock_decode.return_value = {"sub": str(user_id), "type": "refresh"}

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="refresh_token", db=mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Token không phải access token"


@pytest.mark.asyncio
async def test_get_current_user_not_found(mock_db):
    user_id = uuid4()
    with (
        patch("app.dependencies.decode_token") as mock_decode,
        patch(
            "app.dependencies.get_user_by_id", new_callable=AsyncMock
        ) as mock_get_user,
    ):
        mock_decode.return_value = {"sub": str(user_id), "type": "access"}
        mock_get_user.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="valid_token", db=mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Người dùng không tồn tại"


@pytest.mark.asyncio
async def test_get_admin_user_success():
    mock_user = User(id=uuid4(), role="admin")
    admin = await get_admin_user(user=mock_user)
    assert admin.role == "admin"


@pytest.mark.asyncio
async def test_get_admin_user_forbidden():
    """TEST CHỨNG MINH LỖI BROKEN ACCESS CONTROL.

    Đảm bảo user thường cố truy cập endpoint admin sẽ bị văng 403 Forbidden.
    """
    mock_user = User(id=uuid4(), role="user")

    with pytest.raises(HTTPException) as exc_info:
        await get_admin_user(user=mock_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Chỉ Admin mới có quyền truy cập"
