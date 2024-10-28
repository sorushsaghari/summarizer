import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import logging
logging.basicConfig(level=logging.DEBUG)
# Load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

# Get environment variables
API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE_NUMBER = os.getenv('TELEGRAM_PHONE_NUMBER')
SESSION_FILE = 'session.txt'  # The file where the session string will be saved

# Helper function to get the 2FA password from the user
async def get_password_from_user():
    return input('Please enter your 2FA password (if any): ').strip()

# Helper function to get the verification code from the user
async def get_code_from_user():
    return input('Please enter the code you received: ').strip()

async def main():
    # Check if there's already a saved session
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as file:
            session_string = file.read().strip()
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
    else:
        client = TelegramClient(StringSession(''), API_ID, API_HASH)  # Start with no session

    # Start the client and handle the login process
    await client.connect()

    if not await client.is_user_authorized():
        try:
            # If session is not authorized, prompt for phone number and code
            res =  await client.send_code_request(PHONE_NUMBER)
            print(res)
            code = await get_code_from_user()

            # Some accounts also have a 2FA password
            try:
                await client.sign_in(PHONE_NUMBER, code)
            except Exception as e:
                if 'password' in str(e):
                    password = await get_password_from_user()
                    await client.sign_in(password=password)

            # Save the session after a successful login
            session_string = client.session.save()
            with open(SESSION_FILE, 'w') as file:
                file.write(session_string)
            print(f"Session saved to {SESSION_FILE}")

        except Exception as e:
            print(f"Error during Telegram login: {e}")
            return

    print('You are now connected to Telegram!')

    # Do your tasks here, like sending or receiving messages

    await client.disconnect()
    print('Disconnected from Telegram')

if __name__ == '__main__':
    asyncio.run(main())
