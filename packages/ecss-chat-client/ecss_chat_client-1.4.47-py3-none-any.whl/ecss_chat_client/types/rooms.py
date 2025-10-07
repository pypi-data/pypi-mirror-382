from enum import StrEnum


class RoomTypes(StrEnum):
    """Типы комнат в чате."""

    DIRECT = 'd'
    PRIVATE = 'p'
    TELECONFERENCE = 'tc'
    SUPERGROUP = 's'
    TOPIC = 't'
    THREAD_ROOM = 'thread'


class RoomSyncShowType(StrEnum):
    """Типы показа комнат в синхронизации комнат."""

    ONLY_OPEN = 'except'
    HIDDEN = 'only'
    ALL = 'include'


class RoomSettings(StrEnum):
    """Настройки комнаты."""

    ACTIVATE_READ_ONLY = 'ro'
    ACTIVATE_IS_CHANNEL = 'isChannel'
    ACTIVATE_REACTION = 'react'


class RoomSaveSettings(StrEnum):

    CHANGE_READ_ONLY = 'readOnly'
    CHANGE_IS_CHANNEL = 'isChannel'
    CHANGE_AVATAR = 'roomAvatar'
    CHANGE_NAME = 'roomName'
    CHANGE_TYPE = 'roomType'
    ADD_USERS = 'addUsers'
    REMOVE_USERS = 'removeUsers'
