from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient = None


async def connect_db():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    # Перевіряємо з'єднання
    await client.admin.command("ping")
    print(f"✅ Підключено до MongoDB: {settings.DATABASE_NAME}")


async def close_db():
    global client
    if client:
        client.close()
        print("🔌 З'єднання з MongoDB закрито")


def get_db():
    return client[settings.DATABASE_NAME]
