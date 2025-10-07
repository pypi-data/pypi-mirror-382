from typing import Optional

from requests import Response

from .lib import Base
from ..types.folders import FolderTypes
from ..types.rooms import RoomTypes


class Folders(Base):

    def folders_list(
            self,
            folder_types: Optional[tuple[FolderTypes]] = (
                    FolderTypes.ALL,
                    FolderTypes.CUSTOM,
                    FolderTypes.DIRECTS,
                    FolderTypes.GROUPS,
                    FolderTypes.HIDDEN,
                    FolderTypes.SECURITY_USER,
            ),
    ) -> Response:
        """Получение списка папок.

        :param folder_types: типы папок

        :return: requests.Response
        """
        return self._make_request(
            endpoint='folders.list',
            params={
                'types[]': list(folder_types),
            },
            method='get',
        )

    def create(
            self,
            name: str,
            rooms_ids: Optional[list[str]] = None,
            room_types: Optional[list[RoomTypes]] = [],
    ) -> Response:
        """Создание папки.

        :param name: название папки
        :param rooms_ids: uid комнат
        :param room_types: группировка по типу комнат

        :return:
        """
        return self._make_request(
            endpoint='folders.create',
            payload={
                'folderName': name,
                'rooms': rooms_ids,
                'roomTypes': room_types,
            })

    def add_room(
            self,
            folder_id: str,
            room_id: Optional[str] = None,
            room_ids: Optional[list[str]] = None,
    ) -> Response:
        """Добавление комнат в папку.

        :param folder_id: uid папки
        :param room_id: uid комнаты
        :param room_ids: uid комнат

        :return: requests.Response
        """
        return self._make_request(
            endpoint='folders.addRoom',
            payload={
                'folderId': folder_id,
                'roomId': room_id,
                'roomIds': room_ids,
            })

    def remove_room(
            self,
            folder_id: str,
            room_id: Optional[str] = None,
            room_ids: Optional[list[str]] = None,
    ) -> Response:
        """Удаление комнат из папок.

        :param folder_id: uid папки
        :param room_id: uid комнаты
        :param room_ids: uid комнат

        :return: requests.Response
        """
        return self._make_request(
            endpoint='folders.removeRoom',
            payload={
                'folderId': folder_id,
                'roomId': room_id,
                'roomIds': room_ids,
            })

    def add_pinned_room(
            self,
            folder_id: str,
            room_ids: list[str],
            update_time: Optional[int] = None,
    ) -> Response:
        """Добавление закрепленных комнат в папку.

        :param folder_id: uid папки
        :param room_ids: uid комнат
        :param update_time: время обновления (timestamp)

        :return: requests.Response
        """
        return self._make_request(
            endpoint='folders.savePinnedRooms',
            payload={
                'folderId': folder_id,
                'pinnedRoomIds': room_ids,
                'pinnedRoomIdsUpdatedAt': update_time,
            })

    def update(
            self,
            folder_id: str,
            name: Optional[str] = None,
            room_types: Optional[list[RoomTypes]] = None,
            new_room_ids: Optional[list[str]] = None,
    ) -> Response:
        """Обновление папки.

        :param folder_id:  uid папки
        :param name: новое название папки
        :param room_types: группировка комнат по типу
        :param new_room_ids: uid новых комнат

        :return: request.Response
        """
        return self._make_request(
            endpoint='folders.update',
            payload={
                'folderId': folder_id,
                'folderName': name,
                'roomTypes': room_types,
                'newRooms': new_room_ids,
            })

    def remove(self, folder_id: str) -> Response:
        """Удаление папки.

        :param folder_id: uid папки

        :return: requests.Response
        """
        return self._make_request(
            endpoint='folders.remove',
            payload={
                'folderId': folder_id,
            },
        )
