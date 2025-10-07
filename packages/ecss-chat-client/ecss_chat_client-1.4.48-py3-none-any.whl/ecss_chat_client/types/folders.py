from enum import StrEnum


class FolderTypes(StrEnum):
    """Типы папкок в чате."""

    GROUPS = 'g'
    DIRECTS = 'd'
    HIDDEN = 'h'
    ALL = 'a'
    CUSTOM = 'c'
    UNREAD = 'u'  # /pages/viewpage.action?pageId=130365575
    SECURITY_USER = 's'
