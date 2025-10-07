from pydantic import BaseModel, Field
from datetime import datetime

from starvell.enums import MessageType
from .review import Review
from .order import Order, BaseOrder
from .user import MessageAuthor
from starvell.utils import format_message_types


class BaseMessage(BaseModel):
    metadata: dict | None
    """Тип сообщения"""
    id: str
    """ID Сообщения"""
    chat_id: str = Field(alias="chatId")
    """ID Чата, откуда было отправлено сообщения"""
    created_at: datetime = Field(alias="createdAt")
    """Дата отправки сообщения"""
    user: MessageAuthor
    """Отправитель/Покупатель/Админ/Ты/Продавец, если быть проще - автор"""

    @property
    def type(self) -> MessageType:
        """
        Возвращает тип сообщения

        :return: Енам MessageType
        :rtype: MessageType
        """

        if not self.metadata or "isAutoResponse" in self.metadata:
            return MessageType.NEW_MESSAGE

        data = self.metadata.get("notificationType")
        return format_message_types(data)


class Message(BaseMessage):
    content: str
    """Текст сообщения"""
    images: list[str]
    """Изображения в сообщении"""

    @property
    def is_auto_reply(self) -> bool:
        """
        :return: Является-ли сообщение автоответом старвелла?
        :rtype: bool
        """

        return "isAutoResponse" in self.metadata if self.metadata else False

    @property
    def by_api(self) -> bool:
        """
        :return: Отправлено-ли сообщение с помощью API?
        :rtype: bool
        """

        return self.content.startswith("‎")

    @property
    def by_admin(self) -> bool:
        """
        :return: Является-ли автор сообщения админом?
        :rtype: bool
        """

        return bool(self.user.roles)


class NewMessageEvent(Message): ...


class OrderEventShort(BaseMessage):
    order: BaseOrder
    """Заказ"""


class OrderEvent(BaseMessage):
    order: Order
    """Заказ"""
    review: Review | None
    """Отзыв"""
