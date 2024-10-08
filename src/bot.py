from source.telegram_source import TelegramSource
import openai
import os

class Bot:
    def __init__(self, telegram_source: TelegramSource):
        self.telegram_source = telegram_source

    async def run(self):
        try:
            print('Fetching messages...')
            messages = await self.telegram_source.fetch_data()  # Fetch the last 10 messages
            await self.process_messages(messages)
        except Exception as error:
            print('An error occurred while fetching messages:', error)

    async def process_messages(self, messages: list[str]):
        if len(messages) == 0:
            print('No new messages to process.')
            return

        openai.api_key = os.getenv('OPENAI_API_KEY')

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant that summarizes text.'
                },
                {
                    'role': 'user',
                    'content': f'Please summarize the following post: "{messages}"'
                }
            ]
        )

        print('Processing messages:')
        for index, message in enumerate(messages):
            print(f'{index + 1}: {message}')