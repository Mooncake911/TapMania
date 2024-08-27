import sys
import logging
import asyncio
from bot.routers import register_all_handlers
from bot.vars import dp, bot


@dp.startup()
async def on_startup():
    register_all_handlers(dp=dp)


@dp.shutdown()
async def on_shutdown():
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    try:
        logging.info('Bot was launched.')
        asyncio.run(dp.start_polling(bot))

    except KeyboardInterrupt:
        logging.info('Bot was closed.')
