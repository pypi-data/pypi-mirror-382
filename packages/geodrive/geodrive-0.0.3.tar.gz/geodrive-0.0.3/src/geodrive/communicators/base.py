from abc import ABC, abstractmethod

from ..commands import RoverCommands
from ..generated import CommandAck


class BaseCommunicator(ABC):
    """Базовый класс для всех коммуникаторов"""

    def __init__(self):
        self.stub = None
    
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def send_command(self, command: RoverCommands, **kwargs) -> CommandAck:
        pass

    @abstractmethod
    def stream_telemetry(self):
        pass

    @abstractmethod
    def get_telemetry(self):
        pass

    @abstractmethod
    def get_battery_status(self):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def goto(self, **kwargs):
        pass

    @abstractmethod
    def goto_stream_position(self, **kwargs):
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        pass