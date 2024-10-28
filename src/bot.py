# src/bot.py
import openai
from ansible_collections.awx.awx.plugins.modules.workflow_job_template import response
from telethon import TelegramClient
from src.logger_config import get_logger
from src.session_manager import SessionManager
from src.settings import settings

logger = get_logger(__name__)

class Bot:
    def __init__(self, sources: list):
        self.sources = sources
        self.private_channel_id = settings.private_channel_id
        self.bot_token = settings.bot_token
        self.openai_api_key = settings.openai_api_key
        openai.api_key = self.openai_api_key

        # Use SessionManager for bot client as well
        self.telegram_client = SessionManager().get_client()
        logger.debug("Bot initialized with provided configuration.")

    async def run(self):
        try:
            await self.telegram_client.start(bot_token=self.bot_token)
            logger.info('Telegram bot client started.')

            logger.info('Fetching data from sources...')
            all_messages_with_refs = []

            # Fetch data from all sources
            for source in self.sources:
                messages_with_refs = await source.fetch_data()
                all_messages_with_refs.extend(messages_with_refs)

            if all_messages_with_refs:
                # Process and send messages
                await self.process_and_send_messages(all_messages_with_refs)
            else:
                logger.info('No new messages to process.')

        except Exception as error:
            logger.error(f'An error occurred in Bot.run: {error}', exc_info=True)
        finally:
            await self.telegram_client.disconnect()
            logger.info('Telegram bot client disconnected.')

    async def process_and_send_messages(self, combined_messages: str):
        try:
            # Use OpenAI to summarize the combined messages
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{'role': 'user', 'content': self.create_prompt(combined_messages)}],
                max_tokens=100,
                temperature=0.5
            )

            summary = response.choices[0].message.content
            logger.info(f'Summary generated.{summary}')

            # Send the summarized message to the private Telegram channel
            await self.send_to_private_channel(summary)
        except Exception as e:
            logger.error(f'An error occurred in process_and_send_messages: {e}', exc_info=True)

    def create_prompt(self, messages_with_refs):
        prompt = (
            "You are an AI assistant specializing in fundamental analysis of financial markets such as crypto and forex.\n"
            "Please perform the following tasks:\n"
            "1. **Categorize** the messages into appropriate categories (e.g., Market News, Technical Analysis, Announcements).\n"
            "2. **Merge** messages that convey the same or similar information.\n"
            "3. **Summarize** the messages in each category, highlighting key points.\n"
            "4. **Provide additional insights** or relevant information that may aid in understanding or analysis.\n"
            "5. **Include references** to the original message sources where applicable.\n\n"
            "Here are the messages:\n"
        )
        for i, (message, reference) in enumerate(messages_with_refs, 1):
            prompt += f"{i}. {message} (Reference: {reference})\n"
        return prompt
    async def send_to_private_channel(self, summary: str):
        try:
            # Send the summarized message to the specified private channel
            entity = await self.telegram_client.get_entity(self.private_channel_id)

            await self.telegram_client.send_message(entity, summary)

            logger.info(f'Summary sent to private channel {self.private_channel_id}')
        except Exception as e:
            logger.error(f'Failed to send summary to private channel: {e}', exc_info=True)
