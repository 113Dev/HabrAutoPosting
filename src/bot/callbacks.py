from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.handlers import run_auto_post


router = Router()


@router.callback_query(F.data == "start_autopost")
async def start_autopost_callback(callback: CallbackQuery) -> None:
	"""Запускает автопостинг по нажатию кнопки."""
	await callback.answer()

	if not callback.message:
		return

	await run_auto_post(callback.message)


@router.callback_query(F.data == "open_settings")
async def open_settings_callback(callback: CallbackQuery) -> None:
	"""Показывает заглушку для настроек."""
	await callback.answer()

	if not callback.message:
		return

	await callback.message.answer("Настройки пока недоступны.")
