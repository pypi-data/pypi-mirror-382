from enum import StrEnum


class AttachmentsType(StrEnum):
    """Типы вложенний для поиска."""

    SPEECH = 'speech'
    AUDIO = 'audio'
    IMAGE = 'image'
    VIDEO = 'video'
    OTHER = 'other'
