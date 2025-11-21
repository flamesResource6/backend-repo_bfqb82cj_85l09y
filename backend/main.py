from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from database import db, create_document, get_documents
from schemas import Jacket, Review, SizeInput
import os

app = FastAPI(title="Amberarctic API", version="1.0.0")

# CORS for frontend
frontend_url = os.getenv("FRONTEND_URL")
origins = [frontend_url] if frontend_url else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed data on first run (idempotent basic seed)
async def seed_data():
    existing = await get_documents("jacket", {}, limit=1)
    if existing:
        return
    sample = [
        Jacket(
            name="Glacier Pro 3.0",
            slug="glacier-pro-3",
            gender="unisex",
            activity=["travel","city","hike","commute"],
            temperature_min_c=-30,
            temperature_max_c=5,
            battery_life_hours=10,
            warmth_level=9,
            colors=["glacier","onyx","aurora"],
            sizes=["XS","S","M","L","XL","XXL"],
            price=349.0,
            images=[
                "/images/jackets/glacier-pro/1.jpg",
                "/images/jackets/glacier-pro/2.jpg",
                "/images/jackets/glacier-pro/3.jpg"
            ],
            features=["waterproof","windproof","rechargeable","lightweight"]
        ).model_dump(),
        Jacket(
            name="Aurora Lite",
            slug="aurora-lite",
            gender="women",
            activity=["city","travel","commute"],
            temperature_min_c=-10,
            temperature_max_c=10,
            battery_life_hours=12,
            warmth_level=7,
            colors=["frost","rose-ice","onyx"],
            sizes=["XS","S","M","L","XL"],
            price=289.0,
            images=[
                "/images/jackets/aurora-lite/1.jpg",
                "/images/jackets/aurora-lite/2.jpg"
            ],
            features=["water-resistant","windproof","featherweight"]
        ).model_dump(),
        Jacket(
            name="Arctic X",
            slug="arctic-x",
            gender="men",
            activity=["hike","bike","snow"],
            temperature_min_c=-40,
            temperature_max_c=0,
            battery_life_hours=8,
            warmth_level=10,
            colors=["onyx","glacier"],
            sizes=["S","M","L","XL","XXL"],
            price=399.0,
            images=[
                "/images/jackets/arctic-x/1.jpg"
            ],
            features=["waterproof","windproof","impact-resistant"]
        ).model_dump(),
    ]
    for s in sample:
        await create_document("jacket", s)

@app.on_event("startup")
async def on_startup():
    await seed_data()

@app.get("/")
async def root():
    return {"message": "Amberarctic API is running"}

@app.get("/test")
async def test_db():
    try:
        col_names = await db.list_collection_names()
        return {
            "backend": "ok",
            "database": "ok",
            "database_url": os.getenv("DATABASE_URL", "mongodb://localhost:27017"),
            "database_name": os.getenv("DATABASE_NAME", "amberarctic"),
            "connection_status": "connected",
            "collections": col_names,
        }
    except Exception as e:
        return {"backend": "ok", "database": "error", "error": str(e)}

# Query jackets with filters
@app.get("/jackets")
async def list_jackets(
    gender: Optional[str] = Query(None, pattern="^(men|women|unisex)$"),
    activity: Optional[str] = Query(None),
    min_temp: Optional[int] = None,
    max_temp: Optional[int] = None,
):
    filter_dict = {}
    if gender:
        filter_dict["gender"] = gender
    if activity:
        filter_dict["activity"] = {"$in": [activity]}
    if min_temp is not None:
        filter_dict["temperature_min_c"] = {"$lte": min_temp}
    if max_temp is not None:
        filter_dict.setdefault("temperature_max_c", {})["$gte"] = max_temp

    items = await get_documents("jacket", filter_dict, limit=100)
    return {"items": items}

@app.get("/jackets/{slug}")
async def get_jacket(slug: str):
    docs = await get_documents("jacket", {"slug": slug}, limit=1)
    if not docs:
        raise HTTPException(status_code=404, detail="Not found")
    return docs[0]

# Reviews (basic create/list)
@app.get("/reviews/{product_slug}")
async def list_reviews(product_slug: str):
    return {"items": await get_documents("review", {"product_slug": product_slug}, limit=50)}

@app.post("/reviews")
async def create_review(review: Review):
    return await create_document("review", review.model_dump())

# Size recommendation simple algorithm
@app.post("/size/recommend")
async def recommend_size(input: SizeInput):
    # Very simple heuristic demo
    height = input.height_cm
    weight = input.weight_kg
    build = input.build
    base = "M"
    if height < 165 or weight < 55:
        base = "S"
    if height > 180 or weight > 80:
        base = "L"
    if height > 190 or weight > 95:
        base = "XL"

    adjust = {
        "slim": -1,
        "regular": 0,
        "athletic": 0,
        "broad": +1,
    }[build]

    size_order = ["XS","S","M","L","XL","XXL"]
    idx = max(0, min(len(size_order)-1, size_order.index(base) + adjust))
    return {"recommended": size_order[idx]}
