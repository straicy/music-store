from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from bson import ObjectId
from app.core.database import get_db
from app.core.security import get_current_admin
from app.routers.listings import oid

router = APIRouter(prefix="/admin", tags=["admin"])


# ───── Користувачі ─────

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    q: str = Query(None),
    _=Depends(get_current_admin),
):
    db = get_db()
    query = {}
    if q:
        query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"email": {"$regex": q, "$options": "i"}},
        ]

    total = await db.users.count_documents(query)
    skip = (page - 1) * limit
    users = await db.users.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    return {
        "items": [
            {
                "id": str(u["_id"]),
                "name": u["name"],
                "email": u["email"],
                "role": u["role"],
                "is_banned": u.get("is_banned", False),
                "listings_count": u.get("listings_count", 0),
                "created_at": u["created_at"],
            }
            for u in users
        ],
        "total": total,
        "page": page,
    }


@router.patch("/users/{user_id}/ban")
async def toggle_ban(user_id: str, _=Depends(get_current_admin)):
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    if user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Не можна заблокувати адміністратора")

    new_status = not user.get("is_banned", False)
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_banned": new_status, "updated_at": datetime.utcnow()}}
    )

    action = "заблоковано" if new_status else "розблоковано"
    return {"message": f"Користувача {action}", "is_banned": new_status}


@router.patch("/users/{user_id}/role")
async def change_role(user_id: str, role: str, _=Depends(get_current_admin)):
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Роль може бути 'user' або 'admin'")

    db = get_db()
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": role, "updated_at": datetime.utcnow()}}
    )
    return {"message": f"Роль змінено на '{role}'"}


# ───── Оголошення ─────

@router.get("/listings")
async def list_all_listings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    _=Depends(get_current_admin),
):
    db = get_db()
    query = {}
    if status:
        query["status"] = status

    total = await db.listings.count_documents(query)
    skip = (page - 1) * limit
    listings = await db.listings.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    return {
        "items": [
            {
                "id": str(l["_id"]),
                "title": l["title"],
                "price": l["price"],
                "category": l["category"],
                "status": l["status"],
                "seller_name": l.get("seller_name"),
                "views": l.get("views", 0),
                "created_at": l["created_at"],
            }
            for l in listings
        ],
        "total": total,
        "page": page,
    }


@router.patch("/listings/{listing_id}/status")
async def set_listing_status(listing_id: str, status: str, _=Depends(get_current_admin)):
    allowed = ["active", "deactivated", "sold"]
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Статус має бути одним з: {allowed}")

    db = get_db()
    result = await db.listings.update_one(
        {"_id": oid(listing_id)},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")

    return {"message": f"Статус оголошення змінено на '{status}'"}


@router.delete("/listings/{listing_id}")
async def admin_delete_listing(listing_id: str, _=Depends(get_current_admin)):
    db = get_db()
    result = await db.listings.delete_one({"_id": oid(listing_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")
    await db.favorites.delete_many({"listing_id": listing_id})
    return {"message": "Оголошення видалено"}


# ───── Статистика дашборду ─────

@router.get("/stats")
async def get_stats(_=Depends(get_current_admin)):
    db = get_db()
    users_total = await db.users.count_documents({})
    users_banned = await db.users.count_documents({"is_banned": True})
    listings_active = await db.listings.count_documents({"status": "active"})
    listings_total = await db.listings.count_documents({})
    messages_total = await db.messages.count_documents({})

    return {
        "users": {"total": users_total, "banned": users_banned},
        "listings": {"total": listings_total, "active": listings_active},
        "messages": {"total": messages_total},
    }
