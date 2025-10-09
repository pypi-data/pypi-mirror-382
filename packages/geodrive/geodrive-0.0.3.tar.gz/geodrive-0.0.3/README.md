<p align="center">
  <img src="https://github.com/PunkNaPrekole/geodrive/blob/dev/docs/source/_static/logo.png" alt="geodrive" style="width: 500px;">
</p>

<p align="center">
    <em>Python SDK для управления роботами-роверами через gRPC</em>
</p>

<p align="center">
<a href="https://github.com/PunkNaPrekole/geodrive/actions" target="_blank">
    <img src="https://github.com/PunkNaPrekole/geodrive/actions/workflows/test.yml/badge.svg" alt="Tests">
</a>
<a href="https://pypi.org/project/geodrive" target="_blank">
    <img src="https://img.shields.io/pypi/v/geodrive?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/geodrive" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/geodrive.svg?color=%2334D058" alt="Supported Python versions">
</a>
<a href="https://github.com/PunkNaPrekole/geodrive/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/PunkNaPrekole/geodrive?color=%2334D058" alt="License">
</a>
</p>

---

**geodrive** - это современный Python SDK для управления роботами-роверами через gRPC протокол.

## 🚀 Ключевые особенности

* **🎯 Простота использования** - Интуитивный интерфейс с автодополнением
* **⚡ Производительность** - Асинхронный и синхронный клиенты для любых задач  
* **🔧 Готов к продакшену** - Надежная обработка ошибок и переподключение
* **📡 Реальное время** - Потоковая телеметрия и управление
* **🤖 Универсальность** - Поддержка различных моделей роботов-роверов

## 📦 Установка

```bash
uv add geodrive
# или
pip install geodrive
```
# Быстрый старт

## Базовое использование

### Подключение к роверу

```python
from geodrive import Rover

# Подключение к роверу
with Rover(host="10.1.100.160", port=5656) as rover:
    # Отправка команды движения к точке
    rover.goto(5.0, 3.0, 1.57)
    
    # Получение телеметрии
    telemetry = rover.get_telemetry()
    print(f"Позиция: ({telemetry.x:.2f}, {telemetry.y:.2f})")
    print(f"Ориентация: {telemetry.yaw:.2f} рад")
```

## 🛠️ Что внутри?

### **Управление движением**
- Точное позиционирование в координатах X, Y, Yaw
- Потоковое отслеживание прогресса движения  
- RC-стиль управления для плавного движения

### **Телеметрия в реальном времени**
- Потоковая передача данных о позиции и ориентации
- Мониторинг состояния батареи и датчиков

### **Надежная коммуникация**
- gRPC для высокопроизводительной связи
- Автоматическое переподключение при обрывах
- Валидация команд и данных

### **Гибкость использования**
- Синхронный для простых скриптов
- Асинхронный для веб-приложений
- Поддержка контекстных менеджеров

## 📋 Требования

- Python 3.10+
- gRPC сервер на стороне робота
- Сетевое соединение с роботом

## 🔗 Зависимости

**geodrive** построен на современных технологиях:

- **grpcio** - высокопроизводительный gRPC клиент
- **protobuf** - работа с бинарными протоколами  
- **pydantic** - валидация и сериализация данных
- **structlog** - структурированное логирование

## 📚 Документация

### Начало работы
- [🚀 Быстрый старт](https://punknaprekole.github.io/geodrive/geodrive/getting_started)
- [📦 Установка](https://punknaprekole.github.io/geodrive/geodrive/installation) 
- [💡 Примеры](https://punknaprekole.github.io/geodrive/geodrive/examples)

### API документация
- [🔧 Основные классы](https://punknaprekole.github.io/geodrive/geodrive/api/index)

### Сообщество
- [👥 Community Playbook](https://punknaprekole.github.io/geodrive/recipes/index)

### Для разработчиков
- [🤝 Руководство по контрибьютингу](https://punknaprekole.github.io/geodrive/geodrive/contributing)

## 📄 Лицензия

Проект распространяется под лицензией **MIT**.
