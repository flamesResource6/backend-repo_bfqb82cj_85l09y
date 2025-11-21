from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# Each model corresponds to a Mongo collection using its lowercase class name

Gender = Literal["men", "women", "unisex"]
Activity = Literal["travel", "city", "hike", "bike", "commute", "snow"]

class Jacket(BaseModel):
    name: str = Field(..., description="Model name")
    slug: str = Field(..., description="URL-safe identifier")
    gender: Gender
    activity: List[Activity] = []
    temperature_min_c: int = Field(..., description="Minimum temperature rating in Celsius")
    temperature_max_c: int = Field(..., description="Maximum comfort temperature in Celsius")
    battery_life_hours: float = Field(..., description="Max battery life at low setting")
    warmth_level: int = Field(..., ge=1, le=10)
    colors: List[str] = ["glacier", "onyx", "frost"]
    sizes: List[str] = ["XS","S","M","L","XL","XXL"]
    price: float
    images: List[str] = []
    features: List[str] = []

class Review(BaseModel):
    product_slug: str
    rating: int = Field(..., ge=1, le=5)
    title: str
    body: str
    author: str

class SizeInput(BaseModel):
    height_cm: int
    weight_kg: int
    build: Literal["slim","regular","athletic","broad"]
    gender: Optional[Gender] = None
