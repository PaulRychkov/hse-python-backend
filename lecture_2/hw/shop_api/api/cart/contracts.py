from pydantic import BaseModel
from typing import List

class ItemInCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

class CartResponse(BaseModel):
    id: int
    items: List[ItemInCart]
    price: float