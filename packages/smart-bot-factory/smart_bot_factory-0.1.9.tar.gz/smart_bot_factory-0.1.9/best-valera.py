import asyncio

from smart_bot_factory.router import Router
from smart_bot_factory.message import send_message_by_human, send_message_to_users_by_stage
from smart_bot_factory.supabase import SupabaseClient
from smart_bot_factory.creation import BotBuilder

# Создаем роутер для всех обработчиков
router = Router("best-valera_handlers")

supabase_client = SupabaseClient("best-valera")

# =============================================================================
# ОБРАБОТЧИКИ СОБЫТИЙ
# =============================================================================

@router.event_handler("example_event")
async def handle_example_event(user_id: int, event_data: str):
    """Пример обработчика события"""
    # Отправляем подтверждение пользователю
    await send_message_by_human(
        user_id=user_id,
        message_text=f"✅ Событие обработано! Данные: {event_data}"
    )
    
    return {
        "status": "success",
        "message": "Событие обработано"
    }

# =============================================================================
# ВРЕМЕННЫЕ ЗАДАЧИ ДЛЯ ОДНОГО ПОЛЬЗОВАТЕЛЯ
# =============================================================================

@router.schedule_task("send_reminder", delay="1h")
async def send_user_reminder(user_id: int, reminder_text: str):
    """Отправляет напоминание пользователю"""
    await send_message_by_human(
        user_id=user_id,
        message_text=f"🔔 Напоминание: {reminder_text}"
    )
    
    return {
        "status": "reminder_sent",
        "message": f"Напоминание отправлено пользователю {user_id}"
    }

# =============================================================================
# ГЛОБАЛЬНЫЕ ОБРАБОТЧИКИ (для всех пользователей)
# =============================================================================

@router.global_handler("mass_notification", delay="1h", notify=True)
async def send_global_announcement(announcement_text: str):
    """Отправляет анонс всем пользователям бота"""
   
    await send_message_to_users_by_stage(
        stage="introduction",
        message_text=announcement_text,
        bot_id="best-valera"
    )

# =============================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# =============================================================================

async def main():
    """Основная функция запуска бота"""
    try:
        # Создаем и собираем бота
        bot_builder = BotBuilder("best-valera")
        
        # Регистрируем роутер ПЕРЕД сборкой, чтобы обработчики были доступны
        bot_builder.register_router(router)
        
        await bot_builder.build()
        
        # Запускаем бота
        await bot_builder.start()
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
