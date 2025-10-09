import threading
from contextlib import contextmanager
from typing import Generator

from ..commands import RoverCommands
from ..communicators import GRPCCommunicator
from ..generated import RCChannelsCommand, CommandAck, TelemetryData, BatteryData


class RoverClient:
    """
    Синхронный клиент для управления роботом
    """

    def __init__(self, host: str = "10.1.100.160", port: int = 5656):
        self._communicator = GRPCCommunicator(host, port)
        self._is_rc_streaming = False
        self._rc_stream_thread = None
        self._rc_stream_interval = 0.1  # 10 Hz
        self.rc_channels = RCChannelsCommand(
            channel1=1500,
            channel2=1500,
            channel3=1500,
            channel4=1500
        )
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

    def connect(self) -> bool:
        """
        Подключение к роботу
        """
        return self._communicator.connect()

    def disconnect(self):
        """
        Отключение от робота
        """
        self._communicator.disconnect()

    @property
    def is_connected(self) -> bool:
        """
        Статус подключения робота
        """
        return self._communicator.is_connected

    @property
    def is_rc_streaming(self) -> bool:
        """
        Статус потоковой передачи RC-команд
        """
        return self._is_rc_streaming

    def set_velocity(self, linear: float, angular: float) -> CommandAck:
        """
        Установка линейной и угловой скорости робота

        :param linear: Линейная скорость
        :type linear: float
        :param angular: Угловая скорость
        :type angular: float
        :return: Результат выполнения команды
        :rtype: CommandResult
        """
        return self._communicator.send_command(
            RoverCommands.SET_VELOCITY,
            linear=linear,
            angular=angular
        )

    def set_differential_speed(self, left: float, right: float) -> CommandAck:
        """
        Дифференциальное управление скоростями левого и правого колес.

        :param left: Скорость левого колеса в м/с.
                     Положительные значения - вперед,
                     отрицательные - назад
        :type left: float
        :param right: Скорость правого колеса в м/с.
                      Положительные значения - вперед,
                      отрицательные - назад
        :type right: float
        :return: Результат выполнения команды
        :rtype: CommandResult
        """
        return self._communicator.send_command(
            RoverCommands.SET_DIFF_SPEED,
            left=left,
            right=right
        )

    def get_telemetry(self) -> TelemetryData:
        """
        Получение телеметрии робота

        :return: Данные телеметрии робота
        :rtype: Telemetry
        """
        return self._communicator.get_telemetry()

    def get_battery_status(self) -> BatteryData:
        """
        Получение заряда батареи

        :return: Заряд батареи в процентах
        :rtype: int
        """
        return self._communicator.get_battery_status()

    def moo(self) -> CommandAck:
        """
        Воспроизведение звука "мычания"
        """
        return self._communicator.send_command(RoverCommands.MOO)

    def beep(self) -> CommandAck:
        """
        Воспроизведение звукового сигнала
        """
        return self._communicator.send_command(RoverCommands.BEEP)

    def goto(self, x: float, y: float, yaw: float | None = None):
        """
        Перемещение робота в заданную точку.

        :param x: Координата X целевой точки
        :type x: float
        :param y: Координата Y целевой точки
        :type y: float
        :param yaw: Угол поворота в целевой точке (радианы)
        :type yaw: float | None
        """
        self._communicator.goto(x=x, y=y, yaw=yaw)

    def stop(self) -> CommandAck:
        """
        Остановка
        """
        return self._communicator.send_command(RoverCommands.STOP)

    def emergency_stop(self) -> CommandAck:
        """
        Аварийная остановка
        """
        return self._communicator.send_command(RoverCommands.EMERGENCY_STOP)

    def stream_telemetry(self) -> Generator[TelemetryData]:
        """
        Потоковое получение телеметрии

        :return: Генератор данных телеметрии
        :rtype: Generator[TelemetryData]

        :Example:
            .. code-block:: python

                for telemetry in rover.stream_telemetry():
                    print(f"Position: {telemetry.position.x}, {telemetry.position.y}")
        """
        for data in self._communicator.stream_telemetry():
            yield data

    @contextmanager
    def rc_stream_context(self):
        """
        Контекстный менеджер для потоковой передачи RC-каналов.
        """
        try:
            self.start_rc_stream()
            yield self.rc_channels
        finally:
            self.stop_rc_stream()

    def start_rc_stream(self):
        """
        Запуск потоковой передачи RC-команд в отдельном потоке
        """
        with self._lock:
            if self._is_rc_streaming:
                return

            self._is_rc_streaming = True
            self._stop_event.clear()
            self._rc_stream_thread = threading.Thread(
                target=self._rc_stream_loop,
                daemon=True
            )
            self._rc_stream_thread.start()

    def stop_rc_stream(self):
        """
        Остановка потока RC команд
        """
        with self._lock:
            self._is_rc_streaming = False
            self._stop_event.set()

            if self._rc_stream_thread:
                self._rc_stream_thread.join(timeout=2.0)
                if self._rc_stream_thread.is_alive():
                    print("Warning: RC stream thread didn't stop gracefully")
                self._rc_stream_thread = None

            self._reset_rc_channels()

    def _reset_rc_channels(self):
        """
        Сбрасывает RC каналы в нейтральное положение
        """
        self.rc_channels.channel1 = 1500
        self.rc_channels.channel2 = 1500
        self.rc_channels.channel3 = 1500
        self.rc_channels.channel4 = 1500

    def _rc_stream_loop(self):
        """
        Основной цикл отправки RC команд
        """
        try:
            while not self._stop_event.is_set() and self._is_rc_streaming:
                try:
                    ack = self._communicator.stub.stream_rc_channels(self.rc_channels)
                    if not ack.success:
                        print(f"RC command failed: {ack.message}")

                except Exception as e:
                    print(f"RC stream error: {e}")
                    break

                self._stop_event.wait(self._rc_stream_interval)

        except Exception as e:
            print(f"RC stream loop error: {e}")
        finally:
            with self._lock:
                self._is_rc_streaming = False


    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()