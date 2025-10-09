import time
from typing import Generator

import grpc

from ..commands import RoverCommands
from .base import BaseCommunicator
from ..generated import (
    RoverServiceStub,
    DifferentialCommand,
    LedCustomCommand,
    VelocityCommand,
    TelemetryData,
    GotoProgress,
    GotoCommand,
    BatteryData,
    RoverStatus,
    LedCommand,
    CommandAck,
    GotoAck,
    Empty
)



class GRPCCommunicator(BaseCommunicator):
    """
    Синхронный gRPC коммуникатор
    """

    def __init__(self, host: str = "localhost", port: int = 5656):
        super().__init__()
        self.host: str = host
        self.port: int = port
        self.channel: grpc.Channel | None = None
        self.stub: RoverServiceStub | None = None
        self._is_connected: bool = False

    @property
    def is_connected(self) -> bool:
        """
        Проверить подключение к роботу.

        :return: True если подключение активно
        :rtype: bool
        """
        return self._is_connected

    def _check_connection(self):
        """
        Проверка соединения
        """
        request = Empty()
        self.stub.get_status(request)

    def connect(self) -> bool:
        """
        Установка синхронного соединения
        """
        try:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            self.stub = RoverServiceStub(self.channel)

            start_time = time.time()
            while time.time() - start_time < 5.0:
                try:
                    self._check_connection()
                    self._is_connected = True
                    return True
                except grpc.RpcError:
                    time.sleep(0.1)

            return False

        except Exception:
            self.disconnect()
            return False

    def disconnect(self):
        """
        Закрытие соединения
        """
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None
            self._is_connected = False

    def send_command(self, command: RoverCommands, **kwargs) -> CommandAck:
        """
        Отправка команды
        """
        request = Empty()

        match command:
            case RoverCommands.SET_VELOCITY:
                request = VelocityCommand(**kwargs)
                response = self.stub.set_velocity(request)
            case RoverCommands.SET_DIFF_SPEED:
                request = DifferentialCommand(**kwargs)
                response = self.stub.set_differential_speed(request)
            case RoverCommands.LED_CONTROL:
                request = LedCommand(**kwargs)
                response = self.stub.led_control(request)
            case RoverCommands.LED_CUSTOM:
                request = LedCustomCommand(**kwargs)
                response = self.stub.led_custom(request)
            case RoverCommands.STOP:
                response = self.stub.stop(request)
            case RoverCommands.EMERGENCY_STOP:
                response = self.stub.emergency_stop(request)
            case RoverCommands.GOTO_CANCEL:
                response = self.stub.goto_cancel(request)
            case RoverCommands.BEEP:
                response = self.stub.beep(request)
            case RoverCommands.MOO:
                response = self.stub.moo(request)
            case _:
                response = CommandAck(
                    success=False,
                    message=f"Unknown command: {command}"
                )

        return response

    def get_status(self) -> RoverStatus:
        """
        Получение статуса
        """
        request = Empty()
        response = self.stub.get_status(request)
        return response

    def get_battery_status(self) -> BatteryData:
        """
        Получение напряжения
        """
        request = Empty()
        response: BatteryData = self.stub.get_battery_status(request)
        return response

    def get_telemetry(self) -> TelemetryData:
        """
        Получение телеметрии
        """
        request = Empty()
        response = self.stub.get_telemetry(request)
        return response

    def stream_telemetry(self) -> Generator[TelemetryData]:
        """
        Получить поток телеметрии в реальном времени.

        :return: Генератор объектов TelemetryData
        :rtype: Generator[TelemetryData]
        """
        request = Empty()
        for response in self.stub.stream_telemetry(request):
            yield response

    def goto(
            self,
            x: float,
            y: float,
            yaw: float | None=None
    ) -> GotoAck:
        """
        Движение к указанно точке

        :param x: Целевая координата X в метрах
        :type x: float
        :param y: Целевая координата Y в метрах
        :type y: float
        :param yaw: Опциональный целевой курс в радианах
        """
        request = GotoCommand(target_x=x, target_y=y, target_yaw=yaw)
        response = self.stub.goto(request)
        return response

    def goto_stream_position(
            self,
            x: float,
            y: float,
            yaw: float | None=None
    ) -> Generator[GotoProgress]:
        """
        Выполнить движение к точке с потоковой передачей прогресса.

        Возвращает генератор, который возвращает объекты прогресса движения
        в реальном времени. Позволяет отслеживать выполнение операции

        :param x: Целевая координата X в метрах
        :type x: float
        :param y: Целевая координата Y в метрах
        :type y: float
        :param yaw: Опциональный целевой курс в радианах
        """
        command = GotoCommand(target_x=x, target_y=y)
        if yaw is not None:
            command.target_yaw = yaw
        progress_stream = self.stub.goto_stream_position(command)

        for progress in progress_stream:
            yield progress
