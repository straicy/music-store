from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ───── Повідомлення ─────

class MessageCreate(BaseModel):
    receiver_id: str
    listing_id: str
    text: str = Field(..., min_length=1, max_length=1000)


class MessagePublic(BaseModel):
    id: str
    sender_id: str
    sender_name: str
    sender_avatar: Optional[str] = None
    receiver_id: str
    listing_id: str
    listing_title: str
    text: str
    is_read: bool = False
    created_at: datetime


class ConversationSummary(BaseModel):
    """Список розмов у чаті"""
    conversation_id: str  # seller_id + buyer_id + listing_id
    listing_id: str
    listing_title: str
    listing_image: Optional[str] = None
    other_user_id: str
    other_user_name: str
    other_user_avatar: Optional[str] = None
    last_message: str
    last_message_at: datetime
    unread_count: int = 0


# ───── Обране (Favorites) ─────

class FavoriteToggleResponse(BaseModel):
    is_favorited: bool
    message: str


# ───── Загальні відповіді ─────

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    limit: int
    pages: int


class MessageResponse(BaseModel):
    message: str
    success: bool = True
