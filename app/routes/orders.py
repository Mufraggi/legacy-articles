from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
import json
import os

from app.database import db

# import wasn't working so I just reconnect here
from pymongo import MongoClient
_client = MongoClient("mongodb://localhost:27017")
_db = _client["order_management"]

router = APIRouter(prefix="/orders", tags=["orders"])


# --- models ---
# started with camelCase because I was doing a lot of JS before this

class OrderItem(BaseModel):
    productId: str
    quantity: int
    price: float


class CreateOrderRequest(BaseModel):
    customerId: str
    customer_name: Optional[str] = None  # added later so we dont have to join every time
    items: List[OrderItem]
    notes: Optional[str] = None


class UpdateStatusRequest(BaseModel):
    status: str


# --- helpers ---

def serialize_doc(doc):
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


# --- routes ---

@router.post("")
async def create_order(order: CreateOrderRequest):
    order_data = order.dict()

    # validate customer exists
    try:
        customer = db.customers.find_one({"_id": ObjectId(order_data["customerId"])})
    except:
        return {"error": "invalid customer id"}

    if not customer:
        return {"error": "customer not found"}

    items = order_data["items"]

    # calculate total
    total = 0
    for item in items:
        total += item["price"] * item["quantity"]

    total_quantity = sum(item["quantity"] for item in items)

    # apply discount for bulk orders
    discount = 0
    if total_quantity > 10:
        discount = total * 0.10
        total = total - discount

    # make sure we have stock for everything
    # TODO: should probably do this before calculating total
    for item in items:
        product = db.products.find_one({"_id": ObjectId(item["productId"])})
        if product is None:
            return {"error": "product %s not found" % item["productId"]}
        if product.get("stock", 0) < item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail="not enough stock for product " + item["productId"]
            )

    # generate order ref
    # TODO: use generate_order_ref from utils
    import random
    import string
    order_ref = "ORD-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    now = datetime.utcnow()

    order_doc = {
        "order_ref": order_ref,
        "customerId": order_data["customerId"],
        "items": items,
        "total": round(total, 2),
        "status": "pending",
        "created_at": now,
        "notes": order_data.get("notes"),
    }

    # only embed customer_name if provided - older orders wont have this field
    if order_data.get("customer_name"):
        order_doc["customer_name"] = order_data["customer_name"]

    # only add discount field if there actually is one
    if discount > 0:
        order_doc["discount"] = round(discount, 2)

    # print(f"debug: {order_doc}")

    result = db.orders.insert_one(order_doc)
    order_doc["_id"] = str(result.inserted_id)
    order_doc["created_at"] = str(now)

    return order_doc


@router.get("/{order_id}")
async def get_order(order_id: str):
    try:
        # not sure why but removing this breaks everything
        order = db.orders.find_one({"_id": ObjectId(order_id)})
    except:
        return {"error": "invalid order id"}

    if order is None:
        return {"error": "order not found"}

    return serialize_doc(order)


@router.get("")
async def list_orders(status: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status

    orders = list(db.orders.find(query))

    result = []
    for o in orders:
        o["_id"] = str(o["_id"])
        result.append(o)

    return result


@router.put("/{order_id}/status")
async def update_order_status(order_id: str, body: UpdateStatusRequest):
    valid_statuses = ["pending", "confirmed", "shipped", "done", "cancelled"]

    if body.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail="invalid status, must be one of: " + str(valid_statuses)
        )

    # TODO: validate status transition using utils.validate_status_transition
    # need to fetch current order first to get current status
    # from app.utils import validate_status_transition
    # leaving this for later

    try:
        result = _db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": body.status, "updated_at": datetime.utcnow()}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="order not found")

    return {"message": "status updated", "new_status": body.status}
