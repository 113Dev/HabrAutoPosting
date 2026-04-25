from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from db.models import User, async_session


async def get_user_by_tg_id(tg_id: int) -> User | None:
    """Возвращает пользователя по Telegram ID."""
    try:
        async with async_session() as session:
            return await session.scalar(select(User).where(User.tg_id == tg_id))
    except SQLAlchemyError:
        return None


async def get_or_create_user(tg_id: int, username: str) -> User:
    """Возвращает пользователя из БД или создаёт нового."""
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

            if user is None:
                user = User(
                    tg_id=tg_id,
                    username=username,
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user

            if user.username != username:
                user.username = username
                await session.commit()
                await session.refresh(user)

            return user
    except SQLAlchemyError as e:
        raise RuntimeError("Ошибка при работе с базой данных") from e


async def set_gemini_api(tg_id: int, api_key: str) -> None:
    """Устанавливает API ключ для пользователя в базе данных."""
    try:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.tg_id == tg_id).values(gemini_api=api_key)
            )
            await session.commit()
    except SQLAlchemyError as e:
        raise RuntimeError("Ошибка при сохранении API ключа") from e


async def set_gemini_model(tg_id: int, model_name: str) -> None:
    """Устанавливает модель Gemini для пользователя в базе данных."""
    try:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.tg_id == tg_id).values(gemini_model=model_name)
            )
            await session.commit()
    except SQLAlchemyError as e:
        raise RuntimeError("Ошибка при сохранении модели") from e


async def set_prompt(tg_id: int, prompt: str) -> None:
    """Устанавливает prompt для пользователя в базе данных."""
    try:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.tg_id == tg_id).values(prompt=prompt)
            )
            await session.commit()
    except SQLAlchemyError as e:
        raise RuntimeError("Ошибка при сохранении промпта") from e


async def set_url(tg_id: int, url: str) -> None:
    """Устанавливает url для пользователя в базе данных."""
    try:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.tg_id == tg_id).values(url=url)
            )
            await session.commit()
    except SQLAlchemyError as e:
        raise RuntimeError("Ошибка при сохранении URL") from e


async def set_check_interval(tg_id: int, interval: int) -> None:
    """Устанавливает интервал проверки новых статей для пользователя."""
    try:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.tg_id == tg_id).values(check_interval=interval)
            )
            await session.commit()
    except SQLAlchemyError as e:
        raise RuntimeError("Ошибка при сохранении интервала проверки") from e


async def set_poll_interval(tg_id: int, interval: int) -> None:
    """Устанавливает максимальное время ожидания для пользователя."""
    try:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.tg_id == tg_id).values(poll_interval=interval)
            )
            await session.commit()
    except SQLAlchemyError as e:
        raise RuntimeError("Ошибка при сохранении времени ожидания") from e


async def set_target_chat_id(tg_id: int, chat_id: int) -> None:
    """Устанавливает ID целевого чата для пользователя."""
    try:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.tg_id == tg_id).values(target_chat_id=chat_id)
            )
            await session.commit()
    except SQLAlchemyError as e:
        raise RuntimeError("Ошибка при сохранении ID группы") from e