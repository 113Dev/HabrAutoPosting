import asyncio

import httpx

import re

from bs4 import BeautifulSoup

import google.generativeai as gemini

from config import GEMINI_API_KEY, promt


gemini.configure(api_key=str(GEMINI_API_KEY))

stop_event = asyncio.Event()

model = gemini.GenerativeModel(
	"gemini-2.5-flash",
	system_instruction=promt
)

def set_stop(value: bool) -> None:
	"""Эта функция устанавливает или сбрасывает флаг остановки рассылки"""
	if value:
		stop_event.set()
	else:
		stop_event.clear()


def fix_markdown(text: str) -> str:
	"""Эта функция исправляет незакрытые теги Markdown в тексте"""
	lines = text.split('\n')
	fixed_lines = []

	for line in lines:
		if line.strip().startswith('- '):
			fixed_lines.append(line)
			continue

		for pattern, char in [(r'\*\*', '**'), (r'(?<!\*)\*(?!\*)', '*'), (r'`', '`')]:
			count = len(re.findall(pattern, line))
			if count % 2 != 0:
				line = line + char

		fixed_lines.append(line)

	return '\n'.join(fixed_lines)


def limit_text(text: str, max_length: int = 3500) -> str:
	"""Эта функция обрезает текст до максимальной длины с сохранением смысла"""
	if len(text) <= max_length:
		return text

	trimmed = text[:max_length - 3].rsplit(' ', 1)[0]
	return trimmed + "..."


def split_text(text: str, max_length: int = 3500) -> list[str]:
	"""Эта функция разбивает текст на части максимальной длины"""
	if len(text) <= max_length:
		return [text]

	parts = []
	current_part = ""

	for line in text.split('\n'):
		if len(current_part) + len(line) + 1 <= max_length:
			current_part += line + '\n' if current_part else line
		else:
			if current_part:
				parts.append(current_part.rstrip())
			current_part = line

	if current_part:
		parts.append(current_part.rstrip())

	return parts


class HabrParser:
	"""Этот класс отвечает за парсинг статей с Habr"""
	def __init__(
		self,
		url: str
	) -> None:
		self.url = "https://habr.com/" + url.lstrip("/")

	async def get_link(self) -> dict[str, str]:
		"""Эта функция получает ссылку и заголовок последней статьи о Python с Habr"""
		async with httpx.AsyncClient() as client:
			resp = await client.get(self.url)
			resp.raise_for_status()
			
			soup = BeautifulSoup(resp.text, "lxml")
			header = soup.find("h2", class_="tm-title tm-title_h2")
			
			if not header:
				raise ValueError("link is None!")
			
			title = header.get_text(strip=True)
			link_tag = header.find("a", class_="tm-title__link")
			
			if not link_tag or not link_tag.get("href"):
				raise ValueError("link is None!")
				
			return {
				"title": str(title),
				"link": f"https://habr.com{link_tag['href']}"
			}

	async def get_short_content(self, url: str) -> str:
		"""Эта функция парсит текст статьи и сокращает его с помощью Gemini"""
		async with httpx.AsyncClient() as client:
			resp = await client.get(url)
			resp.raise_for_status()

			soup = BeautifulSoup(resp.text, "lxml")
			article_content = soup.find('div', id='post-content-body')

			if not article_content:
				raise ValueError("Пусто!")

			content = article_content.get_text(separator='\n', strip=True)
			response = await model.generate_content_async(content)

			return fix_markdown(str(response.text))