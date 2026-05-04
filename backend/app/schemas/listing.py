from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ListingCategory(str, Enum):
    guitars = "guitars"
    bass = "bass"
    keyboards = "keyboards"
    drums = "drums"
    wind = "wind"
    strings = "strings"
    dj = "dj"
    studio = "studio"
    accessories = "accessories"
    other = "other"


class ListingCondition(str, Enum):
    new = "new"
    like_new = "like_new"
    good = "good"
    fair = "fair"
    for_parts = "for_parts"


class ListingStatus(str, Enum):
    active = "active"
    sold = "sold"
    deactivated = "deactivated"


class ListingCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=150)
    description: str = Field(..., min_length=20, max_length=3000)
    price: float = Field(..., gt=0, le=1_000_000)
    category: ListingCategory
    condition: ListingCondition
    brand: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    # Гнучкі характеристики (специфічні для кожної категорії)
    attributes: Optional[Dict[str, Any]] = {}


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=150)
    description: Optional[str] = Field(None, min_length=20, max_length=3000)
    price: Optional[float] = Field(None, gt=0, le=1_000_000)
    category: Optional[ListingCategory] = None
    condition: Optional[ListingCondition] = None
    brand: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    attributes: Optional[Dict[str, Any]] = None
    status: Optional[ListingStatus] = None


class ListingPublic(BaseModel):
    id: str
    title: str
    description: str
    price: float
    category: str
    condition: str
    brand: Optional[str] = None
    city: Optional[str] = None
    attributes: Dict[str, Any] = {}
    images: List[str] = []
    status: str
    seller_id: str
    seller_name: str
    seller_avatar: Optional[str] = None
    views: int = 0
    is_favorited: Optional[bool] = False
    created_at: datetime
    updated_at: datetime


class ListingShort(BaseModel):
    """Коротка версія для списку/каталогу"""
    id: str
    title: str
    price: float
    category: str
    condition: str
    brand: Optional[str] = None
    city: Optional[str] = None
    images: List[str] = []
    status: str
    seller_id: str
    seller_name: str
    is_favorited: Optional[bool] = False
    views: int = 0
    created_at: datetime


class ListingFilter(BaseModel):
    q: Optional[str] = None
    category: Optional[ListingCategory] = None
    condition: Optional[ListingCondition] = None
    brand: Optional[str] = None
    city: Optional[str] = None
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    sort: Optional[str] = "newest"  # newest | price_asc | price_desc | views
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
