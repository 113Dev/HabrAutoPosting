from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ai.service import get_missing_user_ai_settings
from bot.utils import render_prompt_text, render_settings_text
from bot.keyboards import get_prompt_keyboard, get_settings_keyboard, get_start_keyboard, get_delays_keyboard
from bot.states import SettingsStates
from db.crud import (
    get_or_create_user,
	get_user_by_tg_id,
	set_check_interval,
	set_gemini_api,
	set_gemini_model,
	set_poll_interval,
	set_prompt,
	set_target_chat_id,
	set_url
)
from parser.parser import set_stop

router = Router()


@router.message(Command("start"))
async def start_message(message: Message) -> None:
	"""Приветствует пользователя, создаёт его в БД и показывает стартовые кнопки."""
	if not message.from_user:
		return

	user = await get_or_create_user(
		tg_id=message.from_user.id,
		username=message.from_user.username or str(message.from_user.id),
	)

	missing_settings = get_missing_user_ai_settings(user)
	warning_text = ""
	if missing_settings:
		warning_text = (
			"\n\n*Не заполнены настройки:* "
			f"{', '.join(missing_settings)}.\n"
			"Перед запуском автопоста откройте настройки."
		)

	await message.answer(
		f"*Добро пожаловать в Habr Auto Poster!*{warning_text}",
		reply_markup=get_start_keyboard(),
	)


@router.message(F.text.lower() == "стоп")
async def stop_auto_post(message: Message) -> None:
	"""Останавливает рассылку статей."""
	set_stop(True)
	await message.answer(
		"*Рассылка остановлена*",
		reply_markup=get_start_keyboard()
	)


@router.message(SettingsStates.waiting_url, F.text)
async def save_url(message: Message, state: FSMContext) -> None:
	"""Сохраняет новый URL пользователя."""
	if not message.from_user or not message.text:
		return

	url = message.text.strip().removeprefix("https://habr.com/").removeprefix("habr.com/")

	await set_url(message.from_user.id, url)
	await state.clear()

	user = await get_user_by_tg_id(message.from_user.id)
	if user is None:
		return

	await message.answer(
		render_settings_text(user),
		reply_markup=get_settings_keyboard(),
	)


@router.message(SettingsStates.waiting_api_key, F.text)
async def save_api_key(message: Message, state: FSMContext) -> None:
	"""Сохраняет новый API ключ пользователя."""
	if not message.from_user or not message.text:
		return

	await set_gemini_api(message.from_user.id, message.text.strip())
	await state.clear()

	user = await get_user_by_tg_id(message.from_user.id)
	if user is None:
		return

	await message.answer(
		render_settings_text(user),
		reply_markup=get_settings_keyboard(),
	)


@router.message(SettingsStates.waiting_model, F.text)
async def save_model(message: Message, state: FSMContext) -> None:
	"""Сохраняет новую Gemini модель пользователя."""
	if not message.from_user or not message.text:
		return

	await set_gemini_model(message.from_user.id, message.text.strip())
	await state.clear()

	user = await get_user_by_tg_id(message.from_user.id)
	if user is None:
		return

	await message.answer(
		render_settings_text(user),
		reply_markup=get_settings_keyboard(),
	)


@router.message(SettingsStates.waiting_prompt, F.text)
async def save_prompt(message: Message, state: FSMContext) -> None:
	"""Сохраняет новый prompt пользователя."""
	if not message.from_user or not message.text:
		return

	await set_prompt(message.from_user.id, message.text.strip())
	await state.clear()

	user = await get_user_by_tg_id(message.from_user.id)
	if user is None:
		return

	await message.answer(
		render_prompt_text(user),
		reply_markup=get_prompt_keyboard(),
	)


@router.message(SettingsStates.waiting_check_interval, F.text)
async def save_check_interval(message: Message, state: FSMContext) -> None:
	"""Сохраняет интервал проверки новых статей."""
	if not message.from_user or not message.text:
		return

	try:
		interval = int(message.text.strip())
		if interval < 10:
			await message.answer("*Ошибка:* интервал должен быть не менее 10 секунд")
			return

		await set_check_interval(message.from_user.id, interval)
		await state.clear()

		user = await get_user_by_tg_id(message.from_user.id)
		if user is None:
			return

		text = (
			"*Настройка задержек постинга*\n\n"
			f"Интервал проверки: `{user.check_interval}` сек\n"
			f"Время ожидания: `{user.poll_interval}` сек"
		)

		await message.answer(text, reply_markup=get_delays_keyboard())
	except ValueError:
		await message.answer("*Ошибка:* введите число")


@router.message(SettingsStates.waiting_poll_interval, F.text)
async def save_poll_interval(message: Message, state: FSMContext) -> None:
	"""Сохраняет максимальное время ожидания."""
	if not message.from_user or not message.text:
		return

	try:
		interval = int(message.text.strip())
		if interval < 60:
			await message.answer("*Ошибка:* время ожидания должно быть не менее 60 секунд")
			return

		await set_poll_interval(message.from_user.id, interval)
		await state.clear()

		user = await get_user_by_tg_id(message.from_user.id)
		if user is None:
			return

		text = (
			"*Настройка задержек постинга*\n\n"
			f"Интервал проверки: `{user.check_interval}` сек\n"
			f"Время ожидания: `{user.poll_interval}` сек"
		)

		await message.answer(text, reply_markup=get_delays_keyboard())
	except ValueError:
		await message.answer("*Ошибка:* введите число")

@router.message(SettingsStates.waiting_target_chat_id, F.text)
async def save_target_chat_id(message: Message, state: FSMContext) -> None:
	"""Сохраняет ID целевого чата."""
	if not message.from_user or not message.text:
		return

	try:
		chat_id = int(message.text.strip())
		if chat_id >= 0:
			await message.answer("*Ошибка:* ID группы должен начинаться с минуса")
			return

		await set_target_chat_id(message.from_user.id, chat_id)
		await state.clear()

		user = await get_user_by_tg_id(message.from_user.id)
		if user is None:
			return

		await message.answer(
			render_settings_text(user),
			reply_markup=get_settings_keyboard(),
		)
	except ValueError:
		await message.answer("*Ошибка:* введите число")
