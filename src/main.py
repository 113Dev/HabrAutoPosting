import asyncio
from typing import Any

from aiogram.types import Message

from bot import callbacks_router, handlers_router
from config import bot, dp


def _patch_message_answer_with_safe_delete() -> None:
    """Патчит Message.answer: отправляет новый ответ и безопасно удаляет исходное сообщение."""
    original_answer = Message.answer

    async def patched_answer(self: Message, *args: Any, **kwargs: Any) -> Message:
        sent_message = await original_answer(self, *args, **kwargs)
        try:
            await self.delete()
        except Exception:
            pass
        return sent_message

    Message.answer = patched_answer  # type: ignore[assignment]


async def main() -> None:
	"""Инициализирует и запускает бота в режиме polling."""
	_patch_message_answer_with_safe_delete()

	dp.include_router(handlers_router)
	dp.include_router(callbacks_router)

	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())