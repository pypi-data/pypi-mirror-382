import datetime
import time
import uuid
from typing import List, Literal, Optional

from requests import Response

from .lib import Base
from ..types.attachments import AttachmentsType
from ..utils.decorators import decorator_service


class Messages(Base):

    def send(
            self,
            text: str,
            room_id: str,
            file_ids: Optional[list[str]] = None,
            generate_uid: bool = True,
            uid: Optional[uuid.UUID] = None,
    ) -> tuple[Response, str]:
        """Отправка сообщения в комнату.

        :param text: текст сообщения
        :param room_id: uid комнаты
        :param file_ids: список с uid файлов
        :param generate_uid: Сгенерировать ли uid для сообщения
        :param uid: uid для сообщения(только если generate_uid is True)

        :return: tuple[request.Response, str]
        """
        if generate_uid is True:
            _uuid = str(uuid.uuid4())
        else:
            _uuid = uid
        return self._make_request(
            endpoint='chat.sendMessage',
            payload={
                'message': {
                    'rid': room_id,
                    'msg': text,
                    '_id': _uuid,
                    'fileIds': file_ids,
                },
            },
        ), _uuid

    def reply(
            self,
            text: str,
            room_id: str,
            message_id: str,
    ) -> Response:
        """Ответ на сообщение.

        :param text: текст сообщения
        :param room_id: uid комнаты
        :param message_id: uid сообщения на которое отвечаем

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.sendMessage',
            payload={
                'message': {
                    'rid': room_id,
                    'msg': text,
                    'toReplyId': message_id,
                },
            },
        )

    def forward_message(
            self,
            to_room_id: str,
            from_room_id: str,
            forwarded_message_ids: List[str],
            new_message_ids: Optional[List[str]] = None,
    ) -> Response:
        """Пересылка сообщения из комнаты в комнату.

        :param to_room_id: uid комнаты куда пересылается сообщение
        :param from_room_id: uid комнаты откуда пересылается сообщение
        :param forwarded_message_ids: uid сообщений которые пересылаются
        :param new_message_ids: навые uid сообщений который пересылаем

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.forwardMessages',
            payload={
                'roomId': to_room_id,
                'toForwardRoomId': from_room_id,
                'toForwardIds': forwarded_message_ids,
                'forwardedIds': new_message_ids,
            },
        )

    def deferred_message(
            self,
            room_id: str,
            deferr_time: datetime,
            text: Optional[str] = None,
            alias: Optional[str] = None,
            emoji: Optional[str] = None,
            avatar: Optional[str] = None,
            attachments: Optional[str] = None,
    ) -> Response:
        """Создание отложенного сообщения.

        :param room_id: uid комнаты в которую отправится сообщение
        :param deferr_time: datetime дата когда сообщение должно быть
        отправлено
        :param text: текст сообщения
        :param alias: псевдоним сообщения
        :param emoji: эмодзи
        :param avatar: url аватара
        :param attachments:

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.deferredMessage',
            payload={
                'rid': room_id,
                'text': text,
                'alias': alias,
                'emoji': emoji,
                'avatar': avatar,
                'attachments': attachments,
                'runAt': deferr_time,
            },
        )

    def get_deferred_message(self, room_id: Optional[str] = None) -> Response:
        """Получение информации о отложенных сообщениях.

        :param room_id: uid комнаты

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.deferredMessage',
            params={
                'rid': room_id,
            },
            method='get',
        )

    def update_deferred_message(
            self,
            room_id: str,
            job_id: str,
            deferr_time: Optional[datetime] = None,
            text: Optional[str] = None,
            alias: Optional[str] = None,
            emoji: Optional[str] = None,
            avatar: Optional[str] = None,
            attachments: Optional[str] = None,
    ) -> Response:
        """Обновление отложенного сообщения.

        :param room_id: uid комнаты
        :param job_id: uid задачи
        :param deferr_time: дата отправки отложенного сообщения
        :param text: текст сообщения
        :param alias: псевдоним сообщения
        :param emoji: эмодзи
        :param avatar: url аватара
        :param attachments:

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.deferredMessage',
            payload={
                'rid': room_id,
                'text': text,
                'alias': alias,
                'emoji': emoji,
                'avatar': avatar,
                'attachments': attachments,
                'runAt': deferr_time,
                'jobId': job_id,
            },
            method='put',
        )

    def delete_deferred_message(self, job_id: str) -> Response:
        """Удаление отложенного сообщения.

        :param job_id: uid задачи

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.deferredMessage',
            payload={
                'jobId': job_id,
            },
            method='delete',
        )

    def message_history(
            self,
            room_id: str,
            limit: Optional[int] = 50,
            before: Optional[int] = time.time(),
            after: Optional[int] = 0,
            sort: Optional[Literal[-1, 1]] = -1,
    ) -> Response:
        """Получение истории сообщений.

        :param room_id: uid комнаты
        :param limit: лимит получаемых сообщений
        :param before: искать сообщения старше (timestamp)
        :param after: искать сообщения и/или моложе (timestamp)
        :param sort: сортировка (-1 сначала последние)

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.loadMessageHistory',
            payload={
                'roomId': room_id,
                'limit': limit,
                'before': before,
                'after': after,
                'sort': sort,
            },
        )

    def pin(self, message_id: str) -> Response:
        """Закрепление сообщения.

        :param message_id: uid сообщения

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.pinMessage',
            payload={
                'messageId': message_id,
            },
        )

    def unpin(self, message_id: str) -> Response:
        """Открепление сообщения.

        :param message_id: uid сообщения

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.unPinMessage',
            payload={
                'messageId': message_id,
            },
        )

    @decorator_service.paginate
    def pinned_messages(
            self,
            room_id: str,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Response:
        """Получение закрепленных сообщений в комнате.

        :param room_id: uid комнаты
        :param offset: колличество пропускаемых сообщений
        :param count: максимальное колличество получаемых сообщений

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.getPinnedMessages',
            params={
                'roomId': room_id,
                'offset': offset,
                'count': count,
            },
            method='get',
        )

    def set_reaction(
            self,
            emoji: str,
            message_id: str,
            room_id: str,
            should_react: Optional[bool] = None,
    ) -> Response:
        """Установка реакции на сообщение.

        :param emoji: код эмодзи
        :param message_id: uid сообщения
        :param room_id: uid комнаты
        :param should_react: поставить реакцию или убрать реакцию

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.react', payload={
                'emoji': emoji,
                'messageId': message_id,
                'roomId': room_id,
                'shouldReact': should_react,
            },
        )

    @decorator_service.paginate
    def message_reactions(
            self,
            message_id: str,
            room_id: Optional[str] = None,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Response:
        """Получение реакций под сообщением.

        :param message_id: uid сообщения
        :param room_id: uid комнаты
        :param offset: колличество пропускаемых реакций
        :param count: максимальное количество реакций

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.messageReactions',
            params={
                'msgId': message_id,
                'roomId': room_id,
                'offset': count,
                'count': offset,
            },
            method='get',
        )

    def message_by_id(self, message_id: str) -> Response:
        """Получение информации о сообщении по его uid.

        :param message_id: uid сообщения

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.getMessage',
            params={
                'msgId': message_id,
            },
            method='get',
        )

    @decorator_service.paginate
    def message_by_text(
            self,
            text: str,
            room_id: str,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Response:
        """Поиск сообщения по тексту.

        :param text: текст сообщения
        :param room_id: uid комнаты
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.search',
            params={
                'searchText': text,
                'roomId': room_id,
                'offset': offset,
                'count': count,
            },
            method='get',
        )

    @decorator_service.paginate
    def message_readers(
            self,
            message_id: str,
            room_id: Optional[str] = None,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Response:
        """Получение информации о прочитавших сообщение.

        :param message_id: uid сообщения
        :param room_id: uid комнаты
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.messageReadUsers',
            params={
                'msgId': message_id,
                'roomId': room_id,
                'count': count,
                'offset': offset,
            },
            method='get',
        )

    def create_draft(
            self,
            room_id: str,
            text: str,
            draft_type: Optional[
                Literal
                [
                    'reply', 'none', 'forward', 'edit',
                ]
            ] = 'none',
            data: Optional[dict] = None,
    ) -> Response:
        """Создание черновика сообщения.

        :param room_id: uid комнаты
        :param text: текст сообщения
        :param draft_type: тип черновика
        :param data:

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.draft',
            payload={
                'roomId': room_id,
                'msg': text,
                'mode': {
                    'type': draft_type,
                    'data': data,
                },
            })

    def get_draft(self, room_id: str) -> Response:
        """Получение черновика сообщения.

        :param room_id: uid комнаты

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.draft',
            params={
                'roomId': room_id,
            },
            method='get',
        )

    def delete_message(
            self,
            message_id: str,
            room_id: str,
            as_user: Optional[bool] = None,
    ) -> Response:
        """Удаление сообщения.

        :param message_id: uid сообщения
        :param room_id: uid комнаты
        :param as_user:

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.delete',
            payload={
                'msgId': message_id,
                'roomId': room_id,
                'asUser': as_user,
            },
        )

    @decorator_service.paginate
    def deleted_messages(
            self,
            room_id: str,
            since: int,
            count: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Response:
        """Получение удаленных сообщений.

        :param room_id: uid комнаты
        :param since: с какой даты (timestamp)
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.getDeletedMessages',
            params={
                'roomId': room_id,
                'since': since,
                'count': count,
                'offset': offset,
            },
            method='GET',
        )

    @decorator_service.paginate
    def chat_search_attachments(
            self,
            room_id: str,
            content_types: Optional[list[AttachmentsType]] = None,
            after_date: Optional[int] = None,
            before_date: Optional[int] = None,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Response:
        """Поиск вложенний в комнате по его типу.

        :param room_id: uid комнаты
        :param content_types: типы вложенний
        :param after_date: поиск после этой даты (timestamp)
        :param before_date: поиск до этой даты (timestamp)
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.attachments',
            params={
                'offset': offset,
                'count': count,
            },
            payload={
                'roomId': room_id,
                'contentTypes': content_types,
                'afterDate': after_date,
                'beforeDate': before_date,
            },
        )

    @decorator_service.paginate
    def search_in_attachments(
            self,
            room_id: str,
            content_types: Optional[list[AttachmentsType]] = None,
            search_text: Optional[str] = None,
            after_date: Optional[int] = None,
            before_date: Optional[int] = None,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Response:
        """Поиск вложенний в комнате.


        :param room_id: uid комнаты
        :param content_types: типы файлов
        :param search_text: поиск по названию файла
        :param after_date: поиск после этой даты (timestamp)
        :param before_date: поиск до этой даты (timestamp)
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: request.Response
        """
        return self._make_request(
            endpoint='chat.searchInAttachments',
            params={
                'offset': offset,
                'count': count,
            },
            payload={
                'roomId': room_id,
                'searchContextTypes': content_types,
                'searchText': search_text,
                'afterDate': after_date,
                'beforeDate': before_date,
            },
        )

    def read_messages(self, room_id: str) -> Response:
        """Пометить что прочитал сообщения в комнате.

        :param room_id: uid комнаты

        :return: request.Response
        """
        return self._make_request(
            endpoint='subscriptions.read',
            payload={
                'rid': room_id,
            },
        )
