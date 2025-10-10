"""
TelegramRouter - обертка над aiogram Router для обработки Telegram сообщений
"""

from typing import Any
import logging
from aiogram import Router as AiogramRouter

logger = logging.getLogger(__name__)


class TelegramRouter:
    """
    Обертка над aiogram Router для единообразного API библиотеки
    Позволяет регистрировать обработчики команд, сообщений и callback'ов
    """
    
    def __init__(self, name: str = None):
        """
        Инициализация Telegram роутера
        
        Args:
            name: Имя роутера для логирования
        """
        self.name = name or f"TelegramRouter_{id(self)}"
        self._router = AiogramRouter(name=self.name)
        
        logger.info(f"📱 Создан TelegramRouter: {self.name}")
    
    @property
    def router(self) -> AiogramRouter:
        """
        Возвращает внутренний aiogram Router
        
        Используйте этот роутер для прямой работы с aiogram API:
        
        Example:
            telegram_router = TelegramRouter("my_router")
            
            # Регистрация команды
            @telegram_router.router.message(Command("start"))
            async def start_handler(message: Message):
                await message.answer("Hello!")
            
            # Регистрация callback
            @telegram_router.router.callback_query(F.data.startswith("buy_"))
            async def buy_handler(callback: CallbackQuery):
                await callback.answer("Покупка...")
        """
        return self._router
    
    def get_aiogram_router(self) -> AiogramRouter:
        """Получает внутренний aiogram Router (алиас для .router)"""
        return self._router
    
    def __repr__(self):
        return f"TelegramRouter(name='{self.name}')"

