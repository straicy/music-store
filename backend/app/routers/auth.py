from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from bson import ObjectId
from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, get_current_user
)
from app.schemas.user import (
    UserRegister, UserLogin, TokenResponse,
    UserPublic, UserUpdate, RefreshRequest
)

router = APIRouter(prefix="/auth", tags=["auth"])


def user_to_public(user: dict) -> UserPublic:
    return UserPublic(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        phone=user.get("phone"),
        bio=user.get("bio"),
        city=user.get("city"),
        role=user["role"],
        avatar=user.get("avatar"),
        created_at=user["created_at"],
        listings_count=user.get("listings_count", 0),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister):
    db = get_db()

    # Перевіряємо унікальність email
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує"
        )

    user_doc = {
        "name": data.name,
        "email": data.email,
        "password_hash": hash_password(data.password),
        "phone": data.phone,
        "bio": None,
        "city": None,
        "avatar": None,
        "role": "user",          # user | admin
        "is_banned": False,
        "listings_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    user_id = str(result.inserted_id)
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_to_public(user_doc),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    db = get_db()

    user = await db.users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email або пароль"
        )

    if user.get("is_banned"):
        raise HTTPException(status_code=403, detail="Акаунт заблоковано")

    user_id = str(user["_id"])
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_to_public(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(data: RefreshRequest):
    payload = decode_token(data.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Потрібен refresh token")

    user_id = payload.get("sub")
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=401, detail="Користувача не знайдено")

    new_access = create_access_token({"sub": user_id})
    new_refresh = create_refresh_token({"sub": user_id})

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        user=user_to_public(user),
    )


@router.get("/me", response_model=UserPublic)
async def get_me(current_user=Depends(get_current_user)):
    return user_to_public(current_user)


@router.put("/me", response_model=UserPublic)
async def update_me(data: UserUpdate, current_user=Depends(get_current_user)):
    db = get_db()

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Немає даних для оновлення")

    update_data["updated_at"] = datetime.utcnow()

    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )

    updated = await db.users.find_one({"_id": current_user["_id"]})
    return user_to_public(updated)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user=Depends(get_current_user)):
    db = get_db()
    user_id = current_user["_id"]

    # Деактивуємо оголошення, але не видаляємо (для цілісності)
    await db.listings.update_many(
        {"seller_id": str(user_id)},
        {"$set": {"status": "deactivated"}}
    )
    await db.users.delete_one({"_id": user_id})
