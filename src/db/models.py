from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy import BigInteger

from config import SQLALCHEMY_URL, promt, url, CHECK_NEW_ARTICLE_INTERVAL_SECONDS, POLL_INTERVAL_SECONDS

engine = create_async_engine(SQLALCHEMY_URL) # type: ignore

async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column()
    gemini_api: Mapped[str] = mapped_column(nullable=True)
    gemini_model: Mapped[str] = mapped_column(default="gemini-2.5-flash-lite")
    prompt: Mapped[str] = mapped_column(default=promt)
    url: Mapped[str] = mapped_column(default=url)
    check_interval: Mapped[int] = mapped_column(default=CHECK_NEW_ARTICLE_INTERVAL_SECONDS)
    poll_interval: Mapped[int] = mapped_column(default=POLL_INTERVAL_SECONDS)
    target_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    


async def async_main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)