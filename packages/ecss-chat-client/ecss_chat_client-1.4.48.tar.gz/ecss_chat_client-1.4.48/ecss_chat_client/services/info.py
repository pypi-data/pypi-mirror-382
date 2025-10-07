import requests
from requests import Response

from .lib import Base


class ApiInfo(Base):

    def server_version(self) -> Response:
        """Получение версии сервера.

        :return: requests.Response
        """
        return requests.get(f'{self.short_url}/info', verify=False)

    def server_time(self) -> Response:
        """Получение времени сервера.

        :return: requests.Response
        """
        return requests.get(f'{self.short_url}/timesync', verify=False)

    def swagger_info(self) -> Response:
        """Запрос к url сваггера.

        :return: request.Request
        """
        return self._make_request(
            endpoint='api',
            api_info=True,
            method='GET',
        )

    def open_api_yaml(self) -> Response:
        """Получение open api yaml сервиса.

        :return: request.Request
        """
        return self._make_request(
            endpoint='api-yaml',
            api_info=True,
            method='GET',
        )

    def open_api_json(self) -> Response:
        """Получение open api json сервиса.

        :return: request.Request
        """
        return self._make_request(
            endpoint='api-json',
            api_info=True,
            method='GET',
        )

    def static_recourse(self, endpoint: str) -> Response:
        """Получение статических ресурсов сваггера.

        :param endpoint: эндпоинт статического ресурса

        :return: request.Request
        """
        return self._make_request(
            endpoint=f'api/{endpoint}',
            api_info=True,
            method='GET',
        )
