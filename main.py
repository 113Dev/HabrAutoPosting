import asyncio

from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from config import dp, bot, url

from parser import HabrParser, set_stop, stop_event, split_text


@dp.message(Command("start"))
async def start_message(message: Message) -> None:
	"""Эта функция приветствует пользователя и сообщает как запустить рассылку"""
	if not message.from_user:
		return

	await message.answer(
		"*Добро пожаловать в Berloga Auto Poster! Отправьте /start_post чтобы начать рассылку.*",
		parse_mode="Markdown"
	)


@dp.message(Command("start_post"))
async def start_auto_post(message: Message) -> None:
	"""Эта функция запускает бесконечный цикл мониторинга новых статей и их публикации"""
	set_stop(False)
	await message.answer("*Начало рассылки*", parse_mode="Markdown")

	try:
		while not stop_event.is_set():
			try:
				parser = HabrParser(url=url)
				article = await parser.get_link()
				content = await parser.get_short_content(article["link"])

				title = article['title'].replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')
				header = f"*{title}*\n\nСсылка на оригинальную статью: {article['link']}"

				content_parts = split_text(content)

				for i, part in enumerate(content_parts):
					if i == 0:
						message_text = f"{header}\n\n{part}"
					else:
						message_text = part

					try:
						await bot.send_message(
							chat_id=-1003766155088,
							text=message_text,
							parse_mode="Markdown"
						)
					except TelegramBadRequest:
						await bot.send_message(
							chat_id=-1003766155088,
							text=message_text.replace('*', '').replace('`', '')
						)

					await asyncio.sleep(1)

				while not stop_event.is_set():
					await asyncio.sleep(1800)
					new_article = await parser.get_link()

					if article["title"] != new_article["title"]:
						break
			except Exception as e:
				await message.answer(f"*Ошибка рассылки:* {e}", parse_mode="Markdown")
				await asyncio.sleep(5)
	except asyncio.CancelledError:
		pass


@dp.message(Command("stop_post"))
async def stop_auto_post(message: Message) -> None:
	"""Эта функция останавливает рассылку статей"""
	set_stop(True)
	await message.answer(
		"*Рассылка остановлена*",
		parse_mode="Markdown"
	)


async def main():
	"""Эта функция инициализирует и запускает бота в режиме polling"""
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())