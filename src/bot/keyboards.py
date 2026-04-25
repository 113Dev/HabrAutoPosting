from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_start_keyboard() -> InlineKeyboardMarkup:
	"""Возвращает стартовую клавиатуру с основными действиями."""
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="AutoPost", callback_data="start_autopost"),
				InlineKeyboardButton(text="Настройки", callback_data="open_settings"),
			],
		]
	)