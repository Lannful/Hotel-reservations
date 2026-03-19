from pydantic import BaseModel, ConfigDict


class SRoom(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    hotel_id: int
    name: str
    description: str | None
    services: list[str]
    price: int
    quantity: int
    image_id: int


class SRoomInfo(SRoom):
    model_config = ConfigDict(from_attributes=True)
    
    total_cost: int
    rooms_left: int