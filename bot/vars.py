from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties

from config import TELEGRAM_TOKEN


bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode='HTML', link_preview_is_disabled=True),
)

dp = Dispatcher(
    bot=bot
)

