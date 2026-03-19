from fastapi import UploadFile
from fastapi.routing import APIRouter
import aiofiles

from app.tasks.tasks import process_pic


router = APIRouter(
    prefix="/images",
    tags=["Загрузка картинок"]
)


@router.post("/hotels")
async def add_hotel_image(name: int, file: UploadFile):
    im_path = f"app/static/images/{name}.webp"
    async with aiofiles.open(im_path, "wb+") as file_object:
        file_content = await file.read()
        await file_object.write(file_content)
    process_pic.delay(im_path)
