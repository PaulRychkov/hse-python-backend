from fastapi import FastAPI
from lecture_2.hw.shop_api.api.cart.routes import router as cart
from lecture_2.hw.shop_api.api.item.routes import router as item

app = FastAPI(title="My Shop API")

app.include_router(cart, prefix="/cart", tags=["Cart"])
app.include_router(item, prefix="/item", tags=["Item"])

@app.get("/")
def read_root():
    return {"message": "Hi! Welcome to my Shop API"}