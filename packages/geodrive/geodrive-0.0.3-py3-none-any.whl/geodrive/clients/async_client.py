import asyncio
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from ..commands import RoverCommands
from ..generated import RCChannelsCommand, CommandAck, TelemetryData, BatteryData
from ..communicators import AsyncGRPCCommunicator
from ..logging import get_logger


class AsyncRoverClient:
    """
    Асинхронный клиент для управления ровером
    """

    def __init__(self, host: str = "localhost", port: int = 5656, logging: bool = False):
        self._communicator = AsyncGRPCCommunicator(host, port)
        self._is_rc_streaming: bool = False
        self._rc_stream_task = None
        self._rc_stream_interval: float = 0.05
        self._logger = get_logger()
        self.rc_channels = RCChannelsCommand(
            channel1=1500,
            channel2=1500,
            channel3=1500,
            channel4=1500
        )

    async def connect(self) -> bool:
        """
        Подключение к роботу
        """
        self._logger.info("connecting to rover...")
        result = await self._communicator.connect()

        if result:
            self._logger.info("rover connected successfully!")
        else:
            self._logger.error("rover connection failed!")

        return result

    async def disconnect(self):
        """
        Отключение от робота
        """
        self._logger.info("disconnecting from rover...")
        await self._communicator.disconnect()
        self._logger.info("rover disconnected!")

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

    async def set_velocity(self, linear: float, angular: float) -> CommandAck:
        """
        Установка линейной и угловой скорости робота

        :param linear: Линейная скорость
        :type linear: float
        :param angular: Угловая скорость
        :type angular: float
        :return: Результат выполнения команды
        :rtype: CommandResult
        """
        return await self._communicator.send_command(
            RoverCommands.SET_VELOCITY,
            linear=linear,
            angular=angular
        )


    async def set_differential_speed(self, left: float, right: float) -> CommandAck:
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
        return await self._communicator.send_command(
            RoverCommands.SET_DIFF_SPEED,
            left=left,
            right=right
        )

    async def get_telemetry(self) -> TelemetryData:
        """
        Получение телеметрии робота

        :return: Данные телеметрии робота
        :rtype: Telemetry
        """
        return await self._communicator.get_telemetry()

    async def get_battery_status(self) -> BatteryData:
        """
        Получение заряда батареи

        :return: Заряд батареи в процентах
        :rtype: int
        """
        return await self._communicator.get_battery_status()

    async def moo(self):
        """
        Воспроизведение звука "мычания"
        """
        await self._communicator.send_command(RoverCommands.MOO)

    async def beep(self):
        """
        Воспроизведение звукового сигнала
        """
        await self._communicator.send_command(RoverCommands.BEEP)

    async def goto(self, x: float, y: float, yaw: float | None=None):
        """
        Перемещение робота в заданную точку.

        :param x: Координата X целевой точки
        :type x: float
        :param y: Координата Y целевой точки
        :type y: float
        :param yaw: Угол поворота в целевой точке (радианы)
        :type yaw: float | None
        """
        await self._communicator.goto(x=x, y=y, yaw=yaw)

    async def stop(self) -> CommandAck:
        """
        Остановка
        """
        return await self._communicator.send_command(RoverCommands.STOP)

    async def emergency_stop(self) -> CommandAck:
        """
        Аварийная остановка
        """
        return await self._communicator.send_command(RoverCommands.EMERGENCY_STOP)

    async def stream_telemetry(self) -> AsyncGenerator[TelemetryData, None]:
        """
        Потоковое получение телеметрии

        Генератор, возвращающий данные телеметрии в реальном времени.

        :return: Асинхронный генератор данных телеметрии
        :rtype: AsyncGenerator[TelemetryData, None]

        :Example:
            .. code-block:: python

                async for telemetry in rover.stream_telemetry():
                    print(f"Position: {telemetry.position.x}, {telemetry.position.y}")
        """
        async for data in self._communicator.stream_telemetry():
            yield data

    @asynccontextmanager
    async def rc_stream_context(self):
        """
        Контекстный менеджер для потоковой передачи RC-каналов.

        Автоматически запускает и останавливает RC-поток, обеспечивая
        безопасное управление роботом.

        Example:
            .. code-block:: python
                async with rover.rc_stream_context() as rc_control:
                    # Устанавливаем каналы управления
                    rc_control.channel1 = 2000  # Вперед
                    rc_control.channel2 = 1000  # Поворот влево
                    await asyncio.sleep(2.0)

                    # Меняем команду
                    rc_control.channel1 = 1500  # Стоп
        """
        self._logger.info("entering rc_stream_context")
        try:
            await self.start_rc_stream()

            yield self.rc_channels

        finally:
            self._logger.debug("exiting rc_stream_context")
            await self.stop_rc_stream()

    async def start_rc_stream(self):
        """
        Запустить потоковую передачу RC-команд.

        Используется для непрерывного управления ровером через RC-каналы.

        :raises RuntimeError: При ошибках запуска потока
        """
        if self._is_rc_streaming:
            return

        self._is_rc_streaming = True
        self._rc_stream_task = asyncio.create_task(self._rc_stream_loop())

    async def stop_rc_stream(self):
        """
        Остановка потока RC команд
        """
        self._reset_rc_channels()
        self._is_rc_streaming = False
        if self._rc_stream_task:
            self._rc_stream_task.cancel()
            try:
                await self._rc_stream_task
            except asyncio.CancelledError:
                pass
            finally:
                self._rc_stream_task = None

    def _reset_rc_channels(self):
        """
        Сбрасывает RC каналы в нейтральное положение
        """
        self.rc_channels.channel1 = 1500
        self.rc_channels.channel2 = 1500
        self.rc_channels.channel3 = 1500
        self.rc_channels.channel4 = 1500

    async def _rc_stream_loop(self):
        """
        Основной цикл отправки RC команд
        """
        try:
            async def generate_commands():
                while self._is_rc_streaming:

                    yield self.rc_channels
                    await asyncio.sleep(self._rc_stream_interval)

            async for ack in self._communicator.stub.stream_rc_channels(generate_commands()):
                if not ack.success:
                    raise RuntimeError(f"RC command failed: {ack.message}")

        except asyncio.CancelledError:
            raise RuntimeError("RC stream cancelled")
        except Exception as e:
            raise RuntimeError(f"RC stream error: {e}")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()