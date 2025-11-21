import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "amberarctic")

_client: AsyncIOMotorClient = AsyncIOMotorClient(DATABASE_URL)
db: AsyncIOMotorDatabase = _client[DATABASE_NAME]

async def get_collection(name: str):
    return db[name]

async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    col = await get_collection(collection_name)
    now = datetime.utcnow().isoformat()
    doc = {**data, "created_at": now, "updated_at": now}
    result = await col.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc

async def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
    col = await get_collection(collection_name)
    cursor = col.find(filter_dict or {}).limit(limit)
    docs = []
    async for d in cursor:
        d["_id"] = str(d["_id"])  # convert ObjectId
        docs.append(d)
    return docs
