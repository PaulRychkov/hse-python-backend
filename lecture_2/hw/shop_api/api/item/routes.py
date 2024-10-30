from starlette.responses import Response
from http import HTTPStatus
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from lecture_2.hw.shop_api.store import queries
from lecture_2.hw.shop_api.api.item.contracts import (
    Item,
    PatchItemRequest, 
    ItemRequest
)

router = APIRouter()

@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=Item,
    responses={
        HTTPStatus.CREATED: {
            "description": "new item created",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "failed to create item",
        },
    },
)
async def create_item(item_request: ItemRequest, response: Response) -> Item:
    try:
        item = queries.create_item(item_request)
        response.headers["location"] = f"/item/{item.id}"
        return item
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))

@router.get(
    "/{id}",
    status_code=HTTPStatus.OK,
    response_model=Item,
    responses={
        HTTPStatus.OK: {
            "description": "item successfully returned",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "item not found",
        },
    },
)
async def find_item(id: int) -> Item:
    item = queries.find_item(id)
    if item is None or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="item not found")
    return item

@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=List[Item],
    responses={
        HTTPStatus.OK: {
            "description": "list of items successfully returned",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Item with these request parameters was not found",
        },
    },
)
async def find_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    show_deleted: bool = False,
):
    try:
        items = queries.find_items(offset, limit, min_price, max_price, show_deleted)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    if items is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Items not found")
    return items
    
@router.put(
    "/{id}",
    status_code=HTTPStatus.OK,
    response_model=Item,    
    responses={
        HTTPStatus.OK: {
            "description": "item successfully changed ",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "failed to change item",
        },
    },
)
async def update_item(id: int, item_request: ItemRequest) -> Item:
    try:
        updated_item = queries.update_item(id, item_request)
        if updated_item is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Item not found")
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    return updated_item

@router.patch(
    "/{id}",
    status_code=HTTPStatus.OK,
    response_model=Item,
    responses={
        HTTPStatus.OK: {
            "description": "item modified",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "failed to modify item",
        },
    },

)
async def patch_item(id: int, patch_item_request: PatchItemRequest) -> Item:
    try:
        patched_item = queries.patch_item(id, patch_item_request)
        if patched_item is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Item not found")
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail=str(e))
    return patched_item

@router.delete(
    "/{id}",
    response_model=Item,
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.OK: {"description": "item was successfully deleted"},
        HTTPStatus.NOT_FOUND: {"description": "failed to delete item"},
    },
)
async def delete_item(id: int):
    try:
        item = queries.delete_item(id)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    return item