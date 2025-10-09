# Better IMAP

Асинхронная Python библиотека для работы с IMAP протоколом. Упрощает получение и поиск электронных писем с поддержкой прокси и различных почтовых сервисов.

## Особенности

- Асинхронная работа с IMAP серверами
- Поддержка прокси через better-proxy
- Автоматическое определение настроек IMAP по email адресу
- Гибкие возможности поиска и фильтрации писем
- Поддержка различных почтовых провайдеров

## Установка

```bash
pip install better-imap
```

## Быстрый старт

### Базовое использование

```python
import asyncio
from better_imap import MailBox

async def main():
    # Создание подключения к почтовому ящику
    async with MailBox("user@example.com", "password") as mailbox:
        # Получение всех писем
        messages = await mailbox.fetch_messages()
        
        for message in messages:
            print(f"От: {message.sender}")
            print(f"Тема: {message.subject}")
            print(f"Дата: {message.date}")
            print(f"Текст: {message.text[:100]}...")
            print("-" * 50)

asyncio.run(main())
```

### Поиск писем с фильтрами

```python
import asyncio
from datetime import datetime, timedelta
from better_imap import MailBox

async def main():
    async with MailBox("user@example.com", "password") as mailbox:
        # Поиск писем за последние 7 дней
        since_date = datetime.now() - timedelta(days=7)
        
        messages = await mailbox.fetch_messages(
            search_criteria="ALL",
            since=since_date,
            allowed_senders=["@important-sender.com"],
            folders=["INBOX", "Sent"]
        )
        
        print(f"Найдено {len(messages)} писем")

asyncio.run(main())
```

### Поиск писем по регулярному выражению

```python
import asyncio
import re
from better_imap import MailBox

async def main():
    async with MailBox("user@example.com", "password") as mailbox:
        # Поиск писем содержащих код подтверждения
        pattern = r'\b\d{4,6}\b'  # 4-6 цифр подряд
        
        matches = await mailbox.search_matches(
            regex=pattern,
            folders=["INBOX"],
            search_criteria="UNSEEN"
        )
        
        for message in matches:
            print(f"Код найден в письме от {message.sender}")
            # Извлечение кода из текста
            code = re.search(pattern, message.text).group()
            print(f"Код подтверждения: {code}")

asyncio.run(main())
```

### Использование с прокси

```python
import asyncio
from better_imap import MailBox
from better_proxy import Proxy

async def main():
    # Настройка прокси
    proxy = Proxy.from_str("http://user:pass@proxy-server.com:8080")
    
    async with MailBox("user@example.com", "password", proxy=proxy) as mailbox:
        messages = await mailbox.fetch_messages()
        print(f"Получено {len(messages)} писем через прокси")

asyncio.run(main())
```

### Поиск с повторными попытками

```python
import asyncio
from better_imap import MailBox

async def main():
    async with MailBox("user@example.com", "password") as mailbox:
        # Ожидание письма с кодом подтверждения в течение 5 минут
        try:
            message = await mailbox.search_with_retry(
                regex=r'\b\d{6}\b',  # 6-значный код
                timeout=300,  # 5 минут
                interval=10   # проверка каждые 10 секунд
            )
            
            if message:
                print("Код подтверждения получен!")
                print(f"Текст: {message.text}")
            else:
                print("Письмо не найдено за указанное время")
                
        except Exception as e:
            print(f"Ошибка при поиске: {e}")

asyncio.run(main())
```

## Параметры конструктора MailBox

- `address` (str) - Email адрес для подключения
- `password` (str) - Пароль от почтового ящика
- `service` (ServiceType, optional) - Настройки IMAP сервера (определяется автоматически)
- `use_firstmail_on_unknown_domain` (bool) - Использовать FirstMail для неизвестных доменов
- `proxy` (Proxy, optional) - Прокси сервер для подключения
- `timeout` (float) - Таймаут операций в секундах (по умолчанию 10)
- `loop` (asyncio.AbstractEventLoop, optional) - Event loop для асинхронных операций

## Методы поиска

### fetch_messages()

Основной метод для получения писем с различными фильтрами:

- `folders` - Список папок для поиска (по умолчанию ["INBOX"])
- `search_criteria` - Критерии поиска IMAP ("ALL", "UNSEEN")
- `since` - Поиск писем с указанной даты
- `allowed_senders` - Список разрешенных отправителей (regex паттерны)
- `allowed_receivers` - Список разрешенных получателей (regex паттерны)
- `sender_regex` - Регулярное выражение для фильтрации отправителей

### search_matches()

Поиск писем по регулярному выражению в тексте письма.

### search_match()

Поиск одного письма по регулярному выражению.

### search_with_retry()

Поиск письма с повторными попытками в течение заданного времени.

## Обработка ошибок

Библиотека предоставляет специализированные исключения:

- `IMAPLoginFailed` - Ошибка авторизации
- `IMAPSearchTimeout` - Таймаут при поиске
- `WrongIMAPAddress` - Неправильный IMAP адрес

```python
import asyncio
from better_imap import MailBox
from better_imap.errors import IMAPLoginFailed, IMAPSearchTimeout

async def main():
    try:
        async with MailBox("user@example.com", "wrong_password") as mailbox:
            messages = await mailbox.fetch_messages()
    except IMAPLoginFailed:
        print("Неверные учетные данные")
    except IMAPSearchTimeout:
        print("Превышено время ожидания поиска")

asyncio.run(main())
```

## Лицензия

MIT License