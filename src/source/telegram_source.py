from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from source.telegram_source import TelegramSource
import openai
import os
from .source import Source

Base = declarative_base()

class Channel(Base):
    __tablename__ = 'channels'
    channelID = Column(String, primary_key=True)
    messageID = Column(Integer)

class Bot(Source):
    def __init__(self, telegram_source: TelegramSource, db_url: str):
        self.telegram_source = telegram_source
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

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

    def get_last_message_id(self, channel_id: str) -> int:
        session = self.Session()
        channel = session.query(Channel).filter_by(channelID=channel_id).first()
        session.close()
        return channel.messageID if channel else 0

    def save_last_message_id(self, channel_id: str, message_id: int):
        session = self.Session()
        channel = session.query(Channel).filter_by(channelID=channel_id).first()
        if channel:
            channel.messageID = message_id
        else:
            channel = Channel(channelID=channel_id, messageID=message_id)
            session.add(channel)
        session.commit()
        session.close()