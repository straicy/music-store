from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import connect_db, close_db, get_db
from app.routers import auth, listings, favorites, messages, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    await create_indexes()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print(f"🚀 {settings.APP_NAME} запущено")
    yield
    # Shutdown
    await close_db()


async def create_indexes():
    """Створюємо індекси MongoDB для швидкого пошуку"""
    db = get_db()

    # Текстовий пошук по оголошеннях
    await db.listings.create_index([
        ("title", "text"),
        ("description", "text"),
        ("brand", "text"),
    ])
    await db.listings.create_index([("status", 1), ("created_at", -1)])
    await db.listings.create_index([("seller_id", 1)])
    await db.listings.create_index([("category", 1), ("status", 1)])

    # Користувачі
    await db.users.create_index([("email", 1)], unique=True)

    # Повідомлення
    await db.messages.create_index([("conversation_id", 1), ("created_at", 1)])
    await db.messages.create_index([("receiver_id", 1), ("is_read", 1)])

    # Обране
    await db.favorites.create_index(
        [("user_id", 1), ("listing_id", 1)],
        unique=True
    )

    print("📑 Індекси MongoDB створено")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="REST API для маркетплейсу музичних інструментів",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS — дозволяємо фронтенду (Vue.js dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статичні файли (завантажені зображення)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Роутери
app.include_router(auth.router, prefix="/api")
app.include_router(listings.router, prefix="/api")
app.include_router(favorites.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
