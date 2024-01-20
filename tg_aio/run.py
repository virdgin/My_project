import sys
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app import main_router, pharmacy_router, clinic_router
from config import TOKEN_BOT


async def main():
    bot = Bot(token=TOKEN_BOT)
    dp = Dispatcher()
    dp.include_router(main_router.router)
    dp.include_routers(pharmacy_router.router, clinic_router.router)
    await dp.start_polling(bot, storage=MemoryStorage())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
