from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
from bson import ObjectId
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ──────────────────────────────────────
#   CONFIG
# ──────────────────────────────────────

app = FastAPI(title="Generic Store API", description="Store any JSON-like objects", version="1.0")

MONGO_URI = os.getenv("MONGO_URI")

DB_NAME    = os.getenv("DB_NAME", "mystore")      # ← feel free to change
COLLECTION = os.getenv("COLLECTION", "items")      # ← main collection for all your objects

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION]


# ── CORS ──────────────────────────────────────────────────────────────────────
# Flutter web runs in the browser — requests to localhost:8000 are blocked
# without these headers. ENV=dev uses wildcard; ENV=prod uses explicit origins.
#
# .env:
#   ENV=dev
#   CORS_ALLOWED_ORIGINS=https://your-prod-domain.com   (prod only)
 
ENV = os.getenv("ENV", "dev")
 
if ENV == "dev":
    cors_origins = ["*"]
else:
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "")
    cors_origins = [o.strip() for o in raw.split(",") if o.strip()]
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=ENV != "dev",
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ──────────────────────────────────────
#   MODEL – very loose / flexible
# ──────────────────────────────────────

class StoreItem(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  # becomes str(ObjectId)
    # No other fixed fields — accept anything
    # You can still add optional known ones later if you want

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        extra = "allow"          # ← crucial: allow unknown fields!

# Helper: mongo doc → pydantic (keeps all fields)
def to_item(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc  # return as dict so all original fields are preserved

# ──────────────────────────────────────
#   HEALTH CHECK
# ──────────────────────────────────────

@app.get("/health", status_code=200)
@app.get("/ping", status_code=200)
async def health_check():
    try:
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected", "message": "MongoDB Atlas ready 🚀"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB error: {str(e)}")

# ──────────────────────────────────────
#   CRUD – generic for any JSON object
# ──────────────────────────────────────

@app.post("/items", status_code=201)
async def create_item(item: Dict[str, Any]):
    # Accept raw dict — no strict model enforcement
    result = await collection.insert_one(item)
    created = await collection.find_one({"_id": result.inserted_id})
    return to_item(created)


@app.get("/items", response_model=List[Dict[str, Any]])
async def list_items(
    limit: int = Query(100, ge=1, le=5000, description="Max items to return"),
    skip: int = Query(0, ge=0),
    record_type: Optional[str] = Query(
        None,
        description=(
            "Filter by record_type field (exact match). "
            "Examples: 'route', 'location_history', 'live_location'."
        ),
    ),
    driver_id: Optional[str] = Query(None, description="Filter by driver_id field (exact match)."),
    sort: Optional[str] = Query(
        None,
        description=(
            "Sort field. Prefix with '-' for descending. "
            "Examples: 'sort=-_id' (newest first), 'sort=assigned_date'."
        ),
    ),
):
    mongo_filter: Dict[str, Any] = {}

    # ── record_type filter ────────────────────────────────────────────────────
    if record_type is not None:
        mongo_filter["record_type"] = record_type

    # ── driver_id filter ──────────────────────────────────────────────────────
    if driver_id is not None:
        mongo_filter["driver_id"] = driver_id

    # ── sort ──────────────────────────────────────────────────────────────────
    sort_list = None
    if sort is not None:
        from pymongo import ASCENDING, DESCENDING
        field = sort.lstrip("-")
        direction = DESCENDING if sort.startswith("-") else ASCENDING
        # Map "id" / "_id" both to the real MongoDB _id field
        if field in ("id", "_id"):
            field = "_id"
        sort_list = [(field, direction)]

    cursor = collection.find(mongo_filter).skip(skip).limit(limit)
    if sort_list:
        cursor = cursor.sort(sort_list)

    docs = await cursor.to_list(length=limit)
    return [to_item(d) for d in docs if d is not None]


@app.get("/items/{id}")
async def get_item(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid ID format")

    doc = await collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(404, "Item not found")

    return to_item(doc)


@app.put("/items/{id}")
async def update_item(id: str, item: Dict[str, Any]):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid ID format")

    # Remove id from update payload if present
    item.pop("id", None)
    item.pop("_id", None)

    if not item:
        raise HTTPException(400, "No fields to update")

    updated = await collection.find_one_and_update(
        {"_id": obj_id},
        {"$set": item},
        return_document=True
    )

    if not updated:
        raise HTTPException(404, "Item not found")

    return to_item(updated)


@app.delete("/items/{id}", status_code=204)
async def delete_item(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid ID format")

    result = await collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Item not found")

    return None


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)