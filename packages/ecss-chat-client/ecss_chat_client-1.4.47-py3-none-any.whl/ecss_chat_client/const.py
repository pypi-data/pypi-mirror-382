from dataclasses import dataclass


class RoomSyncConst:
    """Блоки для RoomSync."""

    REQ_DATA = {
        'saved': {
            'saved': True,
        },
        'support': {
            'support': True,
        },
        'byIds': {
            'byIds': None,
        },
        'byRoomName': {
            'byRoomName': None,
        },
    }


@dataclass
class Const:
    """Константы."""

    ROOM_SYNC_CONST: RoomSyncConst = RoomSyncConst()


ecss_const = Const()
