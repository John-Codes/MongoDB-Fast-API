from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
from bson import ObjectId
import uvicorn

# ──────────────────────────────────────
#   CONFIG
# ──────────────────────────────────────

app = FastAPI(title="Generic Store API", description="Store any JSON-like objects", version="1.0")

MONGO_URI = "mongodb+srv://Focus1:Sadman123@cluster0.pis1rb5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

DB_NAME    = "mystore"      # ← feel free to change
COLLECTION = "items"        # ← main collection for all your objects

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION]

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
    limit: int = Query(100, ge=1, le=1000, description="Max items to return"),
    skip: int = Query(0, ge=0)
):
    cursor = collection.find().skip(skip).limit(limit)
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)