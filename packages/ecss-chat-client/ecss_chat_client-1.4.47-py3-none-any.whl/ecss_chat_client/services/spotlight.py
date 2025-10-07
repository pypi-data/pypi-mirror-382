from typing import Literal, Optional

from requests import Response

from .lib import Base
from ..types.spotlight import (
    SpotlightPaginatedSchemas,
    SpotlightSchemas,
)
from ..utils.decorators import decorator_service


class Spotlight(Base):
    """Сервис Spotlight."""

    def search_by_spotlight(
            self,
            page_count: int,
            search_query: str,
            search_schema: list[SpotlightSchemas],
    ) -> Response:
        """Поиск spotlight с заданными параметрами.

        :param page_count: максимально количество возвращаемых объектов
        :param search_query: строка для фильтрации
        :param search_schema: параметры фильтрации

        :return: requests.Response
        """
        return self._make_request(
            endpoint='spotlight',
            payload={
                'count': page_count,
                'query': search_query,
                'searchSchema': search_schema,
            },
        )

    @decorator_service.paginate
    def search_spotlight_paginated(
            self,
            query: str,
            sample: Optional[
                Literal
                [
                    SpotlightPaginatedSchemas.USERS,
                    SpotlightPaginatedSchemas.ROOMS,
                ]
            ] = None,
            offset: Optional[int] = None,
            count: Optional[int] = None,
            exception: Optional[str] = None,
    ) -> Response:
        """Поиск spotlight paginated с заданными параметрами.

        :param query: строка для фильтрации
        :param sample: тип поиска
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений
        :param exception: строка по которой следует исключить результаты

        :return: requests.Response
        """
        search_type_dict: dict = {'users': '@', 'rooms': '%23'}
        if sample:
            search: str = search_type_dict.get(sample)
            return self._make_request(
                f'spotlight.paginated?offset={offset}&count={count}'
                f'&query={search}{query}&exceptions={exception}',
                method='get',
            )
        return self._make_request(
            f'spotlight.paginated?offset={offset}&count={count}'
            f'&query={sample}{query}&exceptions={exception}',
            method='get',
        )

    def search_spotlight_paginated_broken(
            self,
            url: str,
    ) -> Response:
        """Тестовый эндпоинт без параметров для проверки валидации.

        :param url: эндпоинт

        :return: requests.Response
        """
        return self._make_request(
            url,
            method='get',
        )
