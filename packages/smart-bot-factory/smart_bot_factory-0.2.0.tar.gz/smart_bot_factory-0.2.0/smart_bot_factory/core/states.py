"""
Состояния FSM для бота
"""

from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    waiting_for_message = State()
    admin_chat = State()  # пользователь в диалоге с админом

class AdminStates(StatesGroup):
    admin_mode = State()
    in_conversation = State()

