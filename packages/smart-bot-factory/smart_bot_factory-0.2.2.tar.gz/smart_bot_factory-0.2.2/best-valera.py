import asyncio
import logging

from smart_bot_factory.router import EventRouter, TelegramRouter
from smart_bot_factory.message import send_message_by_human, send_message_to_users_by_stage
from smart_bot_factory.supabase import SupabaseClient
from smart_bot_factory.creation import BotBuilder

logger = logging.getLogger(__name__)

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
# ИНИЦИАЛИЗАЦИЯ BOT BUILDER (нужен для декоратора on_start)
# =============================================================================

bot_builder = BotBuilder("best-valera")

# =============================================================================
# TELEGRAM ОБРАБОТЧИКИ (используем прямой aiogram API)
# =============================================================================

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

# =============================================================================
# ОБРАБОТЧИК on_start (вызывается после стандартного /start)
# =============================================================================

@bot_builder.on_start
async def custom_start_handler(user_id: int, session_id: str, message: Message, state: FSMContext):
    """
    Вызывается после стандартной логики /start
    Здесь можно отправить дополнительные сообщения, кнопки и т.д.
    """
    # Пример: отправляем сообщение с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="💰 Цены", callback_data="prices")],
        [InlineKeyboardButton(text="📞 Связаться", callback_data="contact")]
    ])
    
    await message.answer(
        "🎯 Что вас интересует?",
        reply_markup=keyboard
    )

# =============================================================================
# ХУКИ ДЛЯ КАСТОМИЗАЦИИ ОБРАБОТКИ СООБЩЕНИЙ
# =============================================================================

# ХУК 1: Валидация сообщений
@bot_builder.validate_message
async def validate_service_names(message, supabase_client):
    """Проверяем корректность названий услуг"""
    # Пример: блокируем неправильные названия
    incorrect_names = ["массаш", "педекюр", "макияш"]
    
    if message.text:
        for incorrect in incorrect_names:
            if incorrect in message.text.lower():
                await message.answer(
                    f"❗ Возможно, вы имели в виду другую услугу?\n"
                    f"Пожалуйста, уточните название"
                )
                return False  # Прерываем обработку AI
    
    return True  # Продолжаем обработку

# ХУК 2: Обогащение промпта
@bot_builder.enrich_prompt
async def add_client_info_to_prompt(system_prompt, user_id, session_id, supabase_client):
    """Добавляем информацию о клиенте в промпт"""
    try:
        session = await supabase_client.get_active_session(user_id)
        
        if session and session.get('metadata'):
            phone = session['metadata'].get('phone')
            name = session['metadata'].get('confirmed_name') or session['metadata'].get('telegram_name')
            
            if phone:
                client_info = f"\n\nИНФОРМАЦИЯ О КЛИЕНТЕ:\n- Телефон: {phone}"
                if name:
                    client_info += f"\n- Имя: {name}"
                client_info += "\n\n⚠️ ВАЖНО: При создании записи используй ЭТОТ телефон и имя!"
                
                return system_prompt + client_info
    except Exception as e:
        logger.error(f"Ошибка обогащения промпта: {e}")
    
    return system_prompt

# ХУК 3: Обогащение контекста (например, данные из внешнего API)
@bot_builder.enrich_context
async def add_external_api_data(messages, user_id, session_id):
    """Добавляем данные из внешних систем"""
    # Пример: можно добавить расписание из YClients, данные из CRM и т.д.
    # messages.append({
    #     "role": "system",
    #     "content": "Реальное доступное время: ..."
    # })
    return messages

# ХУК 4: Обработка ответа AI
@bot_builder.process_response
async def add_promo_to_price_response(response_text, ai_metadata, user_id):
    """Добавляем промо-код к ответам о ценах"""
    if "цен" in response_text.lower() or "стоимост" in response_text.lower():
        response_text += "\n\n🎁 Промокод FIRST10 для скидки 10% на первый визит!"
    
    return response_text, ai_metadata

# ХУК 5: Фильтр отправки
@bot_builder.filter_send
async def allow_all_messages(user_id, response_text):
    """Разрешаем все сообщения (можно добавить блокировку по условию)"""
    # Пример: блокировка во время обработки
    # if is_processing(user_id):
    #     return False
    return True

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

# Обработчики callback'ов от кнопок в on_start
@telegram_router_1.router.callback_query(F.data == "catalog")
async def handle_catalog(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки Каталог"""
    await callback.answer()
    await callback.message.answer("📖 Вот наш каталог товаров:\n\n1. Товар 1\n2. Товар 2\n3. Товар 3")

@telegram_router_1.router.callback_query(F.data == "prices")
async def handle_prices(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки Цены"""
    await callback.answer()
    await callback.message.answer("💰 Наши цены:\n\n📦 Базовый - 1000₽\n📦 Премиум - 5000₽")

@telegram_router_1.router.callback_query(F.data == "contact")
async def handle_contact(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки Связаться"""
    await callback.answer()
    await callback.message.answer("📞 Свяжитесь с нами:\n\nТелефон: +7 (999) 123-45-67\nEmail: info@example.com")

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
        # bot_builder уже создан выше (для декоратора @bot_builder.on_start)
        
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
