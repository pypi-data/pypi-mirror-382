# Smart Bot Factory

Современная библиотека для создания умных чат-ботов на Python с использованием OpenAI, Telegram и Supabase.

## 🚀 Возможности

- **🤖 AI Integration** - Полная интеграция с OpenAI GPT для умных диалогов
- **📱 Telegram Bot API** - Поддержка через aiogram 3.x
- **💾 Supabase Backend** - Хранение данных, сессий и аналитики
- **🎯 Router System** - Модульная система обработчиков событий
- **⏰ Smart Scheduler** - Умное планирование задач с проверкой активности пользователей
- **🌍 Global Handlers** - Массовые рассылки и глобальные события
- **🧪 Testing Suite** - Встроенная система тестирования ботов
- **🛠️ CLI Tools** - Удобный интерфейс командной строки
- **👥 Admin Panel** - Система администрирования через Telegram
- **📊 Analytics** - Встроенная аналитика и отчеты

## 📦 Установка

### Системные требования

Перед установкой убедитесь, что у вас установлено:

- **Python 3.9+** (рекомендуется 3.11+)
- **pip** или **uv** для управления пакетами
- Доступ к интернету для установки зависимостей

### Из PyPI (рекомендуется)

```bash
pip install smart_bot_factory
```

### С помощью uv (современный менеджер пакетов)

```bash
uv add smart_bot_factory
```

### Из исходников (для разработки)

```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/chat-bots.git
cd chat-bots

# Установите зависимости через uv
uv sync

# Или через pip
pip install -e .
```

### Установка определенной версии

```bash
pip install smart_bot_factory==0.1.8
```

### Проверка установки

После установки проверьте доступность CLI:

```bash
sbf --help
```

Вы должны увидеть список доступных команд.

### Настройка внешних сервисов

Для работы бота вам понадобятся:

1. **Telegram Bot Token**
   - Создайте бота через [@BotFather](https://t.me/botfather)
   - Получите токен вида `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

2. **OpenAI API Key**
   - Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com)
   - Создайте API ключ в разделе API Keys
   - Ключ имеет вид `sk-...`

3. **Supabase Project**
   - Создайте проект на [supabase.com](https://supabase.com)
   - Получите URL проекта и `anon` ключ в Project Settings → API
   - Импортируйте SQL схему из `smart_bot_factory/database/schema.sql`

## ⚡ Быстрый старт

### 1. Создайте нового бота

```bash
sbf create my-bot
```

Это создаст:
- 📁 `bots/my-bot/` - папка с конфигурацией бота
- 📄 `my-bot.py` - основной файл запуска
- ⚙️ `bots/my-bot/.env` - конфигурация окружения
- 📝 `bots/my-bot/prompts/` - промпты для AI
- 🧪 `bots/my-bot/tests/` - тестовые сценарии

### 2. Настройте переменные окружения

Отредактируйте `bots/my-bot/.env`:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key

# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Администраторы
ADMIN_TELEGRAM_IDS=123456789,987654321
```

### 3. Запустите бота

```bash
sbf run my-bot
```

## 📚 Архитектура

### Router System

Smart Bot Factory использует систему роутеров для организации обработчиков:

```python
from smart_bot_factory.router import Router
from smart_bot_factory.message import send_message_by_human
from smart_bot_factory.creation import BotBuilder

# Создаем роутер
router = Router("my_bot_handlers")

# Регистрируем обработчики
@router.event_handler("appointment_booking", notify=True)
async def handle_booking(user_id: int, event_data: str):
    """Обработчик записи на прием"""
    await send_message_by_human(
        user_id=user_id,
        message_text=f"✅ Запись подтверждена! {event_data}"
    )
    return {"status": "success"}

# Запуск бота
async def main():
    bot = BotBuilder("my-bot")
    bot.register_router(router)
    await bot.build()
    await bot.start()
```

### Типы обработчиков

#### 1. Event Handlers - Обработчики событий

Немедленная обработка событий от AI:

```python
@router.event_handler("phone_collected", notify=True, once_only=True)
async def handle_phone(user_id: int, event_data: str):
    """Вызывается когда AI собирает номер телефона"""
    # event_data содержит данные от AI
    phone = parse_phone(event_data)
    
    # Сохраняем в CRM
    await save_to_crm(user_id, phone)
    
    return {"status": "saved", "phone": phone}
```

**Параметры:**
- `notify` - уведомлять админов (default: False)
- `once_only` - выполнить только один раз (default: True)

#### 2. Scheduled Tasks - Запланированные задачи

Задачи с отложенным выполнением для конкретного пользователя:

```python
@router.schedule_task("send_reminder", delay="2h", smart_check=True)
async def send_reminder(user_id: int, reminder_text: str):
    """Отправит напоминание через 2 часа"""
    await send_message_by_human(
        user_id=user_id,
        message_text=f"🔔 {reminder_text}"
    )
    return {"status": "sent"}
```

**Параметры:**
- `delay` - задержка (обязательно): `"1h"`, `"30m"`, `"2h 15m"`, `3600`
- `smart_check` - умная проверка активности (default: True)
- `once_only` - выполнить только один раз (default: True)
- `event_type` - привязка к событию для напоминаний

**Smart Check:**
- Отменяет задачу если пользователь перешел на другой этап
- Переносит выполнение если пользователь был активен недавно
- Сохраняет session_id для точного отслеживания

#### 3. Global Handlers - Глобальные обработчики

Массовые действия для всех пользователей:

```python
@router.global_handler("mass_notification", delay="1h", notify=True)
async def send_announcement(announcement_text: str):
    """Отправит анонс всем пользователям через 1 час"""
    from smart_bot_factory.message import send_message_to_users_by_stage
    
    await send_message_to_users_by_stage(
        stage="introduction",
        message_text=announcement_text,
        bot_id="my-bot"
    )
    
    return {"status": "completed"}
```

**Параметры:**
- `delay` - задержка (обязательно)
- `notify` - уведомлять админов (default: False)
- `once_only` - выполнить только один раз (default: True)

### Event-Based Reminders

Напоминания о событиях за определенное время:

```python
# Сначала создаем обработчик события
@router.event_handler("appointment_booking")
async def handle_booking(user_id: int, event_data: str):
    """Сохраняет запись: имя, телефон, дата, время"""
    return {"status": "saved", "data": event_data}

# Затем создаем напоминание
@router.schedule_task(
    "appointment_reminder",
    delay="2h",
    event_type="appointment_booking"  # Привязка к событию
)
async def remind_about_appointment(user_id: int, reminder_text: str):
    """Отправит напоминание за 2 часа до записи"""
    await send_message_by_human(
        user_id=user_id,
        message_text=f"⏰ Напоминание о записи через 2 часа!"
    )
    return {"status": "sent"}
```

Система автоматически:
1. Извлечет дату/время из события `appointment_booking`
2. Вычислит время напоминания (за 2 часа до записи)
3. Запланирует отправку в правильное время

## 🛠️ CLI Команды

```bash
# Создание и управление ботами
sbf create <bot-id>              # Создать нового бота
sbf create <bot-id> <template>   # Создать из шаблона
sbf copy <source> <new-id>       # Копировать существующего бота
sbf list                         # Показать всех ботов
sbf rm <bot-id>                  # Удалить бота

# Запуск
sbf run <bot-id>                 # Запустить бота

# Тестирование
sbf test <bot-id>                # Запустить все тесты
sbf test <bot-id> --file quick_scenarios.yaml
sbf test <bot-id> -v             # Подробный вывод
sbf test <bot-id> --max-concurrent 10

# Промпты
sbf prompts <bot-id>             # Список промптов
sbf prompts <bot-id> --edit welcome_message
sbf prompts <bot-id> --add new_prompt

# Конфигурация
sbf config <bot-id>              # Редактировать .env
sbf path                         # Показать путь к проекту
sbf link                         # Генератор UTM-ссылок
```

## 📝 Система промптов

Промпты хранятся в `bots/<bot-id>/prompts/`:

- `welcome_message.txt` - Приветственное сообщение
- `help_message.txt` - Справка для пользователя
- `1sales_context.txt` - Контекст продаж
- `2product_info.txt` - Информация о продукте
- `3objection_handling.txt` - Работа с возражениями
- `final_instructions.txt` - Финальные инструкции для AI

AI автоматически получает доступ к зарегистрированным обработчикам через промпт.

## 🧪 Тестирование

Создайте тестовые сценарии в YAML:

```yaml
# bots/my-bot/tests/scenarios.yaml
scenarios:
  - name: "Запись на прием"
    steps:
      - user: "Привет!"
        expect_stage: "introduction"
      
      - user: "Хочу записаться на прием"
        expect_stage: "qualification"
        expect_events:
          - type: "appointment_request"
      
      - user: "Меня зовут Иван, +79991234567, завтра в 15:00"
        expect_events:
          - type: "appointment_booking"
          - type: "appointment_reminder"  # Должно запланироваться
        expect_quality: ">= 8"
```

Запуск:
```bash
sbf test my-bot --file scenarios.yaml -v
```

## 💬 Отправка сообщений

### Отправка пользователю

```python
from smart_bot_factory.message import send_message_by_human

await send_message_by_human(
    user_id=123456789,
    message_text="Привет! Это сообщение от системы",
    session_id="optional-session-id"
)
```

### Массовая рассылка по этапу

```python
from smart_bot_factory.message import send_message_to_users_by_stage

await send_message_to_users_by_stage(
    stage="introduction",
    message_text="📢 Важное объявление!",
    bot_id="my-bot"
)
```

## 🗄️ База данных

Smart Bot Factory использует Supabase со следующими таблицами:

- `sales_users` - Пользователи
- `sales_chat_sessions` - Сессии диалогов
- `sales_chat_messages` - История сообщений
- `scheduled_events` - Запланированные события и задачи
- `admin_sessions` - Сессии администраторов

SQL схема доступна в `smart_bot_factory/database/`.

## 👥 Система администрирования

Добавьте ID администраторов в `.env`:

```env
ADMIN_TELEGRAM_IDS=123456789,987654321
ADMIN_SESSION_TIMEOUT_MINUTES=30
```

Админы получают:
- 📊 Статистику и аналитику
- 🔔 Уведомления о важных событиях (если `notify=True`)
- 🛠️ Доступ к специальным командам

## 🔧 Продвинутое использование

### Множественные роутеры

```python
# handlers/main.py
main_router = Router("main")

# handlers/admin.py
admin_router = Router("admin")

# app.py
bot = BotBuilder("my-bot")
bot.register_router(main_router)
bot.register_router(admin_router)
```

### Вложенные роутеры

```python
main_router = Router("main")
payments_router = Router("payments")

# Включаем роутер платежей в основной
main_router.include_router(payments_router)

bot.register_router(main_router)
```

### Работа с клиентами

```python
from smart_bot_factory.supabase import SupabaseClient

# Создаем клиент для вашего бота
supabase = SupabaseClient("my-bot")

# Используем напрямую
users = supabase.client.table('sales_users').select('*').eq('bot_id', 'my-bot').execute()
```

## 📊 Структура проекта

```
my-project/
├── bots/                      # Папка с ботами
│   ├── my-bot/
│   │   ├── .env              # Конфигурация
│   │   ├── prompts/          # AI промпты
│   │   ├── tests/            # Тестовые сценарии
│   │   ├── files/            # Файлы бота
│   │   ├── welcome_files/    # Приветственные файлы
│   │   └── reports/          # Отчеты тестов
│   └── another-bot/
│       └── ...
├── my-bot.py                 # Основной файл запуска
├── another-bot.py
└── .env                      # Глобальная конфигурация (опционально)
```

## 🔄 Примеры

### Полный пример бота

```python
import asyncio

from smart_bot_factory.router import Router
from smart_bot_factory.message import send_message_by_human, send_message_to_users_by_stage
from smart_bot_factory.supabase import SupabaseClient
from smart_bot_factory.creation import BotBuilder

# Инициализация
router = Router("medical_bot")
supabase_client = SupabaseClient("medical-bot")

# Обработчик записи на прием
@router.event_handler("appointment_booking", notify=True)
async def handle_appointment(user_id: int, event_data: str):
    """Обрабатывает запись на прием к врачу"""
    # event_data: "имя: Иван, телефон: +79991234567, дата: 2025-10-15, время: 14:00"
    
    await send_message_by_human(
        user_id=user_id,
        message_text="✅ Запись подтверждена! Ждем вас."
    )
    
    return {"status": "success", "data": event_data}

# Напоминание за 2 часа до приема
@router.schedule_task(
    "appointment_reminder",
    delay="2h",
    event_type="appointment_booking"
)
async def remind_before_appointment(user_id: int, reminder_text: str):
    """Напоминание о записи"""
    await send_message_by_human(
        user_id=user_id,
        message_text="⏰ Напоминаем о вашей записи через 2 часа!"
    )
    return {"status": "sent"}

# Ночной дайджест для всех
@router.global_handler("daily_digest", delay="24h")
async def send_daily_digest(digest_text: str):
    """Отправляет ежедневный дайджест всем активным пользователям"""
    await send_message_to_users_by_stage(
        stage="active",
        message_text=f"📊 Дайджест дня:\n\n{digest_text}",
        bot_id="medical-bot"
    )

# Запуск
async def main():
    bot = BotBuilder("medical-bot")
    bot.register_router(router)
    await bot.build()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🐛 Отладка

Включите режим отладки в `.env`:

```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

Это покажет:
- JSON ответы от AI
- Детальные логи обработки
- Информацию о роутерах и обработчиках

## 📋 Требования

### Системные
- Python 3.9+ (рекомендуется 3.11+)
- pip или uv для управления пакетами

### Основные зависимости
- aiogram 3.4.1+ - Telegram Bot API
- supabase 2.3.4+ - База данных
- openai 1.12.0+ - AI модель
- click 8.0.0+ - CLI интерфейс
- python-dotenv 1.0.1+ - Управление переменными окружения

Все зависимости устанавливаются автоматически при установке библиотеки.

### Внешние сервисы
- Telegram Bot Token ([@BotFather](https://t.me/botfather))
- OpenAI API Key ([platform.openai.com](https://platform.openai.com))
- Supabase Project ([supabase.com](https://supabase.com))

Подробнее см. раздел [Установка](#-установка).

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! 

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

## 🔗 Полезные ссылки

- [Документация Supabase](https://supabase.com/docs)
- [Документация OpenAI](https://platform.openai.com/docs)
- [Документация aiogram](https://docs.aiogram.dev/)

## 💡 Поддержка

Если у вас возникли вопросы или проблемы, создайте issue в репозитории.

---

Сделано с ❤️ для создания умных ботов
