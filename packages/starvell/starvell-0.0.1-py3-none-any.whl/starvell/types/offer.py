from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime

from starvell.types.order import (
    Descriptions,
    DeliveryTime,
    SubCategory,
)


class OfferFields(BaseModel):
    id: int
    """ID Лота"""
    type: str
    """Тип лота"""
    price: str
    """Цена лота"""
    price_type: str = Field(alias="priceType")
    """Тип цены лота"""
    availability: int
    """Количество товара в лоте"""
    descriptions: Descriptions
    """Описания в товаре"""
    delivery_time: DeliveryTime | None = Field(None, alias="deliveryTime")
    """Модель выполнения заказа от и до, в случае если оно есть в лоте, иначе None"""
    attributes: list[Any]
    """Атрибуты лота"""
    message_after_pay: str | None = Field(None, alias="postPaymentMessage")
    """Сообщение после оплаты, None в случае если оно отсутствует"""
    lot_profile_position: int | None = Field(alias="profilePosition")
    """Позиция лота в профиле"""
    is_auto_delivery: bool = Field(alias="instantDelivery")
    """Включена-ли автовыдача в лоте?"""
    goods: list[Any] | None = None
    """Сам не знаю что это"""
    is_active: bool = Field(alias="isActive")
    """Активен-ли лот?"""
    is_hidden: bool = Field(alias="isHidden")
    """Скрыт-ли лот?"""
    is_profile_visible_only: bool = Field(alias="isProfileVisibleOnly")
    """Виден-ли лот только в профиле?"""
    user_id: int = Field(alias="userId")
    """ID Владельца лота"""
    game_id: int = Field(alias="gameId")
    """ID Игры лота"""
    category_id: int = Field(alias="categoryId")
    """ID Категории лота"""
    sub_category_id: int | None = Field(None, alias="subCategoryId")
    """ID Подкатегории лота (по типу 200 робуксов), None в случае если в категории лота нету подкатегорий"""
    created_at: datetime = Field(alias="createdAt")
    """Дата создания лота"""
    updated_at: datetime = Field(alias="updatedAt")
    """Дата последнего изменения лота"""
    basic_attributes: list = Field([], alias="basicAttributes")
    """Базовые атрибуты"""
    numeric_attributes: list[Any] = Field([], alias="numericAttributes")
    """Сам не знаю что это"""
    sub_category: SubCategory | None = Field(None, alias="subCategory")
    """Подкатегория лота (по типу 200 робуксов), None в случае если в категории лота нету подкатегорий"""

    @property
    def lot_link(self) -> str:
        """
        :return: Ссылка на лот
        :rtype: str
        """

        return f"https://starvell.com/offers/{self.id}"


class CreatedOfferFields(BaseModel):
    """
    Не используйте эту модель нигде, апи её само использует при создании лота
    """

    attributes: list[Any] | None = None
    """Атрибуты лота"""
    availability: int
    """Количество товара"""
    basicAttributes: list[Any] | None = None
    """Базовые атрибуты"""
    categoryId: int
    """ID Категории лота"""
    deliveryTime: DeliveryTime | None = None
    """Время доставки"""
    descriptions: Descriptions
    """Описания лота"""
    goods: list
    """Не знаю что это"""
    isActive: bool
    """Активен-ли лот?"""
    numericAttributes: list[Any]
    """Не знаю что это"""
    postPaymentMessage: str | None = None
    """Сообщение после оплаты"""
    price: str
    """Цена лота"""
    subCategoryId: int | None = None
    """ID Подкатегории лота"""
    type: str
    """Тип лота"""
