from typing import Iterable, List

from lecture_2.hw.shop_api.store.models import (
    Cart, 
    ItemInCart, 
    Item
)

from lecture_2.hw.shop_api.api.item.contracts import (
    ItemRequest,
    PatchItemRequest
)

item_data = dict[int, Item]()
cart_data = dict[int, Cart]()

def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1

_cart_id_generator = int_id_generator()
_item_id_generator = int_id_generator()

def add_cart() -> int:
    _id = next(_cart_id_generator)
    cart = Cart(id=_id)
    cart_data[_id] = cart
    return cart

def find_cart(id: int) -> Cart | None:
    return cart_data.get(id)

def find_carts(min_price: float | None,
                   max_price: float | None,
                   min_quantity: int | None, 
                   max_quantity: int | None, 
                   offset: int = 0, 
                   limit: int = 10) -> List[Cart]:    
    filtered_carts = [cart for cart in cart_data.values() if (min_price is None or cart.price >= min_price) and (max_price is None or cart.price <= max_price)]    
    if max_quantity is not None:
        filtered_carts = [cart for cart in filtered_carts if sum(item.quantity for item in cart.items) <= max_quantity]
    if min_quantity is not None:
        filtered_carts = [cart for cart in filtered_carts if sum(item.quantity for item in cart.items) >= min_quantity]    
    return filtered_carts[offset : offset + limit]

def add_item(cart_id: int, item_id: int) -> Cart:
    cart = find_cart(cart_id)
    if cart is None:
        raise ValueError(f"cant found cart: {cart_id}")

    item = find_item(item_id)
    if item is None:
        raise ValueError(f"cant found item: {item_id}")

    item_dict = {it.id: it for it in cart.items}

    if item_id in item_dict:
        item_in_cart = item_dict[item_id]
        item_in_cart.quantity += 1
    else:
        cart.items.append(ItemInCart(id=item.id, name=item.name, quantity=1, available=True))

    cart.price += item.price
    return cart

def create_item(item_request: ItemRequest) -> Item:
    _id = next(_item_id_generator)
    item = Item(id=_id, name=item_request.name, price=item_request.price)
    item_data[_id] = item
    return item

def find_item(id: int) -> Item | None:
    return item_data.get(id)

def find_items(offset: int, limit: int, min_price: float | None, max_price: float | None, show_deleted: bool) -> List[Item]:
    result = [
        item for item in item_data.values()
        if (min_price is None or item.price >= min_price) and
           (max_price is None or item.price <= max_price) and
           (show_deleted or not item.deleted)
    ]
    return result[offset: offset + limit]

def update_item(id: int, item_request: ItemRequest) -> Item:
    item = find_item(id)
    if not item or item.deleted:
        return None
    item.name = item_request.name
    item.price = item_request.price
    return item

def patch_item(id: int, patch_item_request: PatchItemRequest) -> Item:
    item = find_item(id)
    if not item or item.deleted:
        return None
    if patch_item_request.name:
        item.name = patch_item_request.name
    if patch_item_request.price:
        item.price = patch_item_request.price
    return item

def delete_item(id: int) -> Item | None:
    item = item_data.get(id)
    if not item:
        return None
    item.deleted = True
    return item