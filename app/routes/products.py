from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from datetime import datetime

from app.database import db

router = APIRouter(prefix="/products", tags=["products"])


class CreateProductRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: Optional[str] = None
    tags: Optional[List[str]] = None


# using regular def here - read somewhere that sync is fine for mongodb
# and async was causing weird issues with the mongo driver

@router.post("")
def create_product(product: CreateProductRequest):
    try:
        product_data = product.dict()
        product_data["created_at"] = datetime.utcnow()

        # dont store tags if empty list - cleaner
        if not product_data.get("tags"):
            del product_data["tags"]

        result = db.products.insert_one(product_data)
        product_data["_id"] = str(result.inserted_id)
        product_data["created_at"] = str(product_data["created_at"])

        return product_data
    except Exception as e:
        return {"error": str(e)}


@router.get("")
def list_products(category: Optional[str] = None):
    query = {}
    if category:
        query["category"] = category

    products = list(db.products.find(query))

    for p in products:
        p["_id"] = str(p["_id"])

    return products


# added this one later - wasnt in the original spec but needed it
@router.get("/{product_id}")
def get_product(product_id: str):
    product = db.products.find_one({"_id": ObjectId(product_id)})

    if product is None:
        raise HTTPException(status_code=404, detail="product not found")

    product["_id"] = str(product["_id"])
    return product


@router.put("/{product_id}/stock")
def update_stock(product_id: str, quantity: int):
    # this works don't touch it
    result = db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$inc": {"stock": quantity}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="product not found")

    return {"message": "stock updated"}
