from typing import Optional

from requests import Response

from .lib import Base


class Bots(Base):

    def create(
            self,
            username: str,
            name: str,
            domain: Optional[str] = 'test_domain',
    ) -> Response:
        """Создание бота.

        :param username: Уникальное имя
        :param name: Отображаемое имя
        :param domain: Домен

        :return: requests.Response
        """
        return self._make_request(
            endpoint='bots.create',
            payload={
                'username': username,
                'name': name,
                'domain': domain,
            },
        )

    def update(self, name: str, bot_uid: str) -> Response:
        """Обновление имени бота.

        :param name: Новое имя пользователя
        :param bot_uid: uid бота

        :return: requests.Response
        """
        return self._make_request(
            endpoint='bots.update',
            params={
                'id': bot_uid,
            },
            payload={
                'name': name,
            },
            method='put',
        )

    def delete(self, bot_uid: str) -> Response:
        """Удаление бота.

        :param bot_uid: uid бота

        :return: requests.Response
        """
        return self._make_request(
            endpoint='bots.delete',
            params={
                'id': bot_uid,
            },
            method='delete',
        )

    def regenerate_token(self, bot_uid: str) -> Response:
        """Генерация нового токена.

        :param bot_uid: uid бота

        :return: requests.Response
        """
        return self._make_request(
            endpoint='bots.regenerate-token',
            params={
                'id': bot_uid,
            },
        )
