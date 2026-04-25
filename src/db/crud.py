from sqlalchemy import select, update

from .models import User, async_session


async def get_user_by_tg_id(tg_id: int) -> User | None:
    """Проверяет наличие пользователя в базе данных по tg_id"""
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))
    

async def set_gemini_api(tg_id: int, api_key: str) -> None:
    """Устанавливает API ключ для пользователя в базе данных"""
    async with async_session() as session:
        await session.execute(
            update(User).where(User.tg_id == tg_id).values(gemini_api=api_key)
        )
        await session.commit()


async def set_gemini_model(tg_id: int, model_name: str) -> None:
    """Устанавливает модель для пользователя в базе данных"""
    async with async_session() as session:
        await session.execute(
            update(User).where(User.tg_id == tg_id).values(gemini_model=model_name)
        )
        await session.commit()


async def add_new_user(
    tg_id: int,
    username: str
) -> None:
    """Добавляет нового пользователя в базу данных"""
    async with async_session() as session:
        existing = await session.scalar(
            select(User).where(User.tg_id == tg_id)
        )
        if existing:
            return None
        else:
            new_user = User(
                tg_id=tg_id,
                username=username
            )
        if new_user:
            session.add(new_user)
            await session.commit()