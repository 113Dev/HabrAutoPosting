from aiogram.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    waiting_api_key = State()
    waiting_model = State()
    waiting_prompt = State()
    waiting_check_interval = State()
    waiting_poll_interval = State()
    waiting_url = State()
    waiting_target_chat_id = State()