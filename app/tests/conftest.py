import asyncio
import json
import pytest
import pytest_asyncio
from datetime import date
from sqlalchemy import insert
from app.config import settings
from app.database import Base, async_session_maker, engine

from app.bookings.models import Bookings
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.users.models import Users
from app.users.auth import get_password_hash

from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app as fastapi_app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/unit_tests/mock_{model}.json", encoding="utf-8") as file:
            return json.load(file)

    # Загружаем mock данные
    hotels = open_mock_json("hotels")
    rooms = open_mock_json("rooms")
    users_raw = open_mock_json("users")
    bookings_raw = open_mock_json("bookings")
    
    # Генерируем правильные Argon2 хеши для паролей пользователей
    # Пароли: test@test.com -> "test", artem@example.com -> "artem"
    password_map = {
        "test@test.com": "test",
        "artem@example.com": "artem"
    }
    users = [
        {
            **user,
            "hashed_password": get_password_hash(password_map.get(user["email"], "default"))
        }
        for user in users_raw
    ]
    
    # Конвертируем строки дат в объекты date для bookings
    bookings = [
        {
            **booking,
            "date_from": date.fromisoformat(booking["date_from"]),
            "date_to": date.fromisoformat(booking["date_to"]),
        }
        for booking in bookings_raw
    ]
    
    # Вставляем данные в базу
    async with async_session_maker() as session:
        add_hotels = insert(Hotels).values(hotels)
        add_rooms = insert(Rooms).values(rooms)
        add_users = insert(Users).values(users)
        add_bookings = insert(Bookings).values(bookings)

        await session.execute(add_hotels)
        await session.execute(add_rooms)
        await session.execute(add_users)
        await session.execute(add_bookings)

        await session.commit()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac
        
@pytest.fixture(scope="session")
async def authenticated_ac():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        await ac.post("auth/login", json={
            "email": "test@test.com",
            "password": "test", 
        })
        assert ac.cookies["booking_access_token"]
        yield ac

@pytest.fixture(scope="function")
async def session():
    async with async_session_maker() as session:
        yield session