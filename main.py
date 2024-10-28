# main.py
import asyncio
from src.bot import Bot
from src.source.telegram_source import TelegramSource
from src.logger_config import setup_logging

def main():
    setup_logging()

    sources = [TelegramSource()]
    bot = Bot(sources)

    asyncio.run(bot.run())

if __name__ == '__main__':
    main()