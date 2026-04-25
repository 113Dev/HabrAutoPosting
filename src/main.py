import asyncio

from bot import callbacks_router, handlers_router
from db.models import async_main
from config import bot, dp


async def main() -> None:
    """Инициализирует и запускает бота в режиме polling."""
    await async_main()

    dp.include_router(handlers_router)
    dp.include_router(callbacks_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())