import json
import re
import time
from datetime import datetime
from typing import Any

from uuid import UUID

from starvell.session import StarvellSession

from .enums import PaymentTypes
from .errors import (
    BlockError,
    CreateLotError,
    DeleteLotError,
    EditReviewError,
    GetReviewError,
    ReadChatError,
    RefundError,
    RequestFailedError,
    ReviewNotFoundError,
    SaveSettingsError,
    SendImageError,
    SendMessageError,
    SendReviewError,
    SendTypingError,
    UnBlockError,
    UserNotFoundError,
    WithdrawError,
)
from .types import (
    BlockListedUser,
    ChatShortCut,
    CreatedOfferFields,
    ExchangeRate,
    OfferFields,
    Message,
    Profile,
    OfferShortCut,
    Order,
    OrderFull,
    Review,
    User,
)
from .propertys import MyProfileProperty
from .utils import (
    format_order_status,
    format_payment_methods,
    set_user,
)


class Client:
    def __init__(
        self, session_id: str, proxy: dict[str, str] | None = None
    ) -> None:
        """
        :param session_id: ID Сессии на Starvell (в куки)
        :type session_id: str
        :param proxy: Прокси с которого будут осуществляться запросы (пример: {"http": "http://user:password@your_proxy_ip:port"})
        :type proxy: dict
        """

        # информация об аккаунте
        self.__username: str | None = None
        self.__id: int | None = None
        self.session_id: str = session_id
        self.__email: str | None = None
        self.__created_date: datetime | None = None
        self.__avatar_id: str | None = None
        self.__banner_id: str | None = None
        self.__description: str | None = None
        self.__is_verified: bool | None = None
        self.__rating: int | float | None = None
        self.__reviews_count: int | None = None
        self.__balance_hold: float | None = None
        self.__balance: float | None = None
        self.__active_orders: int | None = None

        # прочее
        self.proxy: dict[str, str] | None = proxy
        self.request: StarvellSession = StarvellSession(session_id, self.proxy)

        # авто запуск
        self.get_info()

    def get_info(self) -> Profile:
        """
        Получает информацию об аккаунте.

        :return: Модель
        :rtype: Profile
        """

        url = "https://starvell.com/api/users-profile"
        response = Profile.model_validate(
            self.request.get(url=url, raise_not_200=True).json()
        )

        self.__username = response.user.username
        self.__id = response.user.id
        self.__email = response.user.email
        self.__created_date = response.user.created_at
        self.__avatar_id = response.user.avatar_id
        self.__banner_id = response.user.banner_id
        self.__description = response.user.description
        self.__is_verified = response.user.is_verified
        self.__rating = response.user.rating
        self.__reviews_count = response.user.reviews
        self.__balance_hold = (
            response.balance_hold / 100 if response.balance_hold else 0
        )
        self.__balance = (
            response.balance.rub / 100
            if isinstance(response.balance.rub, int)
            else None
        )
        self.__active_orders = response.orders.sales if response.orders else 0

        return response

    def get_sales(
        self,
        offset: int = 0,
        limit: int = 100000000,
        filter_sales: dict[str, Any] | None = None,
    ) -> list[OrderFull]:
        """
        Получает продажи аккаунта.

        :param offset: С какой продажи начинать?
        :type offset: int
        :param limit: Сколько продаж получить?
        :type limit: int
        :param filter_sales: Дополнительные фильтры, которые можно передать в тело запроса
        :type filter_sales: dict
        :return: Список, объектами которого являются модели OrderFull
        :rtype: list[OrderFull]
        """

        default: dict[str, str] = {"userType": "seller"}

        url = "https://starvell.com/api/orders/list"
        body = {
            "filter": default if filter_sales is None else filter_sales,
            "with": {"buyer": True},
            "orderBy": {"field": "createdAt", "order": "DESC"},
            "limit": limit,
            "offset": offset,
        }
        response = self.request.post(url, body, raise_not_200=True)

        list_with_sales = []
        orders = response.json()

        for obj in orders:
            obj["status"] = format_order_status(obj["status"])
            ord_2 = OrderFull.model_validate(obj)
            list_with_sales.append(ord_2)

        return list_with_sales

    def get_reviews(
        self, offset: int = 0, limit: int = 100000000
    ) -> list[Review]:
        """
        Получает отзывы аккаунта.

        :param offset: С какого отзыва начинать?
        :type offset: int
        :param limit: Сколько отзывов получить?
        :type limit: int
        :return: Список, объектами которого являются модели Review
        :rtype: list[Review]
        """

        url = "https://starvell.com/api/reviews/list"
        body = {
            "filter": {"recipientId": self.__id},
            "pagination": {"offset": offset, "limit": limit},
        }
        response = self.request.post(url, body, raise_not_200=True).json()

        return [Review.model_validate(i) for i in response]

    def get_chats(self, offset: int, limit: int) -> list[ChatShortCut]:
        """
        Получает чаты аккаунта.

        :param offset: С какого чата начинать?
        :type offset: int
        :param limit: Сколько чатов получить?
        :type limit: int
        :return: Список, объектами которого являются модели ChatShortCut
        :rtype: list[ChatShortCut]
        """

        url = "https://starvell.com/api/chats/list"
        body = {"offset": offset, "limit": limit}
        response = self.request.post(url, body=body, raise_not_200=True).json()

        return [ChatShortCut.model_validate(i) for i in response]

    def get_chat(self, chat_id: str | UUID, limit: int) -> list[Message]:
        """
        Получает историю сообщений чата.

        :param chat_id: ID Чата
        :type chat_id: str | UUID
        :param limit: Сколько сообщений получить?
        :type limit: int
        :return: Список, объектами которого являются модели Message
        :rtype: list[Message]
        """

        url = "https://starvell.com/api/messages/list"
        body = {"chatId": str(chat_id), "limit": limit}
        messages = []

        response = self.request.post(url, body, raise_not_200=True).json()

        for msg in response:
            msg["user"] = set_user(msg)
            messages.append(Message.model_validate(msg, by_alias=True))

        return messages

    def get_order(self, order_id: str | UUID) -> Order:
        """
        Получает заказ.

        :param order_id: ID Заказа
        :type order_id: str | UUID
        :return: Модель
        :rtype: Order
        """

        order_id = str(order_id)
        url = f"https://starvell.com/api/orders/{order_id}"
        body = {"orderId": order_id}

        response = self.request.get(url, body, raise_not_200=True).json()
        response["status"] = format_order_status(response["status"])
        response["basePrice"] = (
            response["basePrice"] / 100
            if isinstance(response["basePrice"], int)
            else 0
        )
        response["totalPrice"] = (
            response["totalPrice"] / 100
            if isinstance(response["totalPrice"], int)
            else 0
        )

        return Order.model_validate(response)

    def get_review(self, order_id: str | UUID) -> Review:
        """
        Получает отзыв с помощью ID заказа.

        :param order_id: ID Заказа
        :type order_id: str | UUID
        :return: Модель Review
        :rtype: Review
        """

        order_id = str(order_id)
        url = "https://starvell.com/api/reviews/by-order-id"
        param = {"id": str(order_id)}

        response = self.request.get(url=url, params=param, raise_not_200=False)

        if response.status_code == 404:
            raise ReviewNotFoundError(response.json().get("message"))

        if response.status_code != 200:
            raise GetReviewError(response.json().get("message"))

        return Review.model_validate(response.json())

    def get_category_lots(
        self,
        category_id: int,
        offset: int = 0,
        limit: int = 100000000,
        only_online: bool = False,
        other_filters: dict[str, str] | None = None,
    ) -> list[OfferShortCut]:
        """
        Получает лоты категории.

        :param category_id: ID Категории
        :type category_id: int
        :param offset: С какого лота начинать?
        :type offset: int
        :param limit: Сколько лотов получить?
        :type limit: int
        :param only_online: Исключить офлайн продавцов?
        :type only_online: True
        :param other_filters: Дополнительные фильтры, которые можно передать в тело запроса
        :type other_filters: dict
        :return: Список, объектами которого являются модели OfferShortCut
        :rtype: list[OfferShortCut]
        """

        url = "https://starvell.com/api/offers/list-by-category"
        body = {
            "categoryId": category_id,
            "onlyOnlineUsers": only_online,
            "attributes": [],
            "numericRangeFilters": [],
            "limit": limit,
            "offset": offset,
            "sortBy": "price",
            "sortDir": "ASC",
            "sortByPriceAndBumped": True,
        }

        if other_filters:
            body.update(**other_filters)

        response = self.request.post(url, body, raise_not_200=True).json()

        return [OfferShortCut.model_validate(i) for i in response]

    def get_my_category_lots(
        self, category_id: int, offset: int = 0, limit: int = 10000000
    ) -> list[OfferFields]:
        """
        Получает свои лоты в категории.

        :param category_id: ID Категории
        :type category_id: int
        :param offset: С какого лота начинать?
        :type offset: int
        :param limit: Сколько лотов получить?
        :type limit: int
        :return: Список, объектами которого являются модели OfferFields
        :rtype: list[OfferFields]
        """

        url = "https://starvell.com/api/offers/list-my"
        body = {"categoryId": category_id, "limit": limit, "offset": offset}

        response = self.request.post(url, body=body, raise_not_200=True).json()

        return [OfferFields.model_validate(i) for i in response]

    def get_lot_fields(self, lot_id: int | str) -> OfferFields:
        """
        Получает поля своего лота.

        :param lot_id: ID Лота
        :type lot_id: int | str
        :return: Модель OfferFields
        :rtype: OfferFields
        """

        url = f"https://starvell.com/api/offers/{lot_id}"
        response = self.request.get(url, raise_not_200=True).json()

        return OfferFields.model_validate(response)

    def get_black_list(self) -> list[BlockListedUser]:
        """
        Получает список пользователей, в чёрном списке аккаунта.

        :return: Список, объектами которого являются модели BlockListedUser
        :rtype: list[BlockListedUser]
        """

        url = "https://starvell.com/api/blacklisted-users/list"
        response = self.request.post(url).json()

        return [BlockListedUser.model_validate(i) for i in response]

    def get_user(self, user_id: str | int) -> User:
        """
        Получает информацию об пользователе.

        :param user_id: ID Пользователя
        :type user_id: int | str
        :return: Модель User
        :rtype: User
        """

        url = f"https://starvell.com/api/users/{user_id}"
        response = self.request.get(url=url, raise_not_200=False)

        if response.status_code == 404:
            raise UserNotFoundError(response.json().get("message"))
        elif response.status_code != 200:
            raise RequestFailedError(response)

        return User.model_validate(response.json())

    def get_usdt_rub_exchange_rate(self) -> ExchangeRate:
        """
        Получает курс USDT к RUB на Starvell.

        :return: Модель ExchangeRate
        :rtype: ExchangeRate
        """

        return ExchangeRate.model_validate(
            self.request.get(
                url="https://starvell.com/api/exchange-rates/usdt-rub"
            ).json()
        )

    def get_usdt_ltc_exchange_rate(self) -> ExchangeRate:
        """
        Получает курс USDT к LTC на Starvell.

        :return: Модель ExchangeRate
        :rtype: ExchangeRate
        """

        return ExchangeRate.model_validate(
            self.request.get(
                url="https://starvell.com/api/exchange-rates/usdt-ltc"
            ).json()
        )

    def create_lot(self, fields: OfferFields) -> OfferFields:
        """
        Создаёт лот на Starvell.

        :param fields: Поля лота
        :type fields: OfferFields
        :return: Поля (OfferFields модель) созданного лота
        :rtype: OfferFields
        :raise CreateLotError: В случае возникновения ошибки
        """

        url = "https://starvell.com/api/offers-operations/create"

        lot_fields = json.loads(fields.model_dump_json(by_alias=True))
        lot_fields["numericAttributes"] = lot_fields["attributes"]
        create_fields = json.loads(
            CreatedOfferFields.model_validate(lot_fields).model_dump_json(
                by_alias=True
            )
        )

        response = self.request.post(url, create_fields, raise_not_200=False)

        if response.status_code != 201:
            raise CreateLotError(response.json().get("message"))

        return OfferFields.model_validate(response.json())

    def delete_lot(self, lot_id: int | str) -> None:
        """
        Удаляет лот со Starvell.

        :param lot_id: ID Лота
        :type lot_id: int | str
        :return: None
        :rtype: None
        :raise DeleteLotError: В случае возникновения ошибки
        """

        url = f"https://starvell.com/api/offers/{lot_id}/delete"
        response = self.request.post(url, raise_not_200=False)
        js = response.json()

        if response.status_code != 200:
            raise DeleteLotError(js.get("message"))

    def send_message(
        self, chat_id: str | UUID, content: Any, read_chat: bool = True
    ) -> None:
        """
        Отправляет сообщение в чат Starvell.

        :param chat_id: ID Чата
        :type chat_id: str | UUID
        :param content: Текст сообщения
        :type content: Any
        :param read_chat: Прочитывать-ли чат, после отправки сообщения?
        :type read_chat: bool
        :return: None
        :rtype: None
        :raise SendMessageError: В случае возникновения ошибки
        """

        url = "https://starvell.com/api/messages/send"
        body = {
            "chatId": str(chat_id),
            "content": f"‎{str(content)}",
        }
        response = self.request.post(url, body, raise_not_200=False)

        if response.status_code != 201:
            raise SendMessageError(response.json().get("message"))

        if read_chat:
            self.read_chat(chat_id)

    def send_image(
        self, chat_id: str | UUID, image_bytes: bytes, read_chat: bool = True
    ) -> None:
        """
        Отправляет изображение в чат Starvell.

        :param chat_id: ID Чата
        :type chat_id: str | UUID
        :param image_bytes: Байты изображения
        :type image_bytes: bytes
        :param read_chat: Прочитывать-ли чат, после отправки сообщения?
        :type read_chat: bool
        :return: None
        :rtype: None
        :raise SendImageError: В случае возникновения ошибки
        """

        url = "https://starvell.com/api/messages/send-with-image"
        param = {"chatId": str(chat_id)}
        files = {"image": ("starvell.png", image_bytes, "image/png")}

        response = self.request.post(
            url=url, files=files, params=param, raise_not_200=False
        )

        if response.status_code != 201:
            raise SendImageError(response.json().get("message"))

        if read_chat:
            self.read_chat(chat_id)

    def read_chat(self, chat_id: str | UUID) -> None:
        """
        Отмечает чат прочитанным.

        :param chat_id: ID Чата
        :type chat_id: str | UUID
        :return: None
        :rtype: None
        :raise ReadChatError: В случае возникновения ошибки
        """

        url = "https://starvell.com/api/chats/read"
        body = {"chatId": str(chat_id)}

        response = self.request.post(url, body, raise_not_200=False)

        if response.status_code != 200:
            raise ReadChatError(response.json().get("message"))

    def save_lot(self, lot: OfferFields) -> None:
        """
        Сохраняет лот, с переданными полями.

        :param lot: Поля лота (Модель OfferFields)
        :type lot: OfferFields
        :return: None
        :rtype: None
        """

        url = f"https://starvell.com/api/offers-operations/{lot.id}/update"
        data = lot.model_dump(by_alias=True)

        if "subCategory" in data:
            data.pop("subCategory")

        for key, value in data.items():
            if type(value) is datetime:
                data[key] = value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        self.request.post(url, data, raise_not_200=False)

    def send_review(self, review_id: str | UUID, content: Any) -> None:
        """
        Отправляет ответ на отзыв только в том случае, если на отзыв ещё нет ответа.

        :param review_id: ID Отзыва
        :type review_id: str | UUID
        :param content: Текст ответа
        :type content: Any
        :return: None
        :rtype: None
        :raise SendReviewError: В случае возникновения ошибки
        """

        url = "https://starvell.com/api/review-responses/create"
        body = {"content": str(content), "reviewId": str(review_id)}
        response = self.request.post(url, body, raise_not_200=False)

        if response.status_code != 200:
            raise SendReviewError(response.json().get("message"))

    def edit_review(self, review_id: str | UUID, content: Any) -> None:
        """
        Редактирует существующий ответ на отзыв.

        :param review_id: ID Отзыва
        :type review_id: str | uuid
        :param content: Текст ответа
        :type content: Any
        :return: None
        :rtype: None
        :raise EditReviewError: В случае возникновения ошибки
        """

        url = f"https://starvell.com/api/review-responses/{review_id}/update"
        body = {"content": content, "reviewId": str(review_id)}
        response = self.request.post(url, body, raise_not_200=False)

        if response.status_code != 200:
            raise EditReviewError(response.json().get("message"))

    def refund(self, order_id: str | UUID) -> None:
        """
        Оформляет возврат средств в заказе.

        :param order_id: ID Заказа
        :type order_id: str | UUID
        :return: None
        :rtype: None
        :raise RefundError: В случае возникновения ошибки
        """

        url = "https://starvell.com/api/orders/refund"
        body = {"orderId": str(order_id)}

        response = self.request.post(url, body, raise_not_200=False)

        if response.status_code != 200:
            raise RefundError(response.json().get("message"))

    def withdraw(
        self,
        payment_system: PaymentTypes,
        requisite: str,
        amount: int | float,
        bank: str | int | None = None,
    ) -> None:
        """
        Создаёт заявку на вывод средств.

        :param payment_system: Тип платёжной системы для вывода
        :type payment_system:PaymentTypes
        :param requisite: Реквизиты для вывода (Номер карты / Номер СБП / Адрес крипты)
        :type requisite: str
        :param amount: Сумма к выводу
        :type amount: int | float
        :param bank: Только если вывод с помощью СБП, тогда указывать айди банка, иначе пропустить
        :type bank: str | int
        :return: None
        :rtype: None
        :raise WithdrawError: В случае возникновения ошибки
        """

        url = "https://starvell.com/api/payouts/create"
        body = {
            "paymentSystemId": format_payment_methods(payment_system),
            "amount": amount * 100,
            "address": requisite,
            "cardHolder"
            if payment_system is not PaymentTypes.SBP
            else "sbpBankId": "starvell"
            if payment_system is not PaymentTypes.SBP
            else bank,
        }

        response = self.request.post(url, body, raise_not_200=False).json()

        if response.status_code != 200:
            raise WithdrawError(response.get("message"))

    def save_settings(
        self,
        is_offers_visible: bool,
        updated_parameter: dict[str, Any] | None = None,
    ) -> None:
        """
        Сохраняет настройки аккаунта.

        :param is_offers_visible: Отображать-ли лоты в профиле?
        :type is_offers_visible: bool
        :param updated_parameter: Обновлённый параметр (словарь (обновлённый параметр: значение)), если требовалось изменение только видимости лотов, то можно не указывать
        :type updated_parameter: dict
        :return: None
        :rtype: None
        :raise SaveSettingsError: В случае возникновения ошибки
        """

        url = "https://starvell.com/api/user/settings"
        body: dict[str, str | bool | None] = {
            "avatar": self.__avatar_id,
            "email": self.__email,
            "isOffersVisibleOnlyInProfile": is_offers_visible,
            "username": self.__username,
        }
        if updated_parameter:
            body.update(**updated_parameter)

        response = self.request.patch(url, body, raise_not_200=False)

        if response.status_code != 200:
            raise SaveSettingsError(response.json().get("message"))

    def block(self, user_id: int) -> None:
        """
        Добавляет пользователя в ЧС Аккаунта на Starvell.

        :param user_id: ID Пользователя
        :type user_id: int
        :return: None
        :rtype: None
        :raise BlockError: В случае возникновения ошибки
        """

        url = "https://starvell.com/api/blacklisted-users/block"
        body: dict[str, int] = {"targetId": user_id}

        response = self.request.post(url, body, raise_not_200=False)

        if response.status_code != 200:
            raise BlockError(response.json().get("message"))

    def unblock(self, user_id: int) -> None:
        """
        Удаляет пользователя из ЧС Аккаунта Starvell.

        :param user_id: ID Пользователя
        :type user_id: int
        :return: None
        :rtype: None
        :raise UnBlockError: В случае возникновения ошибки
        """

        url = "https://starvell.com/api/blacklisted-users/unblock"
        body: dict[str, int] = {"targetId": user_id}

        response = self.request.post(url, body, raise_not_200=False)

        if response.status_code != 200:
            raise UnBlockError(response.json().get("message"))

    def send_typing(
        self, chat_id: str | UUID, is_typing: bool, count: int = 1
    ) -> None:
        """
        Отправляет "Печатает..." в чат на 4 секунды

        :param chat_id: ID Чата
        :type chat_id: str | UUID
        :param is_typing: True - Отправляет "Печатает...", False - Останавливает "Печатает..."
        :type is_typing: bool
        :param count: 1 раз - 4 секунды
        :type count: int
        :return: None
        :rtype: None
        """

        url = "https://starvell.com/api/chats/send-typing"
        body = {"chatId": str(chat_id), "isTyping": is_typing}

        for i in range(count):
            response = self.request.post(
                url=url, body=body, raise_not_200=False
            )

            if response.status_code != 200:
                raise SendTypingError(response.json().get("message"))
            time.sleep(4)

    @property
    def user(self):
        return MyProfileProperty(
            self.__username,
            self.__id,
            self.__email,
            self.__created_date,
            self.__avatar_id,
            self.__banner_id,
            self.__description,
            self.__is_verified,
            self.__rating,
            self.__reviews_count,
            self.__balance_hold,
            self.__balance,
            self.__active_orders,
        )

    @classmethod
    def from_json_cookie(
        cls, cookie_json: list[dict], proxy: dict[str, str] | None = None
    ) -> "Client":
        """
        Инициализирует аккаунт с помощью полного JSON'а с куками (Полученные например с расширения cookie-editor)

        :param cookie_json: Полностью скопированные куки с расширения в формате JSON
        :type cookie_json: list[dict]
        :param proxy: Прокси с которого будут осуществляться запросы (пример: {"http": "http://user:password@your_proxy_ip:port"})
        :type proxy: dict[str, str] | None

        :return: Экземпляр Client
        :raise ValueError: В случае, если формат куки неправильный
        """

        session_id = None

        for value in cookie_json:
            if value["name"] == "session":
                session_id = value["value"]
                break

        if not session_id:
            raise ValueError("формат куки неправильный")

        return cls(session_id=session_id, proxy=proxy)

    @classmethod
    def from_header_string_cookie(
        cls, cookie_header_string: str, proxy: dict[str, str] | None = None
    ) -> "Client":
        """
        Инициализирует аккаунт с помощью полного Header String'а с куками (Полученные например с расширения cookie-editor)

        :param cookie_header_string: Полностью скопированные куки с расширения в формате Header-String
        :type cookie_header_string: str
        :param proxy: Прокси с которого будут осуществляться запросы (пример: {"http": "http://user:password@your_proxy_ip:port"})
        :type proxy: dict[str, str] | None

        :return: Экземпляр Client
        :raise ValueError: В случае, если формат куки неправильный
        """

        regex = re.search(r"session=([^;]+)", cookie_header_string, flags=re.I)

        if not regex:
            raise ValueError("формат куки неправильный")

        return cls(regex.group(1), proxy=proxy)
