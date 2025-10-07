# Smart Bot Factory

Библиотека для создания умных чат-ботов с использованием OpenAI, Telegram и Supabase.

## Установка

```bash
pip install smart-bot-factory
```

## Быстрый старт

1. Создайте нового бота:
```bash
sbf create my-bot
```

2. Настройте конфигурацию в `bots/my-bot/.env`

3. Запустите бота:
```bash
sbf run my-bot
```

## Возможности

- 🤖 Интеграция с OpenAI GPT для умных ответов
- 📱 Поддержка Telegram Bot API через aiogram
- 💾 Хранение данных в Supabase
- 🔄 Система событий и обработчиков
- ⏰ Планировщик задач
- 🧪 Встроенная система тестирования
- 📝 Управление промптами
- 🛠️ Удобный CLI интерфейс

## CLI команды

```bash
# Создать нового бота
sbf create my-bot

# Запустить бота
sbf run my-bot

# Показать список ботов
sbf list

# Управление промптами
sbf prompts my-bot --list
sbf prompts my-bot --edit welcome_message
sbf prompts my-bot --add new_prompt

# Запустить тесты
sbf test my-bot
```

## Пример использования

```python
from smart_bot_factory import BotBuilder, event_handler, schedule_task

# Обработчик события
@event_handler("book_appointment", "Запись на прием")
async def handle_booking(user_id: int, event_data: dict):
    # Логика обработки записи на прием
    return {"status": "success"}

# Запланированная задача
@schedule_task("send_reminder", "Отправка напоминания")
async def send_reminder(user_id: int, message: str):
    # Логика отправки напоминания
    return {"status": "sent"}

# Запуск бота
async def main():
    bot = BotBuilder("my-bot")
    await bot.build()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## Требования

- Python 3.9+
- OpenAI API ключ
- Telegram Bot Token
- Supabase проект

## Лицензия

MIT