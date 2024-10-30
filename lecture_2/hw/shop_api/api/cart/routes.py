from starlette.responses import Response
from http import HTTPStatus
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from lecture_2.hw.shop_api.store import queries
from lecture_2.hw.shop_api.api.cart.contracts import CartResponse

router = APIRouter()

@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=CartResponse,
    responses={
        HTTPStatus.CREATED: {
            "description": "New cart created",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "error when creating a new cart",
        },
    },
)
async def add_cart(response: Response) -> CartResponse:
    try:
        cart = queries.add_cart()
        response.headers["location"] = f"/cart/{cart.id}"
        return cart
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))

@router.get(
    "/{cart_id}",
    status_code=HTTPStatus.OK,
    response_model=CartResponse,
    responses={
        HTTPStatus.OK: {
            "description": "Cart successfully returned",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Cart was not found",
        },
    },
)
async def find_cart(cart_id: int) -> CartResponse:
    try:
        cart = queries.find_cart(cart_id)
        if cart is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Cart was not found"
            )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    return cart

@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=List[CartResponse],
    responses={
        HTTPStatus.OK: {
            "description": "Cart successfully returned",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Request could not be processed",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Cart with these request parameters was not found",
        },
    },
)
async def find_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_quantity: Optional[int] = Query(None, ge=0),
    max_quantity: Optional[int] = Query(None, ge=0),
) -> List[CartResponse]:
    try:
        carts = queries.find_carts(
            min_price, max_price, min_quantity, max_quantity, offset, limit
        )
        if not carts:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Cart with these request parameters was not found"
            )
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Internal error occurred")        
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=f"Invalid input: {e}")
    return carts

@router.post(
    "/{cart_id}/add/{item_id}",
    status_code=HTTPStatus.CREATED,
    response_model=CartResponse,
    responses={
        HTTPStatus.CREATED: {
            "description": "successfully added item to cart",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "failed to add item to cart",
        },
    },
)
async def add_item(cart_id: int, item_id: int) -> CartResponse:
    try:
        cart = queries.add_item(cart_id, item_id)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    return cart