from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, status
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
import math
import os
import cloudinary
import cloudinary.uploader

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.core.config import settings
from app.schemas.listing import (
    ListingCreate, ListingUpdate, ListingCategory, ListingCondition
)

router = APIRouter(prefix="/listings", tags=["listings"])

def configure_cloudinary():
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
        api_key=os.getenv("CLOUDINARY_API_KEY", ""),
        api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
        secure=True
    )

def oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Невалідний ID")


def listing_to_short(doc: dict, user_favorites: set = None) -> dict:
    lid = str(doc["_id"])
    return {
        "id": lid,
        "title": doc["title"],
        "price": doc["price"],
        "category": doc["category"],
        "condition": doc["condition"],
        "brand": doc.get("brand"),
        "city": doc.get("city"),
        "images": doc.get("images", []),
        "status": doc["status"],
        "seller_id": doc["seller_id"],
        "seller_name": doc.get("seller_name", ""),
        "is_favorited": lid in (user_favorites or set()),
        "views": doc.get("views", 0),
        "created_at": doc["created_at"],
    }


def listing_to_public(doc: dict, user_favorites: set = None) -> dict:
    lid = str(doc["_id"])
    return {
        **listing_to_short(doc, user_favorites),
        "description": doc["description"],
        "attributes": doc.get("attributes", {}),
        "seller_avatar": doc.get("seller_avatar"),
        "updated_at": doc["updated_at"],
    }


@router.get("/")
async def get_listings(
    q: Optional[str] = Query(None),
    category: Optional[ListingCategory] = None,
    condition: Optional[ListingCondition] = None,
    brand: Optional[str] = None,
    city: Optional[str] = None,
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    sort: str = Query("newest", enum=["newest", "price_asc", "price_desc", "views"]),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user=Depends(get_optional_user),
):
    db = get_db()
    query = {"status": "active"}

    if q:
        query["$text"] = {"$search": q}
    if category:
        query["category"] = category.value
    if condition:
        query["condition"] = condition.value
    if brand:
        query["brand"] = {"$regex": brand, "$options": "i"}
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    if price_min is not None or price_max is not None:
        query["price"] = {}
        if price_min is not None:
            query["price"]["$gte"] = price_min
        if price_max is not None:
            query["price"]["$lte"] = price_max

    sort_map = {
        "newest": [("created_at", -1)],
        "price_asc": [("price", 1)],
        "price_desc": [("price", -1)],
        "views": [("views", -1)],
    }

    total = await db.listings.count_documents(query)
    skip = (page - 1) * limit
    cursor = db.listings.find(query).sort(sort_map[sort]).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)

    favorites = set()
    if current_user:
        fav_docs = await db.favorites.find(
            {"user_id": str(current_user["_id"])}
        ).to_list(length=None)
        favorites = {f["listing_id"] for f in fav_docs}

    return {
        "items": [listing_to_short(d, favorites) for d in docs],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit) if total > 0 else 1,
    }


@router.get("/my")
async def get_my_listings(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user=Depends(get_current_user),
):
    db = get_db()
    query = {"seller_id": str(current_user["_id"])}
    if status_filter:
        query["status"] = status_filter
    docs = await db.listings.find(query).sort("created_at", -1).to_list(length=None)
    return {"items": [listing_to_short(d) for d in docs], "total": len(docs)}


@router.get("/{listing_id}")
async def get_listing(listing_id: str, current_user=Depends(get_optional_user)):
    db = get_db()
    doc = await db.listings.find_one({"_id": oid(listing_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")

    if doc["status"] != "active":
        if not current_user:
            raise HTTPException(status_code=404, detail="Оголошення не знайдено")
        user_id = str(current_user["_id"])
        if user_id != doc["seller_id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=404, detail="Оголошення не знайдено")

    await db.listings.update_one({"_id": oid(listing_id)}, {"$inc": {"views": 1}})
    doc["views"] = doc.get("views", 0) + 1

    favorites = set()
    if current_user:
        fav = await db.favorites.find_one({
            "user_id": str(current_user["_id"]),
            "listing_id": listing_id,
        })
        if fav:
            favorites = {listing_id}

    return listing_to_public(doc, favorites)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_listing(data: ListingCreate, current_user=Depends(get_current_user)):
    db = get_db()
    doc = {
        **data.model_dump(),
        "category": data.category.value,
        "condition": data.condition.value,
        "images": [],
        "status": "active",
        "seller_id": str(current_user["_id"]),
        "seller_name": current_user["name"],
        "seller_avatar": current_user.get("avatar"),
        "views": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.listings.insert_one(doc)
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$inc": {"listings_count": 1}}
    )
    doc["_id"] = result.inserted_id
    return listing_to_public(doc)


@router.put("/{listing_id}")
async def update_listing(
    listing_id: str,
    data: ListingUpdate,
    current_user=Depends(get_current_user),
):
    db = get_db()
    doc = await db.listings.find_one({"_id": oid(listing_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")
    if str(current_user["_id"]) != doc["seller_id"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Немає доступу")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if "category" in update_data:
        update_data["category"] = update_data["category"].value
    if "condition" in update_data:
        update_data["condition"] = update_data["condition"].value
    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    update_data["updated_at"] = datetime.utcnow()

    await db.listings.update_one({"_id": oid(listing_id)}, {"$set": update_data})
    updated = await db.listings.find_one({"_id": oid(listing_id)})
    return listing_to_public(updated)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(listing_id: str, current_user=Depends(get_current_user)):
    db = get_db()
    doc = await db.listings.find_one({"_id": oid(listing_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")
    if str(current_user["_id"]) != doc["seller_id"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Немає доступу")
    await db.listings.delete_one({"_id": oid(listing_id)})
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$inc": {"listings_count": -1}}
    )
    await db.favorites.delete_many({"listing_id": listing_id})


@router.post("/{listing_id}/images", status_code=status.HTTP_201_CREATED)
async def upload_images(
    listing_id: str,
    files: List[UploadFile] = File(...),
    current_user=Depends(get_current_user),
):
    configure_cloudinary()
    db = get_db()
    doc = await db.listings.find_one({"_id": oid(listing_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")
    if str(current_user["_id"]) != doc["seller_id"]:
        raise HTTPException(status_code=403, detail="Немає доступу")

    current_images = doc.get("images", [])
    if len(current_images) + len(files) > 10:
        raise HTTPException(status_code=400, detail="Максимум 10 фото")

    ALLOWED = {"image/jpeg", "image/png", "image/webp"}
    saved_urls = []

    for file in files:
        if file.content_type not in ALLOWED:
            raise HTTPException(status_code=400, detail="Дозволено лише JPEG, PNG, WebP")
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Файл перевищує 5 МБ")

        # Завантажуємо в Cloudinary
        result = cloudinary.uploader.upload(
            content,
            folder=f"music_store/{listing_id}",
            resource_type="image",
            transformation=[{"width": 1200, "height": 900, "crop": "limit", "quality": "auto"}]
        )
        saved_urls.append(result["secure_url"])

    await db.listings.update_one(
        {"_id": oid(listing_id)},
        {"$push": {"images": {"$each": saved_urls}}}
    )
    return {"images": saved_urls, "message": f"Завантажено {len(saved_urls)} фото"}


@router.delete("/{listing_id}/images/{image_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    listing_id: str,
    image_name: str,
    current_user=Depends(get_current_user),
):
    db = get_db()
    doc = await db.listings.find_one({"_id": oid(listing_id)})
    if not doc or str(current_user["_id"]) != doc["seller_id"]:
        raise HTTPException(status_code=403, detail="Немає доступу")

    # Видаляємо URL що містить image_name
    images = doc.get("images", [])
    to_remove = [img for img in images if image_name in img]
    for img_url in to_remove:
        await db.listings.update_one(
            {"_id": oid(listing_id)},
            {"$pull": {"images": img_url}}
        )
