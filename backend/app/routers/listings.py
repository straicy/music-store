from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, status
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
import math
import os
import uuid
from PIL import Image as PILImage
import aiofiles

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.core.config import settings
from app.schemas.listing import (
    ListingCreate, ListingUpdate, ListingPublic,
    ListingShort, ListingCategory, ListingCondition
)

router = APIRouter(prefix="/listings", tags=["listings"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


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


# ───── Каталог / Пошук ─────

@router.get("/")
async def get_listings(
    q: Optional[str] = Query(None, description="Пошук по назві/опису"),
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

    # Обране поточного користувача
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


@router.get("/my", response_model=None)
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

    # Забороняємо перегляд неактивних оголошень (крім власника і адміна)
    if doc["status"] != "active":
        if not current_user:
            raise HTTPException(status_code=404, detail="Оголошення не знайдено")
        user_id = str(current_user["_id"])
        if user_id != doc["seller_id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=404, detail="Оголошення не знайдено")

    # Збільшуємо лічильник переглядів
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


# ───── Створення оголошення ─────

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

    # Оновлюємо лічильник оголошень у юзера
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$inc": {"listings_count": 1}}
    )

    doc["_id"] = result.inserted_id
    return listing_to_public(doc)


# ───── Оновлення оголошення ─────

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


# ───── Видалення оголошення ─────

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
    # Видаляємо з обраного всіх юзерів
    await db.favorites.delete_many({"listing_id": listing_id})


# ───── Завантаження зображень ─────

@router.post("/{listing_id}/images", status_code=status.HTTP_201_CREATED)
async def upload_images(
    listing_id: str,
    files: List[UploadFile] = File(...),
    current_user=Depends(get_current_user),
):
    db = get_db()
    doc = await db.listings.find_one({"_id": oid(listing_id)})

    if not doc:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")

    if str(current_user["_id"]) != doc["seller_id"]:
        raise HTTPException(status_code=403, detail="Немає доступу")

    current_images = doc.get("images", [])
    if len(current_images) + len(files) > 10:
        raise HTTPException(status_code=400, detail="Максимум 10 фото на оголошення")

    upload_dir = os.path.join(settings.UPLOAD_DIR, "listings", listing_id)
    os.makedirs(upload_dir, exist_ok=True)

    saved_paths = []
    for file in files:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail=f"Дозволено лише JPEG, PNG, WebP")

        content = await file.read()
        if len(content) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"Файл перевищує {settings.MAX_IMAGE_SIZE_MB} МБ")

        # Зберігаємо та оптимізуємо
        ext = file.filename.rsplit(".", 1)[-1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(upload_dir, filename)

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        # Оптимізація через Pillow
        try:
            img = PILImage.open(filepath)
            img.thumbnail((1200, 1200))
            img.save(filepath, optimize=True, quality=85)
        except Exception:
            pass

        url_path = f"/uploads/listings/{listing_id}/{filename}"
        saved_paths.append(url_path)

    await db.listings.update_one(
        {"_id": oid(listing_id)},
        {"$push": {"images": {"$each": saved_paths}}}
    )

    return {"images": saved_paths, "message": f"Завантажено {len(saved_paths)} фото"}


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

    image_url = f"/uploads/listings/{listing_id}/{image_name}"
    await db.listings.update_one(
        {"_id": oid(listing_id)},
        {"$pull": {"images": image_url}}
    )

    filepath = os.path.join(settings.UPLOAD_DIR, "listings", listing_id, image_name)
    if os.path.exists(filepath):
        os.remove(filepath)
