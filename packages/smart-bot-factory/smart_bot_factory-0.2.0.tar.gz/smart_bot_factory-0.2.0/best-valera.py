import asyncio

from smart_bot_factory.router import EventRouter, TelegramRouter
from smart_bot_factory.message import send_message_by_human, send_message_to_users_by_stage
from smart_bot_factory.supabase import SupabaseClient
from smart_bot_factory.creation import BotBuilder

# =============================================================================
# СОЗДАНИЕ РОУТЕРОВ
# =============================================================================

# Роутер для событий (бизнес-логика)
event_router = EventRouter("best-valera_events")

# Роутер для Telegram (команды и сообщения)
telegram_router_1 = TelegramRouter("best-valera_telegram")
telegram_router_2 = TelegramRouter("best-valera_telegram_2")

supabase_client = SupabaseClient("best-valera")

# =============================================================================
# TELEGRAM ОБРАБОТЧИКИ (используем прямой aiogram API)
# =============================================================================

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

@telegram_router_1.router.message(Command("price", "цена"))
async def handle_price_command(message: Message, state: FSMContext):
    """Обработчик команды /price"""
    await message.answer(
        "💰 Наши цены:\n\n"
        "📦 Базовый пакет - 1000₽\n"
        "📦 Стандартный - 2000₽\n"
        "📦 Премиум - 5000₽"
    )

@telegram_router_2.router.message(F.text & (F.text.lower().contains("цена") | F.text.lower().contains("стоимость")))
async def handle_price_question(message: Message, state: FSMContext):
    """Обработчик вопросов о цене"""
    await message.answer("💡 Напишите /price чтобы увидеть актуальные цены")

# =============================================================================
# ОБРАБОТЧИКИ СОБЫТИЙ (бизнес-логика)
# =============================================================================

@event_router.event_handler("example_event")
async def handle_example_event(user_id: int, event_data: str):
    """Пример обработчика события"""
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

@event_router.schedule_task("send_reminder", delay="1h")
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

@event_router.global_handler("mass_notification", delay="1h", notify=True)
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
        
        # Регистрируем роутеры ПЕРЕД сборкой (можно по одному или несколько сразу)
        bot_builder.register_routers(event_router)  # Роутеры событий
        bot_builder.register_telegram_routers(telegram_router_1, telegram_router_2)  # Telegram роутеры
        
        await bot_builder.build()
        
        # Запускаем бота
        await bot_builder.start()
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
