"""
The main project file.
The project is a system of two client-service bots.
The bot client accepts applications and organizes communication
with users who have left applications earlier. the service bot
receives messages from the client bot and organizes the sending
of responses.
"""

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
from handlers.fsm_connect import register_handlers_connect
from handlers.fsm_add_event import register_handlers_add_event


logging.config.fileConfig(fname=r'logger.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

async def start_service_bot():
    bot = Bot(config.SERVICE_TOKEN, parse_mode="HTML")
    bot["bot"] = 'SERVICE_BOT'
    bot["send_to_bot_token"] = config.CLIENT_TOKEN
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_commands(dp)
    register_handlers_connect(dp)

    try:
        await dp.start_polling(dp)
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


async def start_client_bot():
    """
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
    bot["bot"] = 'CLIENT_BOT'
    bot["send_to_bot_token"] = config.SERVICE_TOKEN
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_commands(dp)
    register_catalog_handlers(dp)
    register_handlers_add_event(dp)
    register_handlers_connect(dp)

    try:
        await dp.start_polling(dp)
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


async def main():
    await asyncio.gather(start_service_bot(), start_client_bot())

if __name__ == '__main__':
    try:
        # await asyncio.gather(start_service_bot(), start_client_bot())
        # asyncio.run(start_service_bot())
        asyncio.run(main(),debug=True)
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")



