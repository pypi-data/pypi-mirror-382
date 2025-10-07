from pathlib import Path
from typing import Optional

import magic
import urllib3
from requests import Response

urllib3.disable_warnings()


def remove_none(data):
    if isinstance(data, dict):
        return {k: remove_none(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_none(item) for item in data if item is not None]
    else:
        return data


class Base:
    def __init__(self, client):
        self.client = client
        self.short_url = client.short_url
        self.settings = client.settings
        self.proto = client.proto
        self.verify = client.verify
        self.server = client.server
        self.port = client.port
        self.tus_header_keys = [
            'Upload-Metadata',
            'Content-Length',
            'Upload-Offset',
            'Tus-Resumable',
            'Upload-Length',
            'Content-Type',
        ]

    def _make_request(  # noqa
            self,
            endpoint,
            payload=None,
            params=None,
            method='post',
            files=None,
            short_path=False,
            tus_path=False,
            api_info=False,
    ) -> Response:
        """Отправка запроса к API.

        :param endpoint: эндпоинт
        :param payload: тело запроса
        :param params: query-параметры запроса
        :param method: метод запроса
        :param files: файлы в запросе
        :param short_path: обращение без /api/v1/
        :param tus_path: обращение к TUS сервису
        :param api_info: обращение к Swagger

        :return: requests.Response
        """
        payload = remove_none(payload)

        if tus_path is True:  # noqa
            url = f'{self.proto}://{self.server}/{endpoint}'
        elif api_info is True:
            url = f'{self.proto}://{self.server}/elph_chat/{endpoint}'
        elif short_path is False:
            url = f'{self.proto}://{self.server}:{self.port}/api/v1/{endpoint}'
        else:
            url = f'{self.proto}://{self.server}:{self.port}/{endpoint}'
        info = {
            'method': method.upper(),
            'username': getattr(self.client.session, 'username', 'unknown'),
            'url': url,
            'endpoint': endpoint,
            'headers': self.client.session.headers,
            'params': params or {},
            'payload': payload or {},
            'files': bool(files),
        }
        request_kwargs = {
            'params': params,
        }
        if files:
            request_kwargs['files'] = files
            if payload:
                request_kwargs['data'] = payload
        if tus_path is True and method.lower() == 'patch':
            request_kwargs['data'] = payload
        else:
            if payload:
                request_kwargs['json'] = payload
        if self.proto == 'https' and self.verify is False:
            request_kwargs['verify'] = self.verify
        request_method = getattr(self.client.session, method.lower())
        response = request_method(url, **request_kwargs)
        if tus_path is True:
            for tus_key in self.tus_header_keys:
                self.client.session.headers.pop(tus_key, None)
        response.info = info
        return response

    @staticmethod
    def get_mime_type(file_path: Path) -> str:
        """Определение MIME-типа файла.

        :param file_path: путь до файла

        :return: str
        """
        mime = magic.Magic(mime=True)
        file_mime_type = mime.from_file(filename=file_path)
        return file_mime_type or 'application/octet-stream'

    def _upload_file_base(
            self,
            endpoint: str,
            room_id: str,
            path: Path,
            text: Optional[str] = None,
            extra_data: Optional[dict] = None,
    ) -> Response:
        """Загрузка файла по api.

        :param endpoint: эндпоинт
        :param room_id: uid комнаты
        :param path: путь до файла
        :param text: текст сообщения
        :param extra_data: дополнительная информация в запросе

        :return: requests.Response
        """
        mtype = self.get_mime_type(path)
        data = {}
        if text:
            data['msg'] = text
        if extra_data:
            data.update(extra_data)
        with open(path, 'rb') as file_obj:
            files = {'file': (path, file_obj, mtype)}
            full_endpoint = f'{endpoint}/{room_id}'
            return self._make_request(full_endpoint, payload=data, files=files)
