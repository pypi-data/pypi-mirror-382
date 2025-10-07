from pydantic import BaseModel, Field
from datetime import datetime


class BaseMessageAuthor(BaseModel):
    id: int
    """ID Пользователя"""
    username: str
    """Ник пользователя"""

    @property
    def profile_link(self) -> str:
        """
        :return: Ссылка на профиль
        :rtype: str
        """
        return f"https://starvell.com/users/{self.id}"


class MessageAuthor(BaseMessageAuthor):
    roles: list[str] | None = None
    """Роли, могут отсутствовать"""


class BlockListedUser(BaseMessageAuthor):
    avatar_id: str | None = Field(alias="avatar")
    """ID Аватарки пользователя"""
    block_listed_at: datetime = Field(alias="blacklistedAt")
    """Дата добавления в ЧС"""


class UserTable(BaseMessageAuthor):
    avatar_id: str | None = Field(alias="avatar")
    """ID Аватарки пользователя"""
    is_online: bool = Field(alias="isOnline")
    """Онлайн-ли пользователь?"""
    last_online_at: datetime = Field(alias="lastOnlineAt")
    """Дата последнего онлайна пользователя"""
    created_at: datetime = Field(alias="createdAt")
    """Дата создания аккаунта пользователя"""


class UserShortCut(UserTable):
    is_banned: bool = Field(alias="isBanned")
    """Заблокирован-ли пользователь?"""


class User(UserShortCut):
    banner_id: str | None = Field(alias="banner")
    """ID Баннера"""
    description: str | None
    """Описание аккаунта пользователя"""
    is_verified: bool = Field(alias="isKycVerified")
    """Верифицирован-ли пользователь?"""
    roles: list[str]
    """Роли пользователя, если список не пустой, 99% что это админ/саппорт и т.д"""
    rating: int | float
    """Рейтинг аккаунта пользователя"""
    reviews: int = Field(alias="reviewsCount")
    """Количество отзывов у пользователя"""
    email: str | None = Field(None)
    """Почта пользователя, не None только в том случае, если это свой аккаунт"""


class Balance(BaseModel):
    rub: int = Field(alias="rubBalance")
    """Баланс в рублях"""


class ActiveOrders(BaseModel):
    purchases: int = Field(alias="purchaseOrdersCount")
    """Количество покупок"""
    sales: int = Field(alias="salesOrdersCount")
    """Количество продаж"""


class Profile(BaseModel):
    user: User
    """Свой профиль"""
    balance: Balance
    """Баланс"""
    balance_hold: int | None = None
    """Баланс в заморозке"""
    orders: ActiveOrders | None = None
    """Активные продажи"""
    unread_chat_ids: list[str] | None = Field(None, alias="unreadChatIds")
    """Список непрочитанных чатов"""
