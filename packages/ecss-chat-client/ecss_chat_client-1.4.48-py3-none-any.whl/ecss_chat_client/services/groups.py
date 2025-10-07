from pathlib import Path
from typing import Optional

from requests import Response

from .lib import Base
from ..utils.decorators import decorator_service


class Groups(Base):

    def create(
            self,
            name: str,
            member_ids: list[str],
            read_only: Optional[bool] = False,
    ) -> Response:
        """Создание группы.

        :param name: название группы
        :param member_ids: uid пользователей
        :param read_only: только для чтения

        :return: requests.Response
        """
        return self._make_request(
            endpoint='groups.create',
            payload={
                'name': name,
                'members': member_ids,
                'readOnly': read_only,
            },
        )

    @decorator_service.paginate
    def info(
            self,
            group_id: str,
            count: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Response:
        """Информация о группе.

        :param group_id: uid группы
        :param offset: колличество пропускаемых сообщений
        :param count: максимальное колличество получаемых сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='groups.info',
            params={
                'roomId': group_id,
                'offset': count,
                'count': offset,
            },
            method='get',
        )

    @decorator_service.paginate
    def members(
            self,
            group_id: str,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Response:
        """Участники группы.

        :param group_id: uid группы
        :param offset: колличество пропускаемых сообщений
        :param count: максимальное колличество получаемых сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='groups.members',
            params={
                'roomId': group_id,
                'offset': offset,
                'count': count,
            },
            method='get',
        )

    def invite(self, group_id: str, user_id: str) -> Response:
        """Пригласить в группу.

        :param group_id: uid комнаты
        :param user_id: uid юзера

        :return: requests.Response
        """
        return self._make_request(
            endpoint='groups.invite',
            payload={
                'roomId': group_id,
                'userId': user_id,
            })

    def delete(self, group_id: str) -> Response:
        """Удалить группу.

        :param group_id: uid группы
        :return: requests.Response
        """
        return self._make_request(
            endpoint='groups.delete',
            payload={
                'roomId': group_id,
            },
        )

    def rename(self, group_id: str, name: str) -> Response:
        """Переименовать группу.

        :param group_id: uid группы
        :param name: новое название группы

        :return: requests.Response
        """
        return self._make_request(
            endpoint='groups.rename',
            payload={
                'roomId': group_id,
                'name': name,
            })

    def set_avatar(self, group_id: str, file_path: Path) -> Response:
        """Установка аватарки группы.

        :param group_id: uid группы
        :param file_path: путь до картинки

        :return: requests.Response
        """
        return self._upload_file_base(
            endpoint='groups.setAvatar',
            room_id=group_id,
            path=file_path,
            text=None,
        )

    def convert_to_supergroup(
            self,
            group_id: str,
            topic_name: str,
            emoji: str,
    ) -> Response:
        """Конвертация группы в супергруппу.

        :param group_id: uid группы
        :param topic_name: название топика
        :param emoji: код эмодзи

        :return: requests.Response
        """
        return self._make_request(
            endpoint='groups.convertToSupergroup',
            payload={
                'roomId': group_id,
                'defaultTopic': {
                    'fname': topic_name,
                    'emoji': emoji,
                },
            },
        )

    def add_owner(self, group_id: str, user_id: str) -> Response:
        """Добавление владельца группы.

        :param group_id: uid группы
        :param user_id: uid пользователя которого делаем владельцем

        :return: requests.Response
        """
        return self._make_request(
            endpoint='groups.addOwner',
            payload={
                'roomId': group_id,
                'userId': user_id,
            },
        )

    def kick(self, group_id: str, user_id: str) -> Response:
        """Кик из группы.

        :param group_id: uid группы
        :param user_id: uid пользователя которого кикаем

        :return: requests.Response
        """
        return self._make_request(
            endpoint='groups.kick',
            payload={
                'roomId': group_id,
                'userId': user_id,
            },
        )
