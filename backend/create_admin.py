"""
Запуск: python create_admin.py
Створює першого адміністратора в БД.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "music_store")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    email = input("Email адміністратора: ").strip()
    name = input("Ім'я адміністратора: ").strip()
    password = input("Пароль (мін. 8 символів): ").strip()

    if len(password) < 8:
        print("❌ Пароль занадто короткий!")
        return

    existing = await db.users.find_one({"email": email})
    if existing:
        print(f"❌ Користувач з email {email} вже існує!")
        client.close()
        return

    admin_doc = {
        "name": name,
        "email": email,
        "password_hash": pwd_context.hash(password),
        "phone": None,
        "bio": None,
        "city": None,
        "avatar": None,
        "role": "admin",
        "is_banned": False,
        "listings_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(admin_doc)
    print(f"✅ Адміністратора створено! ID: {result.inserted_id}")
    client.close()


if __name__ == "__main__":
    asyncio.run(create_admin())
