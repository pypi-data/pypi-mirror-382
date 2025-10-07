from requests import Response
from typing_extensions import deprecated

from .lib import Base


class Avatars(Base):

    @deprecated('Устаревшая функция')
    def get_avatar(self, user_id: str) -> Response:
        return self._make_request(
            endpoint=f'avatar/{user_id}',
            params={
                'etag': 'DEFAULT',
            },
            method='get',
        )

    def get_avatar_user(self, user_id: str) -> Response:
        """Получение аватара юзера по его uid.

        :param user_id: uid юзера

        :return: requests.Response
        """
        return self._make_request(
            endpoint=f'avatar/user/{user_id}',
            method='get',
            short_path=True,
        )

    def get_avatar_room(self, room_id: str) -> Response:
        """Получение аватара комнаты по ее uid.

        :param room_id: uid комнаты

        :return: requests.Response
        """
        return self._make_request(
            endpoint=f'avatar/room/{room_id}',
            method='get',
            short_path=True,
        )
