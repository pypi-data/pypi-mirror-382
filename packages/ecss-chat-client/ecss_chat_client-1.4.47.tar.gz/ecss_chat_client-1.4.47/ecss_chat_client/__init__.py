"""ECSS Chat Client - Python клиент для ECSS Chat."""
from .services.auth import Auth, AuthBot
from .services.avatar import Avatars
from .services.bots import Bots
from .services.config import Settings
from .services.directs import Directs
from .services.folders import Folders
from .services.groups import Groups
from .services.info import ApiInfo
from .services.messages import Messages
from .services.polls import Polls
from .services.preferences import UserPreferences
from .services.rooms import Rooms
from .services.server import ServerSettings
from .services.spotlight import Spotlight
from .services.supergroups import SuperGroups
from .services.testing import Testing
from .services.threads import Threads
from .services.tus import TusService
from .services.users import Users


class Client:
    def __init__(
            self,
            server,
            username,
            password,
            port='3443',
            proto='https',
            verify=True,
    ):
        self.username = username
        self.password = password
        self.port = port
        self.proto = proto
        self.verify = verify
        self.server = server
        self.base_url = f'{proto}://{server}:{port}/api/v1'
        self.short_url = f'{proto}://{server}:{port}/api'
        self.__websocket_url = f'wss://{server}:{port}/websocket'

        self.settings = Settings(
            server, config_file='settings.ini',
        )

        self.session = Auth.session(
            username,
            password,
            server,
            proto,
            port,
            verify,
        )
        self.avatars = Avatars(self)
        self.directs = Directs(self)
        self.groups = Groups(self)
        self.polls = Polls(self)
        self.rooms = Rooms(self)
        self.supergroups = SuperGroups(self)
        self.folders = Folders(self)
        self.users = Users(self)
        self.preferences = UserPreferences(self)
        self.messages = Messages(self)
        self.threds = Threads(self)
        self.testing = Testing(self)
        self.spotlight = Spotlight(self)
        self.tus = TusService(self)
        self.api_info = ApiInfo(self)
        self.server_settings = ServerSettings(self)
        self.bots = Bots(self)


class BotClient(Client):
    def __init__(
            self,
            server,
            token,
            port='3443',
            proto='https',
            verify=True,
    ):
        self.token = token
        self.port = port
        self.proto = proto
        self.verify = verify
        self.server = server
        self.base_url = f'{proto}://{server}:{port}/api/v1'
        self.short_url = f'{proto}://{server}:{port}/api'
        self.__websocket_url = f'wss://{server}:{port}/websocket'

        self.settings = Settings(
            server, config_file='settings.ini',
        )

        self.session = AuthBot.session(
            token,
        )
        self.avatars = Avatars(self)
        self.directs = Directs(self)
        self.groups = Groups(self)
        self.polls = Polls(self)
        self.rooms = Rooms(self)
        self.supergroups = SuperGroups(self)
        self.folders = Folders(self)
        self.users = Users(self)
        self.preferences = UserPreferences(self)
        self.messages = Messages(self)
        self.threds = Threads(self)
        self.testing = Testing(self)
        self.spotlight = Spotlight(self)
        self.tus = TusService(self)
        self.api_info = ApiInfo(self)
        self.server_settings = ServerSettings(self)
        self.bots = Bots(self)


__all__ = ['Client']
__version__ = '1.4.47'
__author__ = 'Eltex SC VoIP'
__description__ = 'ElphChat API Client Library'
