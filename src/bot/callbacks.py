from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards import (
	get_back_to_delays_keyboard,
	get_back_to_prompt_keyboard,
	get_back_to_settings_keyboard,
	get_delays_keyboard,
	get_prompt_keyboard,
	get_settings_keyboard,
	get_start_keyboard,
)
from bot.utils import run_auto_post, render_prompt_text, render_settings_text, _edit_callback_message, _ensure_user
from bot.states import SettingsStates

router = Router()


@router.callback_query(F.data == "start_autopost")
async def start_autopost_callback(callback: CallbackQuery) -> None:
	"""Запускает автопостинг по нажатию кнопки."""
	await callback.answer()

	if not callback.message or not callback.from_user:
		return

	await run_auto_post(callback.message, user_id=callback.from_user.id)


@router.callback_query(F.data == "open_settings")
async def open_settings_callback(callback: CallbackQuery) -> None:
	"""Открывает экран настроек пользователя."""
	await callback.answer()
	user = await _ensure_user(callback)

	if user is None:
		return
	
	await _edit_callback_message(
		callback,
		render_settings_text(user),
		reply_markup=get_settings_keyboard(),
	)


@router.callback_query(F.data == "change_api")
async def change_api_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Переводит пользователя в режим ввода нового API ключа."""
	await callback.answer()
	await state.set_state(SettingsStates.waiting_api_key)

	await _edit_callback_message(
		callback,
		"*Введите новый Gemini API ключ*",
		reply_markup=get_back_to_settings_keyboard(),
	)


@router.callback_query(F.data == "change_model")
async def change_model_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Переводит пользователя в режим ввода новой модели."""
	await callback.answer()
	await state.set_state(SettingsStates.waiting_model)

	await _edit_callback_message(
		callback,
		"*Введите новую Gemini модель*",
		reply_markup=get_back_to_settings_keyboard(),
	)


@router.callback_query(F.data == "change_url")
async def change_url_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Переводит пользователя в режим ввода нового URL."""
	await callback.answer()
	await state.set_state(SettingsStates.waiting_url)

	await _edit_callback_message(
		callback,
		"*Введите новый URL*",
		reply_markup=get_back_to_settings_keyboard(),
	)


@router.callback_query(F.data == "change_target_chat_id")
async def change_target_chat_id_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Переводит пользователя в режим ввода ID группы."""
	await callback.answer()
	await state.set_state(SettingsStates.waiting_target_chat_id)

	await _edit_callback_message(
		callback,
		"*Введите ID группы*\n\nID должен начинаться с минуса, например: -1001234567890",
		reply_markup=get_back_to_settings_keyboard(),
	)


@router.callback_query(F.data == "open_prompt")
async def open_prompt_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Показывает текущий prompt пользователя."""
	await callback.answer()
	await state.clear()

	user = await _ensure_user(callback)
	if user is None:
		return

	await _edit_callback_message(
		callback,
		render_prompt_text(user),
		reply_markup=get_prompt_keyboard(),
	)


@router.callback_query(F.data == "change_prompt")
async def change_prompt_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Переводит пользователя в режим ввода нового prompt."""
	await callback.answer()
	await state.set_state(SettingsStates.waiting_prompt)

	await _edit_callback_message(
		callback,
		"*Отправьте новый промпт одним сообщением*",
		reply_markup=get_back_to_prompt_keyboard(),
	)


@router.callback_query(F.data == "back_to_prompt")
async def back_to_prompt_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Возвращает пользователя на экран prompt."""
	await callback.answer()
	await state.clear()

	user = await _ensure_user(callback)
	if user is None:
		return

	await _edit_callback_message(
		callback,
		render_prompt_text(user),
		reply_markup=get_prompt_keyboard(),
	)


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Возвращает пользователя на экран настроек."""
	await callback.answer()
	await state.clear()

	user = await _ensure_user(callback)
	if user is None:
		return
	
	await _edit_callback_message(
		callback,
		render_settings_text(user),
		reply_markup=get_settings_keyboard(),
	)


@router.callback_query(F.data == "back_to_start")
async def back_to_start_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Возвращает пользователя на стартовый экран."""
	await callback.answer()
	await state.clear()

	await _edit_callback_message(
		callback,
		"*Добро пожаловать в Habr Auto Poster!*",
		reply_markup=get_start_keyboard(),
	)


@router.callback_query(F.data == "open_delays")
async def open_delays_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Открывает меню настройки задержек."""
	await callback.answer()
	await state.clear()

	user = await _ensure_user(callback)
	if user is None:
		return

	text = (
		"*Настройка задержек постинга*\n\n"
		f"Интервал проверки: `{user.check_interval}` сек\n"
		f"Время ожидания: `{user.poll_interval}` сек"
	)

	await _edit_callback_message(
		callback,
		text,
		reply_markup=get_delays_keyboard(),
	)


@router.callback_query(F.data == "change_check_interval")
async def change_check_interval_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Переводит пользователя в режим ввода интервала проверки."""
	await callback.answer()
	await state.set_state(SettingsStates.waiting_check_interval)

	await _edit_callback_message(
		callback,
		"*Введите интервал проверки новых статей в секундах*\n\nНапример: 3600 (1 час)",
		reply_markup=get_back_to_delays_keyboard(),
	)


@router.callback_query(F.data == "change_poll_interval")
async def change_poll_interval_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Переводит пользователя в режим ввода времени ожидания."""
	await callback.answer()
	await state.set_state(SettingsStates.waiting_poll_interval)

	await _edit_callback_message(
		callback,
		"*Введите максимальное время ожидания в секундах*\n\nНапример: 7200 (2 часа)",
		reply_markup=get_back_to_delays_keyboard(),
	)


@router.callback_query(F.data == "back_to_delays")
async def back_to_delays_callback(callback: CallbackQuery, state: FSMContext) -> None:
	"""Возвращает пользователя на экран настройки задержек."""
	await callback.answer()
	await state.clear()

	user = await _ensure_user(callback)
	if user is None:
		return

	text = (
		"*Настройка задержек постинга*\n\n"
		f"Интервал проверки: `{user.check_interval}` сек\n"
		f"Время ожидания: `{user.poll_interval}` сек"
	)

	await _edit_callback_message(
		callback,
		text,
		reply_markup=get_delays_keyboard(),
	)
