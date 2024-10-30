from typing import Optional
from pydantic import BaseModel, ConfigDict


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False

class PatchItemRequest(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = ConfigDict(
        extra='forbid',
    )

class ItemRequest(BaseModel):
    name: str
    price: float