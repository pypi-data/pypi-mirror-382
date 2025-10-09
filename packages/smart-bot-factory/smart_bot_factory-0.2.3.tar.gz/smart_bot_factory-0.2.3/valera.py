#!/usr/bin/env python3
"""
Бот valera - создан с помощью Smart Bot Factory
"""

import asyncio

from smart_bot_factory import (
    BotBuilder,
    event_handler,
    schedule_task,
    send_message_by_human
)

# =============================================================================
# ОБРАБОТЧИКИ СОБЫТИЙ
# =============================================================================

@event_handler("example_event", "Пример обработчика события")
async def handle_example_event(user_id: int, event_data: dict):
    """Пример обработчика события"""
    # Отправляем подтверждение пользователю
    await send_message_by_human(
        user_id=user_id,
        message_text="✅ Событие обработано!"
    )
    
    return {
        "status": "success",
        "message": "Событие обработано"
    }

# =============================================================================
# ЗАПЛАНИРОВАННЫЕ ЗАДАЧИ
# =============================================================================

@schedule_task("example_task", "Пример запланированной задачи")
async def example_task(user_id: int, message: str):
    """Пример запланированной задачи"""
    # Отправляем сообщение
    await send_message_by_human(
        user_id=user_id,
        message_text=f"🔔 Напоминание: {message}"
    )
    
    return {
        "status": "sent",
        "user_id": user_id,
        "message": message
    }

# =============================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# =============================================================================

async def main():
    """Основная функция запуска бота"""
    try:
        # Создаем и собираем бота
        bot_builder = BotBuilder("valera")
        await bot_builder.build()
        
        # Запускаем бота
        await bot_builder.start()
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
