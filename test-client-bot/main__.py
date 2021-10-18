import logging.config

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import config
from db.base import Base
from handlers.commands import register_commands
from handlers.catalog import register_catalog_handlers
from handlers.fsm_connect import register_handlers_connect_to_owner
from handlers.fsm_add_event import register_handlers_add_event

logging.config.fileConfig(fname=r'logger.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


async def main():
    """
    Main function.
    Since the work is a test one, the SQLite database and Memory storage are selected.
    In real conditions, other databases should be used, for example MySQL and Redis.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    bot = Bot(config.CLIENT_TOKEN, parse_mode="HTML")
    bot["db"] = async_sessionmaker
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_commands(dp)
    register_handlers_connect_to_owner(dp)
    register_catalog_handlers(dp)
    register_handlers_add_event(dp)

    try:
        await dp.start_polling(dp)
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")

    