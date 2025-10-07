import threading
from typing import Any, Callable, Iterable

from websocket import WebSocketApp

from starvell.account import Client
from starvell.enums import MessageType, SocketTypes
from starvell.errors import HandlerError, ReviewNotFoundError
from starvell.socket import Socket
from starvell.types import (
    NewMessageEvent,
    OrderEventShort,
    BaseMessage,
    OrderEvent,
)
from starvell.utils import get_clear_dict


class EventListener:
    def __init__(self, acc: Client, always_online: bool = True):
        """
        :param acc: Экземпляр класса Client
        :param always_online: Поддерживать-ли постоянный онлайн? (True - при использовании API, аккаунт всегда будет онлайн)
        """

        self.acc: Client = acc

        self.socket: Socket = Socket(acc.session_id, always_online)
        self.socket.handlers[SocketTypes.OPEN].append(self.on_open_process)
        self.socket.handlers[SocketTypes.NEW_MESSAGE].append(
            self.on_new_message
        )

        self.handlers: dict[MessageType | SocketTypes, list] = {
            MessageType.NEW_MESSAGE: [],
            MessageType.NEW_ORDER: [],
            MessageType.CONFIRM_ORDER: [],
            MessageType.ORDER_REOPENED: [],
            MessageType.ORDER_REFUND: [],
            MessageType.NEW_REVIEW: [],
            MessageType.REVIEW_DELETED: [],
            MessageType.REVIEW_CHANGED: [],
            MessageType.REVIEW_RESPONSE_EDITED: [],
            MessageType.REVIEW_RESPONSE_CREATED: [],
            MessageType.REVIEW_RESPONSE_DELETED: [],
            MessageType.BLACKLIST_YOU_ADDED: [],
            MessageType.BLACKLIST_USER_ADDED: [],
            MessageType.BLACKLIST_YOU_REMOVED: [],
            MessageType.BLACKLIST_USER_REMOVED: [],
            SocketTypes.OPEN: [],
            SocketTypes.NEW_MESSAGE: [],
        }

        self.event_types: dict[
            MessageType,
            type[NewMessageEvent | OrderEventShort | BaseMessage],
        ] = {
            MessageType.NEW_MESSAGE: NewMessageEvent,
            MessageType.NEW_ORDER: OrderEventShort,
            MessageType.CONFIRM_ORDER: OrderEventShort,
            MessageType.ORDER_REFUND: OrderEventShort,
            MessageType.ORDER_REOPENED: OrderEventShort,
            MessageType.NEW_REVIEW: OrderEventShort,
            MessageType.REVIEW_DELETED: OrderEventShort,
            MessageType.REVIEW_CHANGED: OrderEventShort,
            MessageType.REVIEW_RESPONSE_EDITED: OrderEventShort,
            MessageType.REVIEW_RESPONSE_CREATED: OrderEventShort,
            MessageType.REVIEW_RESPONSE_DELETED: OrderEventShort,
            MessageType.BLACKLIST_YOU_REMOVED: BaseMessage,
            MessageType.BLACKLIST_USER_REMOVED: BaseMessage,
            MessageType.BLACKLIST_YOU_ADDED: BaseMessage,
            MessageType.BLACKLIST_USER_ADDED: BaseMessage,
        }

        self.add_handler(
            SocketTypes.NEW_MESSAGE,
            handler_filter=lambda msg, *args: msg.startswith("42/chats"),
        )(self.msg_process)
        self.add_handler(
            SocketTypes.NEW_MESSAGE,
            handler_filter=lambda msg, *args: msg == "2",
        )(lambda _, ws: ws.send("3"))

    @staticmethod
    def handling(handler: list[Callable[[Any], None] | dict], *args) -> None:
        """
        Вызывает хэндлер с переданными аргументами

        :param handler: Хэндлер который будет обрабатывать
        :param args: Аргументы к этому хэндлеру

        :return: None
        """

        if handler[1] is None:
            threading.Thread(target=handler[0], args=args).start()
        else:
            if not isinstance(handler[1], (list, tuple, set)):
                if handler[1](*args, **handler[2]):
                    threading.Thread(target=handler[0], args=args).start()
            else:
                if all([h(*args, **handler[2]) for h in handler[1]]):
                    threading.Thread(target=handler[0], args=args).start()

    def add_handler(
        self,
        handler_type: Iterable[MessageType | SocketTypes]
        | MessageType
        | SocketTypes,
        handler_filter: list[Callable] | Callable | None = None,
        **kwargs: object,
    ) -> Callable[[Any], None]:
        """
        Добавляет хэндлер

        Примеры:

        ``@add_handler(MessageType.NEW_MESSAGE)``

        ``@add_handler(SocketTypes.NEW_MESSAGE)``

        :param handler_type: MessageType либо SocketTypes
        :param handler_filter: Функция-фильтр, указывать необязательно, в случае если эта функция вернёт False, хэндлер не сработает

        :return: Callable
        """

        def decorator(func):
            if isinstance(handler_type, Iterable):
                for h in handler_type:
                    self.handlers[h].append([
                        func,
                        handler_filter,
                        kwargs,
                    ])
            else:
                self.handlers[handler_type].append([
                    func,
                    handler_filter,
                    kwargs,
                ])

            return func

        return decorator

    def msg_process(self, msg: str, _: WebSocketApp) -> None:
        """
        Вызывается при новом сообщении в веб-сокете
        в случае если это новое событие на Starvell, определяет событие
        и вызывает все привязанные к этому событию хэндлеры (функции)

        Каждый хэндлер (функция), вызывается в отдельном потоке

        :param _: WebSocketApp
        :param msg: Сообщение с веб-сокета

        :return: None
        """

        data = get_clear_dict(msg)

        model = BaseMessage.model_validate(data, by_alias=True)
        translate = self.event_types[model.type]
        new = translate.model_validate(data, by_alias=True)

        if isinstance(new, OrderEventShort):
            back_to_json = new.model_dump(by_alias=True)
            back_to_json["order"] = self.acc.get_order(new.order.id)
            try:
                back_to_json["review"] = self.acc.get_review(new.order.id)
            except ReviewNotFoundError:
                back_to_json["review"] = None
            new = OrderEvent.model_validate(back_to_json, by_alias=True)

        for handler in self.handlers[model.type]:
            try:
                self.handling(handler, new)
            except Exception as e:
                raise HandlerError(f"error in {handler[0].__name__}: {e}")

    def on_open_process(self, ws: WebSocketApp) -> None:
        """
        Вызывается при открытии веб-сокета, и вызывает все привязанные к этому событию хэндлере

        Каждый хэндлер (функция), вызывается в отдельном потоке

        :param ws: WebSocketApp

        :return: None
        """

        for func in self.handlers[SocketTypes.OPEN]:
            try:
                self.handling(func, ws)
            except Exception as e:
                raise HandlerError(str(e))

    def on_new_message(self, ws: WebSocketApp, msg: str) -> None:
        """
        Вызывается при новом сообщении в веб-сокете, и вызывает все привязанные к этому событию хэндлеры (Не путать с новым сообщением на Starvell)

        Каждый хэндлер (функция), вызывается в отдельном потоке

        :param ws: WebSocketApp
        :param msg: Сообщение веб-сокета (Строка)

        :return: None
        """

        for func in self.handlers[SocketTypes.NEW_MESSAGE]:
            try:
                self.handling(func, msg, ws)
            except Exception as e:
                raise HandlerError(str(e))
