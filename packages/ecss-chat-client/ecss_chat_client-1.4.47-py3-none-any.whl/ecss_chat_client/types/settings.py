from dataclasses import dataclass
from enum import StrEnum


class ClientControlSettings(StrEnum):
    """Настройки кэширования и токенов."""

    CACHE_COUNTER = 'ClientControl_ClearCacheCounter'
    AUTH_TOKEN_EXPIRATION = 'ClientControl_InvalidateAuthTokenDate'


class SecurityUserSettings(StrEnum):
    """Настройки security user."""

    ACTIVATE = 'Security_User'
    PASSWORD = 'Security_User_Password'


class FileSettings(StrEnum):
    """Настройки работы с файлами."""

    ACTIVATE = 'FileUpload_Enabled'
    SIZE = 'FileUpload_MaxFileSize'
    AVATAR_SIZE = 'FileUpload_MaxGroupAvatarSize'
    MEDIA_ALLOWED_TYPES = 'FileUpload_MediaTypeWhiteList'
    MEDIA_RESTRICTED_TYPES = 'FileUpload_MediaTypeBlackList'


class FoldersSettings(StrEnum):
    """Настройки папок."""

    FOLDER_LIMIT = 'UserFolderLimit'
    ROOM_IN_FOLDER_LIMIT = 'RoomInFoldersLimit'
    PINNED_ROOM_IN_FOLDER_LIMIT = 'PinRoomsInFolderLimit'


class MessageSettings(StrEnum):
    """Настройки сообщений."""

    FORWARD_LIMIT = 'ForwardLimit'
    ACTIVATE_MULTIPLE_REACTION = 'AllowMultipleReactions'
    ACTIVATE_SHORTENING_URL = 'Message_autolink_enabled'
    SHORTENING_URL_LIST = 'Message_autolink_domains'
    ACTIVATE_NUMBER_TO_URL = 'Message_local_number_enabled'
    REGEX_SEARCH_NUMBER = 'Message_local_number_regexp'


class MobileSettings(StrEnum):
    """Настройки для мобильных клиентов."""

    ANDROID = 'platform_Android'
    IOS = 'platform_iOS'


@dataclass
class ServerSettingsType:
    """Типы настроек сервера."""

    FILES = FileSettings
    FOLDERS = FoldersSettings
    MESSAGES = MessageSettings
    MOBILE = MobileSettings
    SECURITY_USER = SecurityUserSettings
    CLIENT = ClientControlSettings


server_settings_type = ServerSettingsType()
