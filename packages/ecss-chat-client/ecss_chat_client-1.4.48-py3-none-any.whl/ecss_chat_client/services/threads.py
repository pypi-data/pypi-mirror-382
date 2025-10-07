from typing import Literal, Optional

from requests import Response

from .lib import Base
from ..utils.decorators import decorator_service


class Threads(Base):

    def create(self, message_id: str, room_id: str) -> Response:
        """Создание треда.

        :param message_id: uid сообщения от которого создается тред
        :param room_id: uid комнаты

        :return: requests.Response
        """
        return self._make_request(
            endpoint='thread.createOrJoinWithMessage',
            payload={
                'mid': message_id,
                'roomId': room_id,
            },
        )

    @decorator_service.paginate
    def list(
            self,
            room_id: str,
            sort_by_ts: Optional[Literal[-1, 1]] = None,
            only_membered_thread: Optional[bool] = None,
            alerted_only: Optional[bool] = None,
            before: Optional[int] = None,
            after: Optional[int] = None,
            count: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Response:
        """Список тредов в комнате.

        :param room_id: uid комнаты
        :param sort_by_ts: сортировка к меньшему(-1) к большему(1)
        :param only_membered_thread: фильтрация по участию в тредах
        :param alerted_only: фильтрация по упоминаниям в тредаъ
        :param before: фильтрация поиск до определенной даты (timestamp)
        :param after: фильтрация поиск после определенной даты (timestamp)
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='thread.list',
            params={
                'roomId': room_id,
                'sortByTs': sort_by_ts,
                'showOnlyMemberedThread': str(only_membered_thread).lower(),
                'alertedOnly': str(alerted_only).lower(),
                'before': before,
                'after': after,
                'count': count,
                'offset': offset,
            },
            method='GET',
        )
