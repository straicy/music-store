from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List
from datetime import datetime
from bson import ObjectId
from app.core.database import get_db
from app.core.security import get_current_user, decode_token
from app.schemas.message import MessageCreate
from app.routers.listings import oid

router = APIRouter(prefix="/messages", tags=["messages"])


# ───── WebSocket менеджер з'єднань ─────

class ConnectionManager:
    def __init__(self):
        # {user_id: [WebSocket, ...]}
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(user_id, []).append(ws)

    def disconnect(self, user_id: str, ws: WebSocket):
        if user_id in self.active:
            self.active[user_id].remove(ws)
            if not self.active[user_id]:
                del self.active[user_id]

    async def send_to_user(self, user_id: str, data: dict):
        for ws in self.active.get(user_id, []):
            try:
                await ws.send_json(data)
            except Exception:
                pass

    def is_online(self, user_id: str) -> bool:
        return user_id in self.active and len(self.active[user_id]) > 0


manager = ConnectionManager()


# ───── WebSocket endpoint ─────

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """
    Клієнт підключається з токеном: ws://localhost:8000/api/messages/ws?token=<jwt>
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "access":
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            # Клієнт може відправити ping для підтримки з'єднання
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)


# ───── REST: список розмов ─────

@router.get("/conversations")
async def get_conversations(current_user=Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user["_id"])

    # Агрегація: останнє повідомлення кожної розмови
    pipeline = [
        {"$match": {"$or": [{"sender_id": user_id}, {"receiver_id": user_id}]}},
        {"$sort": {"created_at": -1}},
        {"$group": {
            "_id": "$conversation_id",
            "last_message": {"$first": "$text"},
            "last_message_at": {"$first": "$created_at"},
            "listing_id": {"$first": "$listing_id"},
            "listing_title": {"$first": "$listing_title"},
            "listing_image": {"$first": "$listing_image"},
            "sender_id": {"$first": "$sender_id"},
            "receiver_id": {"$first": "$receiver_id"},
            "sender_name": {"$first": "$sender_name"},
            "receiver_name": {"$first": "$receiver_name"},
            "unread_count": {
                "$sum": {
                    "$cond": [
                        {"$and": [
                            {"$eq": ["$receiver_id", user_id]},
                            {"$eq": ["$is_read", False]}
                        ]},
                        1, 0
                    ]
                }
            }
        }},
        {"$sort": {"last_message_at": -1}},
    ]

    convs = await db.messages.aggregate(pipeline).to_list(length=100)

    result = []
    for c in convs:
        other_id = c["receiver_id"] if c["sender_id"] == user_id else c["sender_id"]
        other_name = c["receiver_name"] if c["sender_id"] == user_id else c["sender_name"]

        result.append({
            "conversation_id": c["_id"],
            "listing_id": c["listing_id"],
            "listing_title": c["listing_title"],
            "listing_image": c.get("listing_image"),
            "other_user_id": other_id,
            "other_user_name": other_name,
            "last_message": c["last_message"],
            "last_message_at": c["last_message_at"],
            "unread_count": c["unread_count"],
            "is_online": manager.is_online(other_id),
        })

    return {"conversations": result, "total": len(result)}


# ───── REST: повідомлення розмови ─────

@router.get("/conversation/{conversation_id}")
async def get_conversation_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    db = get_db()
    user_id = str(current_user["_id"])

    # Перевіряємо що юзер є учасником
    sample = await db.messages.find_one({"conversation_id": conversation_id})
    if not sample:
        raise HTTPException(status_code=404, detail="Розмову не знайдено")

    if user_id not in [sample["sender_id"], sample["receiver_id"]]:
        raise HTTPException(status_code=403, detail="Немає доступу")

    total = await db.messages.count_documents({"conversation_id": conversation_id})
    skip = (page - 1) * limit

    messages = await db.messages.find(
        {"conversation_id": conversation_id}
    ).sort("created_at", 1).skip(skip).limit(limit).to_list(length=limit)

    # Позначаємо як прочитані
    await db.messages.update_many(
        {"conversation_id": conversation_id, "receiver_id": user_id, "is_read": False},
        {"$set": {"is_read": True}}
    )

    return {
        "messages": [
            {
                "id": str(m["_id"]),
                "sender_id": m["sender_id"],
                "sender_name": m["sender_name"],
                "text": m["text"],
                "is_read": m["is_read"],
                "created_at": m["created_at"],
            }
            for m in messages
        ],
        "total": total,
        "page": page,
    }


# ───── REST: надіслати повідомлення ─────

@router.post("/")
async def send_message(data: MessageCreate, current_user=Depends(get_current_user)):
    db = get_db()
    sender_id = str(current_user["_id"])

    if sender_id == data.receiver_id:
        raise HTTPException(status_code=400, detail="Не можна надсилати повідомлення собі")

    # Отримуємо отримувача
    receiver = await db.users.find_one({"_id": ObjectId(data.receiver_id)})
    if not receiver:
        raise HTTPException(status_code=404, detail="Отримувача не знайдено")

    # Отримуємо оголошення
    listing = await db.listings.find_one({"_id": oid(data.listing_id)})
    if not listing:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")

    # ID розмови — унікальний для пари юзерів + оголошення
    participants = sorted([sender_id, data.receiver_id])
    conversation_id = f"{participants[0]}_{participants[1]}_{data.listing_id}"

    msg_doc = {
        "conversation_id": conversation_id,
        "sender_id": sender_id,
        "sender_name": current_user["name"],
        "sender_avatar": current_user.get("avatar"),
        "receiver_id": data.receiver_id,
        "receiver_name": receiver["name"],
        "listing_id": data.listing_id,
        "listing_title": listing["title"],
        "listing_image": listing["images"][0] if listing.get("images") else None,
        "text": data.text,
        "is_read": False,
        "created_at": datetime.utcnow(),
    }

    result = await db.messages.insert_one(msg_doc)
    msg_doc["_id"] = result.inserted_id

    # Надсилаємо через WebSocket якщо отримувач онлайн
    ws_payload = {
        "type": "new_message",
        "conversation_id": conversation_id,
        "message": {
            "id": str(msg_doc["_id"]),
            "sender_id": sender_id,
            "sender_name": current_user["name"],
            "text": data.text,
            "created_at": msg_doc["created_at"].isoformat(),
            "listing_id": data.listing_id,
            "listing_title": listing["title"],
        }
    }
    await manager.send_to_user(data.receiver_id, ws_payload)

    return {
        "id": str(msg_doc["_id"]),
        "conversation_id": conversation_id,
        "message": "Повідомлення надіслано",
    }
