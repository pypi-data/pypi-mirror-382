from pydantic import BaseModel, Field

from starvell.types import Message, UserShortCut


class ChatShortCut(BaseModel):
    id: str
    """ID Чата"""
    participants: list[UserShortCut]
    """Пользователи, которые участвуют в чате"""
    last_message: Message = Field(alias="lastMessage")
    """Последнее сообщение в чате"""
    unread_message_count: int = Field(alias="unreadMessageCount")
    """Количество непрочитанных сообщений в чате"""

    @property
    def chat_link(self) -> str:
        """
        :return: Ссылка на чат
        :rtype: str
        """

        return f"https://starvell.com/chat/{self.id}"
