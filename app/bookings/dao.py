from datetime import date

from sqlalchemy import and_, func, insert, or_, select, delete
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions import RoomFullyBooked
from app.hotels.rooms.models import Rooms
from app.logger import logger


class BookingDAO(BaseDAO):
    model = Bookings
    
    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE room_id = 1 AND 
            (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
            (date_from <= '2023-05-15' AND date_to >= '2023-05-15')
        )
        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id
        """
        try:
            async with async_session_maker() as session:
                booked_rooms = select(Bookings).where(
                    and_(
                        Bookings.room_id == room_id,
                        or_(
                            and_(
                                Bookings.date_from >= date_from,
                                Bookings.date_from <= date_to
                            ),
                            and_(
                                Bookings.date_from <= date_from,
                                Bookings.date_to > date_from
                            ),
                        )
                    )
                ).cte("booked_rooms")

                """
                SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
                LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
                WHERE rooms.id = 1
                GROUP BY rooms.quantity, booked_rooms.room_id
                """

                get_rooms_left = select(
                    (Rooms.quantity - func.count(booked_rooms.c.room_id)).label("rooms_left")
                    ).select_from(Rooms).join(
                        booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True
                    ).where(Rooms.id == room_id).group_by(
                        Rooms.quantity, booked_rooms.c.room_id
                    )

                rooms_left_result = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left_result.scalar() or 0
                
                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price_result = await session.execute(get_price)
                    price: int = price_result.scalar()
                    if price is None:
                        return None
                    add_booking = insert(Bookings).values(
                        room_id=room_id,
                        user_id=user_id,
                        date_from=date_from,
                        date_to=date_to,
                        price=price,
                    ).returning(Bookings)

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.scalar()
                else:
                    raise RoomFullyBooked
        except RoomFullyBooked:
            # Пробрасываем исключение о полностью забронированном номере дальше
            raise
        except SQLAlchemyError as e:
            msg = "Database Exc: Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)
            return None
        except Exception as e:
            msg = "Unknown Exc: Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)
            return None 
    
    @classmethod
    async def delete(cls, id: int, user_id: int):
        async with async_session_maker() as session:
            query = delete(cls.model).where(
                and_(
                    cls.model.id == id,
                    cls.model.user_id == user_id
                )
            )
            await session.execute(query)
            await session.commit()