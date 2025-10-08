"""
Router модули smart_bot_factory
"""

from ..core.router import EventRouter
from ..core.telegram_router import TelegramRouter

__all__ = [
    'EventRouter',  # Роутер для событий
    'TelegramRouter',  # Роутер для Telegram
]