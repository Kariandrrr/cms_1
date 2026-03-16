import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.api.auth.utils_jwt import encode_jwt, hash_password
from src.core.models.base import Base
from src.core.models.db_helper import get_db
from src.core.models.post import Post
from src.core.models.user import User, UserRole
from src.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def editor_user(db_session: AsyncSession):
    plain_password = "editor123safe"
    hashed = hash_password(plain_password)

    user = User(
        username=f"editor_test_{id(db_session)}",
        hashed_password=hashed,
        role=UserRole.EDITOR,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def editor_token(editor_user: User):
    payload = {
        "sub": editor_user.username,
        "role": editor_user.role.value,
    }
    return encode_jwt(payload)


@pytest.fixture(scope="function")
async def viewer_user(db_session: AsyncSession):
    plain_password = "editor123safes"
    hashed = hash_password(plain_password)

    user = User(
        username=f"editor_test_{id(db_session)}",
        hashed_password=hashed,
        role=UserRole.USER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def viewer_token(viewer_user: User):
    payload = {"sub": viewer_user.username, "role": viewer_user.role.value}
    return encode_jwt(payload)


@pytest.fixture(scope="function")
async def test_post(db_session: AsyncSession, editor_user: User):
    post = Post(
        title="Тестовый пост для тестов",
        content="<p>Контент тестового поста</p>",
        slug="test-post-slug",
        status="draft",
        author_id=editor_user.id,
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post
