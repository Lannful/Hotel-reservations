from __future__ import annotations

from typing import TYPE_CHECKING

from datetime import date
from sqlalchemy import Computed, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.users.models import Users
    from app.hotels.rooms.models import Rooms


class Bookings(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date_from: Mapped[date] = mapped_column(Date)
    date_to: Mapped[date] = mapped_column(Date)
    price: Mapped[int]
    total_cost: Mapped[int] = mapped_column(Computed("(date_to-date_from) * price"))
    total_days: Mapped[int] = mapped_column(Computed("(date_to-date_from)"))

    user: Mapped["Users"] = relationship(back_populates="bookings")
    room: Mapped["Rooms"] = relationship(back_populates="bookings")

    def __str__(self):
        return f"Booking #{self.id}"