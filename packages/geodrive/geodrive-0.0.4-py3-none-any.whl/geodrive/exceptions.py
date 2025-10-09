class RoverCommunicationError(Exception):
    """Базовое исключение для ошибок коммуникации"""
    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class RoverConnectionError(RoverCommunicationError):
    """Ошибки подключения"""
    pass

class RoverCommandError(RoverCommunicationError):
    """Ошибки выполнения команд"""
    pass

class RoverTimeoutError(RoverCommunicationError):
    """Таймауты операций"""
    pass

class RoverStreamError(RoverCommunicationError):
    """Ошибки потоковой передачи"""
    pass

class RCStreamError(RoverStreamError):
    """Ошибки RC потока"""
    pass

class TelemetryStreamError(RoverStreamError):
    """Ошибки потока телеметрии"""
    pass

class InvalidCommandError(RoverCommandError):
    """Некорректная команда"""
    pass

class RoverNotConnectedError(RoverConnectionError):
    """Операция требует подключения"""
    pass