import json
import uuid
from pathlib import Path
from typing import List, Literal, Optional

from requests import Response

from .lib import Base
from ..const import ecss_const
from ..types.rooms import (RoomSaveSettings, RoomSyncShowType,
                           RoomTypes)
from ..utils.decorators import decorator_service


class Rooms(Base):

    @decorator_service.paginate
    def members(
            self,
            room_id: str,
            count: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Response:
        """Участники комнаты.

        :param room_id: uid комнаты
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.members',
            params={
                'roomId': room_id,
                'count': count,
                'offset': offset,

            },
            method='get',
        )

    @decorator_service.paginate
    def room_sync_preview(
            self,
            hidden_rooms: Optional[
                Literal
                [
                    RoomSyncShowType.HIDDEN,
                    RoomSyncShowType.ALL,
                    RoomSyncShowType.ONLY_OPEN,
                ]
            ] = RoomSyncShowType.ALL,
            room_types: list[RoomTypes] = [ # noqa
                RoomTypes.DIRECT,
                RoomTypes.PRIVATE,
                RoomTypes.TELECONFERENCE,
            ],
            alerted_only: bool = False,
            updated_since: int = 0,
            sort_lm: int = 1,
            sort_pinned: int = 1,
            folder_id: str = 'all',
            exclude: list[str] = [], # noqa
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Response:
        """Актуальный список комнат пользователя(Блок Preview).

        :param hidden_rooms: показывать ли скрытые комнаты
        :param room_types: типы комнат
        :param alerted_only: только комнаты в которых есть упоминание
        :param updated_since: обновленные с этой даты
        :param sort_lm: правило сортировки по дате последнего сообщения
        :param sort_pinned: правило сортировки по закреплению
        :param folder_id: показывать комнаты пренадлежащие папке (uid или all)
        :param exclude: uid комнат которые надо исключить из выборки
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.sync',
            payload={
                'preview': {
                    'hidenRooms': hidden_rooms,
                    'roomTypes': room_types,
                    'alertedOnly': alerted_only,
                    'updatedSince': updated_since,
                    'sortlm': sort_lm,
                    'sortstarred': sort_pinned,
                    'offset': offset,
                    'count': count,
                    'except': exclude,
                    'folderId': folder_id,
                },
            })

    @decorator_service.paginate
    def room_sync_list(
            self,
            hidden_rooms: Optional[
                Literal
                [
                    RoomSyncShowType.HIDDEN,
                    RoomSyncShowType.ALL,
                    RoomSyncShowType.ONLY_OPEN,
                ]
            ] = RoomSyncShowType.ALL,
            alerted_only: bool = False,
            folder_id: str = '',
            exclude: List[Optional[str]] = [], # noqa
            room_type: List[RoomTypes] = [ # noqa
                RoomTypes.DIRECT,
                RoomTypes.PRIVATE,
                RoomTypes.TELECONFERENCE,
                RoomTypes.SUPERGROUP,
            ],
            required: Optional[list[str]] = [],
            count: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Response:
        """Актуальный список комнат пользователя(Блок List).

        :param hidden_rooms: показывать ли скрытые комнаты
        :param alerted_only: только комнаты в которых есть упоминание
        :param folder_id: показывать комнаты пренадлежащие папке по uid
        :param exclude: uid комнат которые надо исключить из выборки
        :param room_type: типы комнат
        :param required: uid закрепленных комнат
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.sync',
            payload={
                'list': {
                    'hiddenRooms': hidden_rooms,
                    'alertedOnly': alerted_only,
                    'offset': offset,
                    'count': count,
                    'except': exclude,
                    'folderId': folder_id,
                    'roomTypes': room_type,
                },
                'required': {
                    'byIds': required,
                },
                'removed': {},
            },
        )

    def room_sync_required(
            self,
            req: str,
            objects: List[str] = [],
    ) -> Response:
        """Актуальный список комнат пользователя(Блок required).

        :param req: параметр поиска
        :param objects: значение параметра поиска
        :return:
        """
        req_data = ecss_const.ROOM_SYNC_CONST.REQ_DATA.get(req)
        if len(objects) > 0:
            req_data[req] = objects
            payload = {'required': req_data}
        else:
            payload = {'required': req_data}
        return self._make_request('rooms.sync', payload=payload)

    def room_sync_alerts(
            self,
            updated_date: Optional[int] = 0,
    ) -> Response:
        """Я не понял(pageId=98699168)(Блок alerts).

        :param updated_date: дата обновления комнат(timestamp)

        :return: requests.Response
        """
        return self._make_request(
            'rooms.sync',
            payload={
                'alerts':
                {
                    'updatedSince': updated_date,
                },
            },
        )

    def room_sync_alerted_rooms(
            self,
            alerts_count: Optional[bool] = True,
    ) -> Response:
        """Количество комнат в которых есть непрочитанные(блок alerts).

        :param alerts_count: посчитать ли суммарное колво комнат

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.sync',
            payload={
                'alertedRooms':
                {
                    'total': alerts_count,
                },
            },
        )

    @decorator_service.paginate
    def room_sync_removed(
            self,
            delete_since: Optional[int] = 0,
            count: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Response:
        """Cобытия об удалении из комнат(блок removed).

        :param delete_since: с какой даты фильтровать
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.sync',
            payload={
                'removed': {
                    'deletedSince': delete_since,
                    'offset': offset,
                    'count': count,
                },
            },
        )

    def info(self, room_id: str) -> Response:
        """Информация о группе.

        :param room_id: uid группы

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.info',
            params={
                'roomId': room_id,
            },
            method='get',
        )

    def invite_to_many(
            self,
            room_ids: list[str],
            user_ids: list[str],
    ) -> Response:
        """Пригласить много пользователей в группы.

        :param room_ids: uid комнат
        :param user_ids: uid пользователей

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.inviteToMany',
            payload={
                'roomIds': room_ids,
                'userIds': user_ids,
            },
        )

    def leave(self, room_id: str) -> Response:
        """Покинуть комнату.

        :param room_id: uid комнаты

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.leave',
            payload={
                'roomId': room_id,
            },
        )

    def set_room_notifications(
            self,
            room_id: str,
            mute: Optional[bool] = False,
    ) -> Response:
        """Персональная настройка оповещений в комнате.

        :param room_id: uid комнаты
        :param mute: заглушить?

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.setNotifications',
            payload={
                'roomId': room_id,
                'mute': mute,
            },
        )

    @decorator_service.paginate
    def current_user_rooms(
            self,
            query: Optional[str] = None,
            count: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Response:
        """Поиск комнат с наличием {query} пользователя.

        :param query: пользователь для фильтрации
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.myRoomsWithOtherUser',
            params={
                'userId': self.client.session.uid,
                'query': query,
                'offset': offset,
                'count': count,
            },
            method='get',
        )

    @decorator_service.paginate
    def search_in_my_rooms(
            self,
            folder_id: Optional[str] = None,
            exclude_folder_id: Optional[str] = None,
            query: Optional[str] = None,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Response:
        """Метод поиска комнат в папках(вроде).

        :param folder_id: uid папки
        :param exclude_folder_id: uid папки которую следует исключить
        :param query: фильтрация с помощью названия комнаты
        :param offset: количество пропускаемых сообщений
        :param count: максимальное количество сообщений

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.searchInMyRooms',
            params={
                'folderId': folder_id,
                'excludeFolderId': exclude_folder_id,
                'query': query,
                'offset': offset,
                'count': count,
            },
            method='get',
        )

    def change_settings(
            self,
            room_id: str,
            setting_type: Literal[
                RoomSaveSettings.CHANGE_READ_ONLY,
                RoomSaveSettings.CHANGE_AVATAR,
                RoomSaveSettings.CHANGE_NAME,
                RoomSaveSettings.CHANGE_TYPE,
                RoomSaveSettings.ADD_USERS,
                RoomSaveSettings.REMOVE_USERS,
            ],
            setting_value: str | RoomTypes | list[str],
    ) -> Response:
        """Изменение настроек комнаты.

        :param room_id: uid комнаты
        :param setting_type: Тип настройки
        :param setting_value: Значение настройки

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.saveRoomSettings',
            payload={
                'rid': room_id,
                setting_type: setting_value,
            },
        )

    def pin(
            self,
            folder_id: str,
            room_id: str,
            position: Optional[int] = 0,
    ) -> Response:
        """Закрепление комнаты в папке.

        :param folder_id: uid папки
        :param room_id: uid комнаты
        :param position: позиция для закрепления (0 самая первая)

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.pin',
            payload={
                'folderId': folder_id,
                'roomId': room_id,
                'position': position,
            },
        )

    def unpin(self, folder_id: str, room_id: str) -> Response:
        """Открепить комнату в папке.

        :param folder_id: uid папки
        :param room_id: uid комнаты

        :return: requests.Response
        """
        return self._make_request(
            endpoint='rooms.unpin',
            payload={
                'folderId': folder_id,
                'roomId': room_id,
            },
        )

    def upload_file(
            self,
            room_id: str,
            file_path: Path,
            text: Optional[str] = None,
            duration: Optional[int] = None,
    ) -> Response:
        """Загрузка файла в комнату.

        :param room_id: uid комнаты
        :param file_path: путь до файла
        :param text: текст сообщения
        :param duration: длительность видео

        :return: requests.Response
        """
        if duration:
            duration_data = {f'metadata_video_duration_{file_path}': duration}
        else:
            duration_data = None
        return self._upload_file_base(
            endpoint='rooms.upload',
            room_id=room_id,
            path=file_path,
            text=text,
            extra_data=duration_data,
        )

    def upload_speech(
            self,
            room_id: str,
            file_path: Path,
            waveform: dict,
            text: Optional[str] = None,
            reply_id: Optional[str] = None,
    ) -> Response:
        """Загрузить голосвое сообщение.

        :param room_id: uid комнаты
        :param text: текст сообщения
        :param file_path: путь до файла
        :param waveform: волноформа
        :param reply_id: uid сообщение на которое отвечаем

        :return: requests.Response
        """
        extra_data = {
            '_id': str(uuid.uuid4()),
            'waveform': json.dumps(waveform),
        }
        if reply_id:
            extra_data['toReplyId'] = reply_id
        return self._upload_file_base(
            endpoint='rooms.uploadSpeech',
            room_id=room_id,
            path=file_path,
            text=text,
            extra_data=extra_data,
        )
