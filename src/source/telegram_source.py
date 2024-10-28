# src/source/telegram_source.py
from mpmath import limit

from src.logger_config import get_logger
from src.session_manager import SessionManager
from src.source.models import db, Channel
from src.settings import settings
from src.source.source import Source

logger = get_logger(__name__)

class TelegramSource(Source):
    def __init__(self):
        self.client = SessionManager().get_client()
        self.channels = settings.channels

        # Ensure tables are created
        db.connect()
        db.create_tables([Channel], safe=True)
        db.close()

    async def fetch_data(self) -> list:
        await self.client.connect()
        if not await self.client.is_user_authorized():
            logger.error("Client is not authorized. Please check your session string.")
            raise ValueError("Client is not authorized.")

        new_messages = []

        for channel_id in self.channels:
            last_message_id = self.get_last_message_id(channel_id)
            logger.debug(f"Fetching messages for channel {channel_id} starting from message ID {last_message_id}")

            try:
                # Fetch messages after last_message_id
                latest_message_id = last_message_id
                async for message in self.client.iter_messages(channel_id, min_id=last_message_id, limit=10):
                    if message.text:
                        reference = f"Channel: {channel_id}, Message ID: {message.id}"
                        new_messages.append((message.text, reference))
                        if message.id > latest_message_id:
                            latest_message_id = message.id

                if latest_message_id > last_message_id:
                    self.save_last_message_id(channel_id, latest_message_id)
            except Exception as e:
                logger.error(f"Error fetching messages from {channel_id}: {e}", exc_info=True)

        await self.client.disconnect()
        logger.debug("Disconnected Telegram client")

        return new_messages

    def get_last_message_id(self, channel_id: str) -> int:
        try:
            channel = Channel.get(Channel.channel_id == channel_id)
            last_id = channel.last_message_id or 0
        except Channel.DoesNotExist:
            last_id = 0
        logger.debug(f"Last message ID for channel {channel_id}: {last_id}")
        return last_id

    def save_last_message_id(self, channel_id: str, message_id: int):
        Channel.insert(channel_id=channel_id, last_message_id=message_id).on_conflict(
            update={Channel.last_message_id: message_id},
            conflict_target=[Channel.channel_id]
        ).execute()
        logger.debug(f"Saved last message ID {message_id} for channel {channel_id}")
