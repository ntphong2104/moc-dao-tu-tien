import pytest
from uuid import uuid4
from datetime import UTC, datetime, timedelta
from jose import jwt
from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock, AsyncMock

from app.config import settings
from app.models.user import User
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_or_create_user,
    get_user_by_id,
    verify_google_token,
)


@pytest.fixture
def mock_google_info():
    return {
        "google_id": "test_google_id_123",
        "email": "test@moctu.com",
        "display_name": "Test User",
        "avatar_url": "https://example.com/avatar.jpg",
    }


def test_create_access_token():
    user_id = uuid4()
    token = create_access_token(user_id, "user")

    # Verify the generated token
    payload = jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "user"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_refresh_token():
    user_id = uuid4()
    token = create_refresh_token(user_id)

    payload = jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_decode_token_valid():
    user_id = uuid4()
    token = create_access_token(user_id, "admin")

    decoded = decode_token(token)
    assert decoded["sub"] == str(user_id)
    assert decoded["role"] == "admin"


def test_decode_token_invalid():
    with pytest.raises(ValueError, match="Token không hợp lệ"):
        decode_token("invalid.token.string")


def test_decode_token_expired():
    """Kiểm tra rằng token hết hạn bị từ chối — security edge case."""
    user_id = uuid4()
    expired_payload = {
        "sub": str(user_id),
        "role": "user",
        "type": "access",
        # Đặt thời gian hết hạn là 1 giờ trước
        "exp": datetime.now(UTC) - timedelta(hours=1),
    }
    expired_token = jwt.encode(
        expired_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    with pytest.raises(ValueError, match="Token không hợp lệ"):
        decode_token(expired_token)


# Mock async db session for get_or_create_user
class MockResult:
    def __init__(self, user):
        self.user = user

    def scalar_one_or_none(self):
        return self.user


class MockAsyncSession:
    """Mock SQLAlchemy AsyncSession để tránh kết nối DB thật trong unit test.

    Dùng `mock_db` dict để lưu user theo google_id như một in-memory database.
    Tương thích với SQLAlchemy 2.0: execute() nhận Select statement và trả
    về MockResult mà không phụ thuộc vào nội dung SQL string.
    """

    def __init__(self):
        self.added = []
        self.flushed = False
        self.mock_db: dict = {}
        # Đếm số lần execute() được gọi để kiểm tra luồng chạy
        self._execute_count = 0

    async def execute(self, stmt):
        self._execute_count += 1
        # Đọc google_id từ WHERE clause của SELECT statement
        # SQLAlchemy 2.0: compile stmt thành string để trích xuất tham số
        compiled = stmt.compile(compile_kwargs={"literal_binds": True})
        stmt_str = str(compiled)
        # Tìm google_id trong mock_db từ stmt string
        for google_id, user in self.mock_db.items():
            if google_id in stmt_str:
                return MockResult(user)
        return MockResult(None)

    def add(self, instance):
        self.added.append(instance)

    async def flush(self):
        self.flushed = True


@pytest.mark.asyncio
async def test_get_or_create_user_new(mock_google_info):
    db = MockAsyncSession()

    user = await get_or_create_user(cast(AsyncSession, db), mock_google_info)

    assert user.google_id == "test_google_id_123"
    assert user.email == "test@moctu.com"
    assert user.display_name == "Test User"
    assert user.role == "user"
    assert len(db.added) == 1
    assert db.flushed is True


@pytest.mark.asyncio
async def test_get_or_create_user_existing(mock_google_info):
    db = MockAsyncSession()

    existing_user = User(
        id=uuid4(),
        google_id="test_google_id_123",
        email="test@moctu.com",
        display_name="Old Name",
        role="user",
    )
    db.mock_db["test_google_id_123"] = existing_user

    user = await get_or_create_user(cast(AsyncSession, db), mock_google_info)

    assert user.id == existing_user.id
    assert user.display_name == "Test User"  # should be updated
    # Không gọi db.add(existing_user) khi cập nhật vì SQLAlchemy tự động theo dõi
    # trạng thái thay đổi của đối tượng (dirty state tracking) thông qua Unit of Work
    # và sẽ tự động sinh lệnh UPDATE khi commit/flush.
    assert len(db.added) == 0


@pytest.mark.asyncio
async def test_get_user_by_id():
    db = AsyncMock()
    user = User(id=uuid4(), email="test@moctu.com")

    # Just mock execute
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    db.execute.return_value = mock_result

    res = await get_user_by_id(cast(AsyncSession, db), user.id)
    assert res is not None
    assert res.email == "test@moctu.com"


@pytest.mark.asyncio
async def test_verify_google_token_success():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "123",
            "email": "test@google.com",
            "name": "Test",
        }
        mock_get.return_value = mock_response

        from app.config import settings

        old_aud = settings.google_client_id
        settings.google_client_id = ""  # Disable audience check

        res = await verify_google_token("valid_token")
        assert res["email"] == "test@google.com"

        settings.google_client_id = old_aud


@pytest.mark.asyncio
async def test_verify_google_token_invalid():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Google ID token không hợp lệ"):
            await verify_google_token("invalid_token")


@pytest.mark.asyncio
async def test_verify_google_token_wrong_aud():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "123",
            "email": "test@google.com",
            "name": "Test",
            "aud": "wrong_aud",
        }
        mock_get.return_value = mock_response

        from app.config import settings

        old_aud = settings.google_client_id
        settings.google_client_id = "correct_aud"

        with pytest.raises(ValueError, match="Token audience không khớp"):
            await verify_google_token("valid_token")

        settings.google_client_id = old_aud
