from pydantic import BaseModel, Field
from datetime import datetime

from starvell.types import MessageAuthor


class Response(BaseModel):
    id: str
    """ID Ответа"""
    content: str
    """Текст ответа"""


class Review(BaseModel):
    id: str
    """ID Отзыва"""
    content: str
    """Текст ответа"""
    rating: int
    """Количество звёзд"""
    author_id: int = Field(alias="authorId")
    """ID Автора отзыва"""
    order_id: str = Field(alias="orderId")
    """ID Заказа"""
    is_hidden: bool = Field(alias="isHidden")
    """Скрыт-ли отзыв?"""
    created_at: datetime = Field(alias="createdAt")
    """Дата создания отзыва"""
    updated_at: datetime | None = Field(None, alias="updatedAt")
    """Последняя дата изменения отзыва"""
    author: MessageAuthor
    """Автор отзыва"""
    response: Response | None = Field(None, alias="reviewResponse")
    """Модель ответа на отзыв, None в случае отсутствия ответа"""
