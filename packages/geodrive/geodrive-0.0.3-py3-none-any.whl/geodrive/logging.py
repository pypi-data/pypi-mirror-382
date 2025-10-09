import logging
import time
from typing import Any, Callable, TypeVar, cast
from contextlib import contextmanager

import structlog

F = TypeVar('F', bound=Callable[..., Any])


def setup_logging(
        level: str = "INFO",
        json_format: bool = False,
        enable_stdlib: bool = False,
        **kwargs: Any
) -> None:
    """
    Настройка логирования для geodrive SDK.

    :param level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
    :param json_format: Использовать JSON формат для продакшена
    :param enable_stdlib: Также настроить стандартное логирование
    :param kwargs: Дополнительные аргументы
    """
    _setup_structlog(level, json_format, enable_stdlib, **kwargs)


def _setup_structlog(
        level: str = "INFO",
        json_format: bool = False,
        enable_stdlib: bool = False,
        **kwargs: Any
) -> None:
    """
    Настройка structlog для современного структурированного логирования.

    :param level: Уровень логирования
    :param json_format: Использовать JSON формат
    :param enable_stdlib: Настроить стандартное логирование
    :param kwargs: Дополнительные аргументы
    """
    level_num = getattr(logging, level.upper(), logging.INFO)

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    if json_format:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    if enable_stdlib:
        _setup_stdlib_logging(level, **kwargs)

    # Устанавливаем уровень для structlog
    logging.getLogger("geodrive").setLevel(level_num)


def _setup_stdlib_logging(level: str = "INFO", **kwargs: Any) -> None:
    """
    Настройка стандартного логирования как fallback.

    :param level: Уровень логирования
    :param kwargs: Дополнительные аргументы
    """
    level_num = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger("geodrive")
    logger.setLevel(level_num)
    logger.addHandler(handler)
    logger.propagate = False


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """
    Получить логгер для компонентов SDK.

    :param name: Имя логгера. Если None, возвращает корневой логгер 'geodrive'
    :return: Настроенный структурированный логгер
    """
    if name is None:
        name = "geodrive"
    else:
        name = f"geodrive.{name}"

    return structlog.get_logger(name)


def get_communicator_logger() -> structlog.BoundLogger:
    """
    Получить логгер для коммуникаторов.

    :return: Логгер для компонентов коммуникации
    """
    return get_logger("communicators")


def get_movement_logger() -> structlog.BoundLogger:
    """
    Получить логгер для менеджеров движения.

    :return: Логгер для компонентов управления движением
    """
    return get_logger("movement")


def get_client_logger() -> structlog.BoundLogger:
    """
    Получить логгер для клиентов.

    :return: Логгер для клиентских компонентов
    """
    return get_logger("client")


class LoggingContext:
    """
    Контекстный менеджер для добавления временного контекста в логи.

    :param context_vars: Переменные контекста в виде ключ-значение
    """

    def __init__(self, **context_vars: Any):
        self.context_vars = context_vars
        self.token = None

    def __enter__(self) -> "LoggingContext":
        self.token = structlog.contextvars.bind_contextvars(**self.context_vars)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.token:
            structlog.contextvars.unbind_contextvars(self.token)


def track_performance(operation: str) -> Callable[[F], F]:
    """
    Декоратор для отслеживания производительности функций.

    :param operation: Название операции для логирования
    :return: Декорированная функция
    """

    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger("performance")
            start_time = time.time()

            with LoggingContext(operation=operation):
                logger.debug(f"Начало операции {operation}")

                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    logger.info(
                        f"Операция {operation} завершена успешно",
                        duration_seconds=round(duration, 3),
                        status="success"
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    logger.error(
                        f"Операция {operation} завершена с ошибкой",
                        duration_seconds=round(duration, 3),
                        error=str(e),
                        status="error"
                    )
                    raise

        return cast(F, wrapper)

    return decorator


@contextmanager
def performance_tracker(operation: str, **context: Any) -> Any:
    """
    Контекстный менеджер для отслеживания производительности блоков кода.

    :param operation: Название операции для логирования
    :param context: Дополнительный контекст для логирования
    :return: Контекстный менеджер
    """
    logger = get_logger("performance")
    start_time = time.time()

    with LoggingContext(operation=operation, **context):
        logger.debug(f"Начало операции {operation}", **context)

        try:
            yield
            duration = time.time() - start_time
            logger.info(
                f"Операция {operation} завершена успешно",
                duration_seconds=round(duration, 3),
                status="success",
                **context
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Операция {operation} завершена с ошибкой",
                duration_seconds=round(duration, 3),
                error=str(e),
                status="error",
                **context
            )
            raise


_LOG_SETUP_NOTE = """
Рекомендации по настройке логирования:
--------------------------------------

Для разработки:
    >>> from geodrive.logging import setup_logging
    >>> setup_logging(level="DEBUG")

Для продакшена:
    >>> setup_logging(level="INFO", json_format=True)

Интеграция с существующей системой логирования:
    >>> import logging
    >>> logging.getLogger("geodrive").setLevel(logging.DEBUG)
"""

__all__ = [
    'setup_logging',
    'get_logger',
    'get_communicator_logger',
    'get_movement_logger',
    'get_client_logger',
    'LoggingContext',
    'track_performance',
    'performance_tracker',
]