from enum import StrEnum


class SpotlightSchemas(StrEnum):
    """Типы доступных целей поиска в Spotlight."""

    ALL_USERS = 'users'
    UNKNOWN_USERS = 'unknown-users'
    DIRECT = 'rooms-d'
    PRIVATE = 'rooms-p'
    TELECONFERENCE = 'rooms-tc'
    SUPERGROUP = 'rooms-s'
    TOPIC = 'rooms-t'
    THREAD_ROOM = 'rooms-thread'
    GROUPS = 'groups'
    MESSAGES = 'messages'


class SpotlightPaginatedSchemas(StrEnum):
    """Типы доступных целей поиска в Spotlight paginated."""

    ROOMS = 'rooms'
    USERS = 'users'
