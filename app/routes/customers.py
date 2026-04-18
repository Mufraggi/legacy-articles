from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from datetime import datetime

from app.database import db

router = APIRouter(prefix="/customers", tags=["customers"])


class CreateCustomerRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None


@router.post("")
async def create_customer(customer: CreateCustomerRequest):
    customer_data = customer.dict()

    # check email not already taken
    existing = db.customers.find_one({"email": customer_data["email"]})
    if existing:
        raise HTTPException(status_code=400, detail="email already registered")

    customer_data["created_at"] = datetime.utcnow()

    result = db.customers.insert_one(customer_data)
    customer_data["_id"] = str(result.inserted_id)
    customer_data["created_at"] = str(customer_data["created_at"])

    return customer_data


@router.get("/{customer_id}")
async def get_customer(customer_id: str):
    try:
        customer = db.customers.find_one({"_id": ObjectId(customer_id)})
    except:
        raise HTTPException(status_code=400, detail="invalid customer id")

    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")

    customer["_id"] = str(customer["_id"])
    return customer


@router.get("/{customer_id}/orders")
async def get_customer_orders(customer_id: str):
    try:
        customer = db.customers.find_one({"_id": ObjectId(customer_id)})
    except:
        raise HTTPException(status_code=400, detail="invalid customer id")

    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")

    customer["_id"] = str(customer["_id"])

    # get orders - customerId is stored as string in the orders collection
    orders = list(db.orders.find({"customerId": customer_id}))

    for o in orders:
        o["_id"] = str(o["_id"])

    customer["orders"] = orders
    customer["order_count"] = len(orders)

    return customer
