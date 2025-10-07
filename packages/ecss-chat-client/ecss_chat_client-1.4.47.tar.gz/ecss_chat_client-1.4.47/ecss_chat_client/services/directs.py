from typing import Literal, Optional

from requests import Response

from .lib import Base
from ..utils.decorators import decorator_service


class Directs(Base):

    def im_create_username(self, user_username: str) -> Response:
        """Создание директа по username.

        :param user_username: username пользователя с которым создаем директ

        :return: requests.Response
        """
        return self._make_request(
            endpoint='im.create',
            payload={
                'username': user_username,
            },
        )

    @decorator_service.paginate
    def im_members(
            self,
            room_id: str,
            count: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Response:
        """Получение участников директа.

        :param room_id: uid комнаты
        :param offset: колличество пропускаемых сообщений
        :param count: максимальное колличество получаемых сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='im.members',
            params={
                'roomId': room_id,
                'count': count,
                'offset': offset,
            },
            method='get',
        )

    def dm_create_user_id(self, user_id: str) -> Response:
        """Создание директа по uid.

        :param user_id: uid пользователя с которым создаем директ

        :return: requests.Response
        """
        return self._make_request(
            endpoint='dm.create',
            payload={
                'userId': user_id,
            },
        )

    def dm_delete(
            self,
            room_id: str,
            delete_type: Literal['soft', 'hard'],
    ) -> Response:
        """Удаление директа.

        :param room_id: uid комнаты
        :param delete_type: тип удаления

        :return: requests.Response
        """
        return self._make_request(
            endpoint='dm.delete',
            payload={
                'roomId': room_id,
                'type': delete_type,
            })
