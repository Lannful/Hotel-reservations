
from pydantic import BaseModel, ConfigDict


class SHotel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    location: str
    services: list[str]
    rooms_quantity: int
    image_id: int


class SHotelInfo(SHotel):
    model_config = ConfigDict(from_attributes=True)
    
    rooms_left: int

