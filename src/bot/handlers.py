import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from config import (
	url,
	TARGET_CHAT_ID,
	SEND_DELAY_SECONDS,
	POLL_INTERVAL_SECONDS,
	RETRY_DELAY_SECONDS
)
from keyboards import get_start_keyboard
from parser.parser import HabrParser, set_stop, split_text, stop_event

router = Router()


async def _send_article(message: Message, article: dict[str, str], content: str) -> None:
	"""Отправляет статью в канал по частям с fallback на plain text."""
	title = article["title"].replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
	header = f"*{title}*\n\nСсылка на оригинальную статью: {article['link']}"

	for index, part in enumerate(split_text(content)):
		message_text = f"{header}\n\n{part}" if index == 0 else part

		try:
			await message.bot.send_message(
				chat_id=TARGET_CHAT_ID,
				text=message_text,
			)
		except TelegramBadRequest:
			await message.bot.send_message(
				chat_id=TARGET_CHAT_ID,
				text=message_text.replace("*", "").replace("`", ""),
			)

		await asyncio.sleep(SEND_DELAY_SECONDS)


async def _wait_for_next_article(parser: HabrParser, current_article: dict[str, str]) -> None:
	"""Ждёт появления новой статьи, пока рассылка не будет остановлена."""
	while not stop_event.is_set():
		await asyncio.sleep(POLL_INTERVAL_SECONDS)
		new_article = await parser.get_link()

		if current_article["title"] != new_article["title"]:
			return


async def run_auto_post(message: Message) -> None:
	"""Запускает мониторинг новых статей и публикует их в канал."""
	set_stop(False)
	await message.answer(
		"*Начало рассылки*"
	)

	try:
		while not stop_event.is_set():
			try:
				parser = HabrParser(url=url)
				article = await parser.get_link()
				content = await parser.get_short_content(article["link"])

				await _send_article(message, article, content)
				await _wait_for_next_article(parser, article)
			except Exception as error:
				await message.answer(
					f"*Ошибка рассылки:* {error}"
				)
				await asyncio.sleep(RETRY_DELAY_SECONDS)
	except asyncio.CancelledError:
		pass


@router.message(Command("start"))
async def start_message(message: Message) -> None:
	"""Приветствует пользователя и показывает стартовые кнопки."""
	if not message.from_user:
		return

	await message.answer(
		"*Добро пожаловать в Habr Auto Poster!*",
		reply_markup=get_start_keyboard(),
	)


@router.message(Command("stop_post"))
async def stop_auto_post(message: Message) -> None:
	"""Останавливает рассылку статей."""
	set_stop(True)
	await message.answer(
		"*Рассылка остановлена*"
	)