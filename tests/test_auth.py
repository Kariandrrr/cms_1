import pytest

from src.api.auth.utils_jwt import decode_jwt
from src.api.auth.utils_jwt import hash_password
from src.core.models.user import User, UserRole


@pytest.mark.asyncio
async def test_login_success(client, db_session):
    plain_password = "test_password"
    hashed = hash_password(plain_password)

    user = User(
        username="test_user",
        hashed_password=hashed,
        role=UserRole.EDITOR,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = client.post(
        "/api/auth/login", data={"username": "test_user", "password": "test_password"}
    )
    assert response.status_code == 200, response.text

    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

    decoded = decode_jwt(tokens["access_token"])
    assert decoded["sub"] == "test_user"
    assert "exp" in decoded
    assert isinstance(decoded["exp"], int)
