import asyncio
from typing import Any

import httpx

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery

from ai.service import UserGeminiService, get_missing_user_ai_settings
from bot.keyboards import (
    get_settings_keyboard
)
from config import (
    RETRY_DELAY_SECONDS,
    SEND_DELAY_SECONDS,
    url
)
from db.crud import (
    get_or_create_user, 
    get_user_by_tg_id
)
from db.models import User
from parser.parser import HabrParser, set_stop, split_text, stop_event

router = Router()


def _escape_markdown(text: str) -> str:
    return text.replace("\\", "\\\\").replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")


def _mask_api_key(api_key: str | None) -> str:
    if not api_key:
        return "не указан"
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return f"{api_key[:4]}...{api_key[-4:]}"


def render_settings_text(user: User) -> str:
    return (
        "*Добро пожаловать в настройки*\n\n"
        f"ID пользователя: `{user.tg_id}`\n"
        f"URL: `{user.url}`\n"
        f"ID группы: `{user.target_chat_id}`\n"
        f"Gemini модель: `{_escape_markdown(user.gemini_model)}`\n"
        f"API ключ: `{_escape_markdown(_mask_api_key(user.gemini_api))}`"
    )


def render_prompt_text(user: User) -> str:
    return (
        "*Текущий промпт*\n\n"
        f"{_escape_markdown(user.prompt)}"
    )


async def _edit_callback_message(callback: CallbackQuery, text: str, **kwargs: Any) -> None:
    """Безопасно редактирует текущее сообщение callback-запроса."""
    if not callback.message:
        return
    await callback.message.edit_text(text, **kwargs)


async def _ensure_user(callback: CallbackQuery):
    if not callback.from_user:
        return None
    return await get_or_create_user(
        tg_id=callback.from_user.id,
        username=callback.from_user.username or str(callback.from_user.id),
    )


async def _send_article(message: Message, article: dict[str, str], content: str, target_chat_id: int) -> None:
    """Отправляет статью в канал по частям с fallback на plain text."""
    title = article["title"].replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
    header = f"*{title}*\n\nСсылка на оригинальную статью: {article['link']}"

    for index, part in enumerate(split_text(content)):
        message_text = f"{header}\n\n{part}" if index == 0 else part

        try:
            await message.bot.send_message(
                chat_id=target_chat_id,
                text=message_text,
            )
        except TelegramBadRequest:
            await message.bot.send_message(
                chat_id=target_chat_id,
                text=message_text.replace("*", "").replace("`", ""),
            )

        await asyncio.sleep(SEND_DELAY_SECONDS)


async def _wait_for_next_article(
    parser: HabrParser,
    current_article: dict[str, str],
    check_interval_seconds: int,
    poll_interval_seconds: int
) -> None:
    """Ждёт появления новой статьи, пока рассылка не будет остановлена."""
    elapsed = 0
    check_interval = 10

    while not stop_event.is_set() and elapsed < poll_interval_seconds:
        await asyncio.sleep(check_interval)
        elapsed += check_interval

        if elapsed % check_interval_seconds == 0:
            try:
                new_article = await parser.get_link()
                if current_article["title"] != new_article["title"]:
                    return
            except Exception:
                pass  


async def run_auto_post(message: Message, user_id: int | None = None) -> None:
    """Запускает мониторинг новых статей и публикует их в канал."""
    user = None
    tg_id = user_id or (message.from_user.id if message.from_user else None)

    if tg_id:
        user = await get_user_by_tg_id(tg_id)
        if not user and message.from_user:
            user = await get_or_create_user(
                tg_id=message.from_user.id,
                username=message.from_user.username or str(message.from_user.id),
            )

    missing_settings = get_missing_user_ai_settings(user)
    if missing_settings:
        await message.answer(
            "*Автопост нельзя запустить.*\n\n"
            f"Не заполнены: {', '.join(missing_settings)}.\n"
            "Откройте настройки и заполните их.",
            reply_markup=get_settings_keyboard(),
        )
        return

    set_stop(False)
    await message.answer("*Начало рассылки*\n\nЧтобы остановить рассылку, отправьте 'Стоп'")

    try:
        while not stop_event.is_set():
            try:
                if tg_id:
                    user = await get_user_by_tg_id(tg_id)

                missing_settings = get_missing_user_ai_settings(user)
                if missing_settings:
                    await message.answer(
                        "*Автопост остановлен.*\n\n"
                        f"Не заполнены: {', '.join(missing_settings)}.",
                        reply_markup=get_settings_keyboard(),
                    )
                    set_stop(True)
                    return

                ai_service = UserGeminiService.from_user(user)
                parser = HabrParser(
                    url=user.url if user.url else url,
                    ai_service=ai_service,
                )
                article = await parser.get_link()
                content = await parser.get_short_content(article["link"])

                await _send_article(message, article, content, user.target_chat_id)

                while not stop_event.is_set():
                    await _wait_for_next_article(
                        parser,
                        article,
                        user.check_interval,
                        user.poll_interval
                    )

                    new_article = await parser.get_link()
                    if new_article["title"] != article["title"]:
                        article = new_article
                        break
            except (httpx.HTTPError, httpx.TimeoutException):
                await message.answer("*Ошибка сети:* не удалось получить данные с Habr")
                await asyncio.sleep(RETRY_DELAY_SECONDS)
            except ValueError:
                await message.answer("*Ошибка парсинга:* не удалось обработать статью")
                await asyncio.sleep(RETRY_DELAY_SECONDS)
            except Exception:
                await message.answer(f"*Произошла ошибка, повторная попытка через {RETRY_DELAY_SECONDS} сек*")
                await asyncio.sleep(RETRY_DELAY_SECONDS)
    except asyncio.CancelledError:
        pass