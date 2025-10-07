import json
from typing import Optional

from requests import Response

from .lib import Base
from ..types.settings import \
    server_settings_type  # noqa
from ..utils.decorators import decorator_service


class ServerSettings(Base):

    @decorator_service.paginate
    def settings_public(
            self,
            count: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Response:
        """Получение настроек сервера.

        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='settings.public',
            params={
                'offset': offset,
                'count': count,
            },
            method='get',
        )

    def setting_public_by_id(self, setting_id: str) -> Response:
        """Получить настройку сервера по uid.

        :param setting_id: uid настройки

        :return: requests.Response
        """
        return self._make_request(
            endpoint=f'settings.public/{setting_id}',
            method='get',
        )

    def hide_setting_by_id(self, setting_id: str) -> Response:
        """Получить скрытую настройку по uid.

        :param setting_id: uid настройки

        :return: requests.Response
        """
        return self._make_request(
            endpoint=f'settings/{setting_id}',
            method='GET',
        )

    def setting_set(
            self,
            setting_name: (
                    server_settings_type.FILES |
                    server_settings_type.MOBILE |
                    server_settings_type.MESSAGES |
                    server_settings_type.FOLDERS |
                    server_settings_type.SECURITY_USER,
            ),
            value: bool | str | int | list[str] | dict,
    ) -> Response:
        """Установка настройки сервера.

        :param setting_name: название настройки
        :param value: значение настройки

        :return: requests.Response
        """
        if type(value) is dict:
            value = json.dumps(value)
        return self._make_request(
            endpoint='settings.set',
            payload={
                'id': setting_name,
                'value': value,
            },
        )
