from pydantic import BaseModel, Field

from starvell.types.order import Descriptions, SubCategory, AttributeValue
from starvell.types import UserTable


class OfferShortCut(BaseModel):
    id: int
    """ID Лота"""
    attributes: list[AttributeValue]
    """Атрибуты лота"""
    price: str
    """Цена лота"""
    descriptions: Descriptions
    """Описания лота"""
    availability: int
    """Количество товаров у лота"""
    auto_delivery: bool = Field(alias="instantDelivery")
    """Включена-ли автоматическая выдача от старвелла?"""
    user: UserTable
    """Продавец"""
    sub_category: SubCategory | None = Field(alias="subCategory")
    """Подкатегория в категории, например 200 робуксов, если в категории нету её выбора, будет None"""

    @property
    def lot_link(self) -> str:
        """
        :return: Ссылка на лот
        :rtype: str
        """

        return f"https://starvell.com/offers/{self.id}"

    @property
    def buyer_link(self) -> str:
        """
        :return: Ссылка на автора лота
        :rtype: str
        """

        return f"https://starvell.com/users/{self.user.id}"
