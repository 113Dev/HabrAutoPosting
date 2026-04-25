from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_start_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="AutoPost", callback_data="start_autopost"),
				InlineKeyboardButton(text="Настройки", callback_data="open_settings"),
			],
		]
	)


def get_settings_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Изменить API", callback_data="change_api"),
				InlineKeyboardButton(text="Изменить модель", callback_data="change_model"),
			],
			[
				InlineKeyboardButton(text="Изменить URL", callback_data="change_url"),
				InlineKeyboardButton(text="ID группы", callback_data="change_target_chat_id"),
			],
			[
				InlineKeyboardButton(text="Промпт", callback_data="open_prompt"),
				InlineKeyboardButton(text="Задержка постинга", callback_data="open_delays"),
			],
			[
				InlineKeyboardButton(text="Назад", callback_data="back_to_start"),
			],
		]
	)


def get_prompt_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Изменить промпт", callback_data="change_prompt"),
			],
			[
				InlineKeyboardButton(text="Назад", callback_data="back_to_settings"),
			],
		]
	)


def get_back_to_settings_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Назад", callback_data="back_to_settings"),
			],
		]
	)


def get_back_to_prompt_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Назад", callback_data="back_to_prompt"),
			],
		]
	)


def get_delays_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Интервал проверки", callback_data="change_check_interval"),
			],
			[
				InlineKeyboardButton(text="Время ожидания", callback_data="change_poll_interval"),
			],
			[
				InlineKeyboardButton(text="Назад", callback_data="back_to_settings"),
			],
		]
	)


def get_back_to_delays_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Назад", callback_data="back_to_delays"),
			],
		]
	)
