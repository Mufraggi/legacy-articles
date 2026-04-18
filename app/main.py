from fastapi import FastAPI
from app.routes import orders, products, customers
import uvicorn

app = FastAPI(
    title="Order Management API",
    description="Internal order management system",
    version="1.0.0"
)

app.include_router(orders.router)
app.include_router(products.router)
app.include_router(customers.router)


@app.get("/")
async def root():
    return {"message": "Order Management API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
