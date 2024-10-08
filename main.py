import os
import asyncio
from src.source.telegram_source import TelegramSource
from src.bot import Bot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dotenv

dotenv.load_dotenv()

# Load environment variables
telegram_api_id = int(os.getenv('TELEGRAM_API_ID'))
telegram_api_hash = os.getenv('TELEGRAM_API_HASH')
telegram_channel_username = os.getenv('TELEGRAM_CHANNEL_USERNAME')
session_file = os.path.join(os.path.dirname(__file__), 'session.txt')  # Path to the saved session file
db_url = os.getenv('DATABASE_URL')

# Initialize the Telegram source and bot
telegram_source = TelegramSource(telegram_api_id, telegram_api_hash, session_file, telegram_channel_username)
bot = Bot(telegram_source, db_url)

# Function to run the bot
async def run_bot():
    try:
        await telegram_source.start()
        await bot.run()
    except Exception as error:
        print('Error running bot:', error)
    finally:
        await telegram_source.close()

# Schedule the bot to run every hour
asyncio.run(run_bot())