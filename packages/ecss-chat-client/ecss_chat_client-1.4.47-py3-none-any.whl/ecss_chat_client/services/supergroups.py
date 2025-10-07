from pathlib import Path
from typing import Optional

from requests import Response

from .lib import Base
from ..utils.decorators import decorator_service


class SuperGroups(Base):

    def create(
            self,
            name: str,
            members_ids: Optional[list[str]] = None,
            topics: Optional[list[dict]] = None,
    ) -> Response:
        """Создание супергруппы.

        :param name: название группы
        :param members_ids: uid пользователей которых надо пригласить
        :param topics: информация о создаваемых топиках
        :param uid: uid для комнаты

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.create',
            payload={
                'supergroups': [
                    {
                        'fname': name,
                        'members': members_ids,
                        'topics': topics,
                    },
                ],
            },
        )

    def add_topics(
            self,
            room_id: str,
            topic_name: str,
            topic_emoji: Optional[str] = None,
            topic_uid: Optional[str] = None,
    ) -> Response:
        """Добавление топика в супергруппу.

        :param room_id: uid комнаты
        :param topic_name: название топика
        :param topic_emoji: код эмодзи для топика
        :param topic_uid: uid для топика

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.addTopics',
            payload={
                'roomId': room_id,
                'topics': [
                    {
                        'fname': topic_name,
                        'emoji': topic_emoji,
                        '_id': topic_uid,
                    },
                ],
            },
        )

    def remove_topics(
            self,
            room_id: str,
            topics_ids: list[str],
    ) -> Response:
        """Удаление топиков из супегруппы.

        :param room_id: uid комнаты
        :param topics_ids: uid топиков

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.removeTopics',
            payload={
                'roomId': room_id,
                'topicIds': topics_ids,
            },
        )

    @decorator_service.paginate
    def get_topics(
            self,
            spg_id: str,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Response:
        """Список топиков в суппергруппе.

        :param spg_id: uid супергруппы
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.topics',
            params={
                'roomId': spg_id,
                'offset': offset,
                'count': count,
            },
            method='get',
        )

    def edit_topic(
            self,
            topic_id: str,
            new_topic_name: Optional[str] = None,
            new_topic_emoji: Optional[str] = None,
    ) -> Response:
        """Изменение топика в супегруппе.

        :param topic_id: uid топика
        :param new_topic_name: новое название топика
        :param new_topic_emoji: код нового эмодзи топика

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.editTopics',
            payload={
                'topics': [
                    {
                        '_id': topic_id,
                        'fname': new_topic_name,
                        'emoji': new_topic_emoji,
                    },
                ],
            },
        )

    def invite(
            self,
            room_id: str,
            user_ids: list[str],
    ) -> Response:
        """Пригласить в супергруппу.

        :param room_id: uid супергруппы
        :param user_ids: uid пользователей которых следует пригласить

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.invite',
            payload={
                'roomId': room_id,
                'userIds': user_ids,
            },
        )

    def set_avatar(self, sgp_id: str, file_path: Path) -> Response:
        return self._upload_file_base(
            endpoint='supergroups.setAvatar',
            room_id=sgp_id,
            path=file_path,
            text=None,
        )

    def rename_supergroup(self, sgp_id: str, new_name: str) -> Response:
        """Переименование супегруппы.

        :param sgp_id: uid супегруппы
        :param new_name: новое название супергруппы

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.rename',
            payload={
                'roomId': sgp_id,
                'name': new_name,
            },
        )

    def add_owner(self, sgp_id: str, user_id: str) -> Response:
        """Добавить владельца в супергруппу.

        :param sgp_id: uid супергруппы
        :param user_id: uid пользователя которого следует сделать владельцем

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.addOwner',
            payload={
                'roomId': sgp_id,
                'userId': user_id,
            },
        )

    def remove_owner(self, sgp_id: str, user_id: str) -> Response:
        """Удалить владельца в супегруппе.

        :param sgp_id: uid супергруппы
        :param user_id: uid пользователя у которого следует забрать роль
         владельца

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.removeOwner',
            payload={
                'roomId': sgp_id,
                'userId': user_id,
            },
        )

    def convert_supergroup_to_group(self, sgp_id: str) -> Response:
        """Конвертироват супергруппу в группу.

        :param sgp_id: uid супергруппы

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.convertToGroup',
            payload={
                'roomId': sgp_id,
            },
        )

    def pin_topic(
            self,
            room_id: str,
            topic_id: str,
            pin_after_id: Optional[str] = None,
            pin_before_id: Optional[str] = None,
    ) -> Response:
        """Закрепить топик в супергруппе.

        :param room_id: uid супергруппы
        :param topic_id: uid топика
        :param pin_after_id: uid топика после которого закреплять
        :param pin_before_id: uid топика перед каким закреплять

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.pinTopic',
            payload={
                'roomId': room_id,
                'topicId': topic_id,
                'pinAfter': pin_after_id,
                'pinBefore': pin_before_id,
            },
        )

    def set_pinned_topics(self, spg_id: str, pinned: list[str]) -> Response:
        """Предположительно закрепление топиков по порядку через {pinned}.
        (pageId=160147670)

        :param spg_id: uid супегруппы
        :param pinned: список uid топиков, по которым будем закреплять

        :return: requests.Response
        """
        return self._make_request(
            endpoint='supergroups.setPinnedTopics',
            payload={
                'roomId': spg_id,
                'pinned': pinned,
            },
        )
