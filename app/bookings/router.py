from datetime import date
from fastapi import APIRouter, Depends
from pydantic import TypeAdapter
from fastapi import BackgroundTasks
from fastapi_versioning import version

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.tasks.tasks import send_booking_confirmation_email
from app.users.models import Users 
from app.users.dependencies import get_current_user
from app.exceptions import RoomFullyBooked

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"]
)



@router.get("")
@version(1)
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBooking]:
    return await BookingDAO.find_all(user_id=user.id)


@router.post("")
@version(1)
async def add_booking(
    background_tasks: BackgroundTasks,
    room_id: int, 
    date_from: date, 
    date_to: date,
    user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomFullyBooked
    booking_dict = TypeAdapter(SBooking).validate_python(booking).model_dump()
    # вариант с celery
    # send_booking_confirmation_email.delay(booking_dict, user.email)
    # вариант встроенный background tasks
    background_tasks.add_task(send_booking_confirmation_email, booking_dict, user.email)
    return booking_dict

@router.delete("/{booking_id}")
@version(1)
async def delete_booking(
    booking_id: int,
    user: Users = Depends(get_current_user),
):
    await BookingDAO.delete(id=booking_id, user_id=user.id)
    return {"message": "Booking deleted successfully"}
  