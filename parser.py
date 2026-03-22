import asyncio

from bs4 import BeautifulSoup

import google.generativeai as gemini

import requests

import time

from config import GEMINI_API_KEY, BOT_TOKEN

from aiogram import Bot, Dispatcher
from aiogram.filters import Command 
from aiogram.types import Message

bot = Bot(str(BOT_TOKEN))
dp = Dispatcher()

gemini.configure(api_key=str(GEMINI_API_KEY))

model = gemini.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="Ты профессиональный копирайтер на русском, ты должен МАКСИМОЛЬНО сокращать статьи посвещенный it БЕЗ ПОТЕРИ контекста. ФОРМАТИРУЙ ТЕКСТ СТРОГО ПО MARKDOWN!!! ЧТО БЫ РАЗМТКА MARKDOWN РАБОТАЛА БЕЗ ОШИБОК ТОЕСТЬ ЗАКРЫВАЙ ТЕГИ КОТОРЫЕ ОТКРЫВАЕШЬ И БЕЗ ВСЯКИХ '##', И '*' ДЛЯ ОТМЕТКИ ПУНКТОВ Я ОТПРАВЛЯЮ ЭТОТ ТЕКСТ В ТГ ТАКИХ ТЕГОВ БЫТЬ НЕ МОЖЕТ ТАКЖЕ ОТПРАВЛЯЙ МНЕ ИСКЛЮЧИТЕЛЬНО ГОТОВЫЙ ТЕКСТ БЕЗ ТВОИХ ПРИПИСОК ПО ТИПУ'Вот сокращенныя версия статьи' B ТД"
)


def get_link() -> dict[str, str]:
    resp = requests.get("https://habr.com/ru/search/?q=python&target_type=posts&order=date")

    soup = BeautifulSoup(resp.text, "lxml")

    soup = soup.find("h2", class_="tm-title tm-title_h2")

    if soup is None:
        raise ValueError("link is None!")
    else:
        title: str = soup.get_text()

        title_link = soup.find("a", class_="tm-title__link")
        if title_link:
            link = title_link["href"]
        else:
            raise ValueError("link is None!")

    if link:
        finally_link: str = "https://habr.com" + str(link)
    else:
        raise ValueError("link is None!")

    return {
        "title": str(title),
        "link": str(finally_link)
    }


def get_short_content(url: str) -> str:
    response = requests.get(url).text
    soup = BeautifulSoup(response, "lxml")

    article_content = soup.find('div', id='post-content-body')

    if article_content:
        content = article_content.get_text(separator='\n', strip=True)

        response = model.generate_content(content)

        return str(response.text)
    else:
        raise ValueError("Пусто!")


@dp.message(Command("start"))
async def get_dinvoice(message: Message) -> None:
    if not message.from_user:
        return None
    
    await message.answer(
        "*Добро подаловать в Berloga Auto Poster! Отправте '/start_post' что бы начать рассылку.*",
        parse_mode="Markdown"
    )


@dp.message(Command("start_post"))
async def start_auto_post(message: Message) -> None:
    await message.answer("*Начатие Рассылки...*", parse_mode="Markdown")

    while True:
        article: dict[str, str] = get_link()

        content = get_short_content(article["link"])

        try:
            await bot.send_message(
                chat_id=-1003766155088,
                text=f"*{article["title"]}*\n{content}\nСсылка на оригинальную статью: `{article["link"]}`",
                parse_mode="Markdown"
            )
        except:
            await bot.send_message(
                chat_id=-1003766155088,
                text=f"{article["title"]}\n{content}\nСсылка на оригинальную статью: {article["link"]}"
            )

        while True:
            time.sleep(5)

            second_article: dict[str, str] = get_link()
            
            if article["title"] == second_article["title"]:
                print("Error")
                continue
            else:
                break


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())