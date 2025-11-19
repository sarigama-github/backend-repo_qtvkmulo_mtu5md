import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import create_document, get_documents, db
from schemas import Order

app = FastAPI(title="VRINDAVAN SOUTH INDIAN API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static menu definition
MENU = [
    {"name": "Plain Dosa", "price": 50, "category": "Dosa"},
    {"name": "Onion Dosa", "price": 60, "category": "Dosa"},
    {"name": "Ghee Dosa", "price": 60, "category": "Dosa"},
    {"name": "Masala Dosa", "price": 70, "category": "Dosa"},
    {"name": "Karam Dosa", "price": 60, "category": "Dosa"},
    {"name": "Ghee Karam Dosa", "price": 70, "category": "Dosa"},
    {"name": "Onion Karam Dosa", "price": 70, "category": "Dosa"},
    {"name": "Setl Dosa", "price": 70, "category": "Dosa"},
    {"name": "Upma Dosa", "price": 70, "category": "Dosa"},
    {"name": "Butter Dosa", "price": 60, "category": "Dosa"},
    {"name": "Mysore Bonda", "price": 50, "category": "Combo"},
    {"name": "Idli + Punugulu + Vada", "price": 50, "category": "Combo"},
    {"name": "Idli + Punugulu + Vada + Bonda", "price": 60, "category": "Combo"},
]

class Health(BaseModel):
    message: str

@app.get("/")
def read_root() -> Health:
    return {"message": "VRINDAVAN SOUTH INDIAN backend is running"}

@app.get("/menu")
def get_menu():
    return {"items": MENU}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

@app.post("/order")
def create_order(order: Order):
    # Basic total validation
    calc_subtotal = sum(item.price * item.quantity for item in order.items)
    if round(calc_subtotal + order.delivery_fee, 2) != round(order.total, 2):
        raise HTTPException(status_code=400, detail="Total does not match order items")

    order_id = create_document("order", order)
    return {"message": "Order placed successfully", "order_id": order_id}

@app.get("/orders")
def list_orders(limit: int = 50):
    docs = get_documents("order", limit=limit)
    # convert ObjectId to string
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])
    return {"orders": docs}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
