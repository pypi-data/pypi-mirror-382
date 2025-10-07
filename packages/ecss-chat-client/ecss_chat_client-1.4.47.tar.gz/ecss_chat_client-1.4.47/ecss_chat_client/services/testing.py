from typing import Optional

from requests import Response

from .lib import Base


class Testing(Base):

    def new_user(
            self,
            username: str,
            name: str,
            domain: str,
            password: Optional[str] = None,
    ) -> Response:
        """Создание тестового юзера.

        :param username: никнейм пользователя
        :param name: имя пользователя
        :param password: пароль пользователя
        :param domain: домен на который регистрируется пользователь

        :return: requests.Response
        """
        return self._make_request(
            endpoint='testing.newUser',
            payload={
                'username': username,
                'name': name,
                'password': password,
                'domain': domain,
            },
        )
