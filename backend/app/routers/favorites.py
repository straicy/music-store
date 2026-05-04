from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.routers.listings import oid, listing_to_short

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("/{listing_id}")
async def toggle_favorite(listing_id: str, current_user=Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user["_id"])

    # Перевіряємо що оголошення існує
    listing = await db.listings.find_one({"_id": oid(listing_id)})
    if not listing:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")

    existing = await db.favorites.find_one({
        "user_id": user_id,
        "listing_id": listing_id,
    })

    if existing:
        await db.favorites.delete_one({"_id": existing["_id"]})
        return {"is_favorited": False, "message": "Видалено з обраного"}
    else:
        await db.favorites.insert_one({
            "user_id": user_id,
            "listing_id": listing_id,
            "created_at": datetime.utcnow(),
        })
        return {"is_favorited": True, "message": "Додано до обраного"}


@router.get("/")
async def get_my_favorites(current_user=Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user["_id"])

    fav_docs = await db.favorites.find({"user_id": user_id}).sort("created_at", -1).to_list(None)
    listing_ids = [oid(f["listing_id"]) for f in fav_docs]

    if not listing_ids:
        return {"items": [], "total": 0}

    listings = await db.listings.find({"_id": {"$in": listing_ids}}).to_list(None)
    favorites_set = {str(lid) for lid in listing_ids}

    return {
        "items": [listing_to_short(l, favorites_set) for l in listings],
        "total": len(listings),
    }
