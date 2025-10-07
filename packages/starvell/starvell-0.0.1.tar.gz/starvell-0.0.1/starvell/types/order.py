from pydantic import BaseModel, Field
from starvell.enums import OrderStatuses
from starvell.types import User
from datetime import datetime


class SubCategory(BaseModel):
    name: str
    """Название"""


class Game(SubCategory):
    id: int
    """ID"""
    slug: str
    """Слаг"""


class Category(Game): ...


class TimeRange(BaseModel):
    unit: str
    """Тип времени"""
    value: int | float
    """Значение (например 10)"""


class DeliveryTime(BaseModel):
    from_: TimeRange = Field(alias="from")
    """От"""
    to: TimeRange
    """До"""


class Description(BaseModel):
    full_description: str | None = Field(None, alias="description")
    """Полное описание заказа"""
    short_description: str | None = Field(None, alias="briefDescription")
    """Короткое описание заказа (Заголовок лота)"""


class Descriptions(BaseModel):
    ru: Description | None = Field(None, alias="rus")
    """Описания на русском"""
    en: Description | None = Field(None, alias="eng")
    """Описания на английском"""


class AttributeValue(BaseModel):
    id: str | None = None
    """ID Значения атрибута"""
    name_ru: str | None = Field(None, alias="nameRu")
    """Название значения атрибута на русском, будет None если значение численное/Не тот язык"""
    name_en: str | None = Field(None, alias="nameEn")
    """Название значения атрибута на английском, будет None если значение численное/Не тот язык"""
    numeric_value: int | float | None = Field(None, alias="numericValue")
    """Значения, которые связаны с цифрами (по типу стоимость инвентаря и т.д)"""


class OfferAttributes(BaseModel):
    id: str
    """ID атрибута"""
    value: AttributeValue
    """Значение атрибута"""
    name_ru: str | None = Field(None, alias="nameRu")
    """Название атрибута на русском"""
    name_en: str | None = Field(None, alias="nameEn")
    """Название атрибута на английском"""


class OfferDetails(BaseModel):
    game: Game
    """Игра (Основная категория)"""
    category: Category
    """Категория игры"""
    attributes: list[OfferAttributes] | None
    """Атрибуты лота"""
    subcategory: SubCategory | None = Field(alias="subCategory")
    """Подкатегория категории"""
    delivery_time: DeliveryTime | None = Field(alias="deliveryTime")
    """Время доставки"""
    descriptions: Descriptions
    """Описания лота"""
    images: list
    """Изображения лота"""
    availability: int | float
    """Количество доступного товара"""
    auto_delivery: bool = Field(alias="instantDelivery")
    """Авто-выдача от старвелла?"""

    @property
    def game_fullname(self) -> str:
        """
        :return: Полное название игры + категории, в формате игра, категория
        :rtype: str
        """

        return f"{self.game.name}, {self.category.name}"

    @property
    def game_link(self) -> str:
        """
        :return: Ссылка на категорию лота
        :rtype: str
        """

        return f"https://starvell.com/{self.game.slug}/{self.category.slug}"

    @property
    def attributes_dict(self) -> dict[str, str]:
        """
        :return: Словарь с атрибутами лота, в формате атрибут: значение атрибута
        :rtype: dict[str, str]
        """

        data = {}

        for value in self.attributes:
            data.setdefault(
                value.name_ru if value.name_ru else value.name_en,
                value.value.name_ru
                if value.value.name_ru
                else value.value.name_en
                if value.value.name_en
                else value.value.numeric_value,
            )

        return data


class OrderArgs(BaseModel):
    id: str
    """ID Аргумента"""
    value: str | None
    """Значение аргумента"""
    name_ru: str | None = Field(None, alias="nameRu")
    """Название аргуминета на русском"""
    name_en: str | None = Field(None, alias="nameEn")
    """Название аргумента на английском"""


class BaseOrder(BaseModel):
    id: str
    """ID Заказа"""
    quantity: int
    """Количество товара"""
    order_args: list[OrderArgs] = Field(alias="orderArgs")
    """Аргументы к заказу"""
    offer_details: OfferDetails = Field(alias="offerDetails")
    """Лот"""

    @property
    def order_args_dict(self) -> dict[str, str]:
        """
        :return: Словарь с аргументами заказа в формате аргумент: значение аргумента
        :rtype: dict[str, str]
        """
        return {
            value.name_ru if value.name_ru else value.name_en: value.value
            for value in self.order_args
        }

    @property
    def short_order_id(self) -> str:
        """
        :return: Короткий ID Заказа, ровно тот, что и отображается на сайте
        :rtype: str
        """

        return f"{self.id[-8:].upper()}"

    @property
    def order_link(self) -> str:
        """
        :return: Ссылка на заказ
        :rtype: str
        """

        return f"https://starvell.com/order/{self.id}"


class OrderShortCut(BaseOrder):
    status: OrderStatuses
    """Статус заказа"""
    price_for_me: float = Field(alias="basePrice")
    """Прайс для меня (Без комиссии покупателя)"""
    price_for_buyer: float = Field(alias="totalPrice")
    """Прайс для покупателя (С комиссией покупателя)"""
    review_visible_after_refund: bool = Field(alias="reviewVisibleAfterRefund")
    """Виден-ли отзыв после возврата?"""
    created_at: datetime = Field(alias="createdAt")
    """Дата создания"""
    updated_at: datetime = Field(alias="updatedAt")
    """Дата последнего изменения статуса заказа"""

    @property
    def status_translate(self) -> str:
        """
        :return: ППолучает переведённый статус заказа, тот что и на сайте
        :rtype: str
        """

        return {
            OrderStatuses.PAID: "Создан",
            OrderStatuses.CLOSED: "Завершен",
            OrderStatuses.REFUNDED: "Возврат",
            OrderStatuses.UNKNOWN: "Неизвестный",
        }.get(self.status)


class Order(OrderShortCut):
    offer_id: int | None = Field(alias="offerId")
    """ID Оплаченного лота"""

    @property
    def lot_link(self) -> str:
        return f"https://starvell.com/offers/{self.offer_id}"


class OrderFull(Order):
    user: User
    """Покупатель"""
