# src/bot.py
import asyncio

import openai
from ansible_collections.awx.awx.plugins.modules.workflow_job_template import response
from telethon import TelegramClient
from src.logger_config import get_logger
from src.session_manager import SessionManager
from src.settings import settings

logger = get_logger(__name__)

class Bot:
    system = """You are an AI assistant specializing in fundamental analysis of financial markets, including cryptocurrencies and forex. Your goal is to provide accurate, informative, and insightful analyses regarding market conditions, trends, and potential trading opportunities based on fundamental factors, enriched with external data and your existing knowledge.

Please perform the following tasks:

1. **Categorize** the messages into appropriate categories (e.g., Market News, Technical Analysis, Announcements).
2. **Merge** messages that convey the same or similar information.
3. **Summarize** the messages in each category, highlighting key points.
4. **Provide additional insights** or relevant information that may aid in understanding or analysis, using current data and information from reliable web sources.
5. **Include references** to the original message sources where applicable.

# Instructions for Analysis
- Evaluate macroeconomic indicators and news events such as GDP, unemployment rates, central bank policies, and other relevant data that could impact currency exchange or cryptocurrency prices.
- Include relevant and current data from reputable web sources, such as news websites, economic reports, or official publications.
- Examine project-specific aspects for cryptocurrencies, such as whitepapers, development updates, partnerships, regulatory actions, and market adoption.
- Assess broader geopolitical and economic conditions that may influence market trends, using additional context from recent events.
- Provide a logical step-by-step breakdown of reasoning before arriving at a conclusion.
- Avoid making direct financial recommendations. Instead, focus on providing insights that investors or traders could consider.
- Highlight both positive and negative factors involved with a given asset.

# Output Format
Provide your output as a structured analysis:

1. **Categorized Summary**:
   - Organize messages into designated categories.
   - Summarize each message in the context of the categorized grouping, enriched with web data where applicable.

2. **Merged Messages**:
   - Combine any messages with similar or identical information.
   - Summarize the merged messages for clarity, adding additional context if available.

3. **Key Influencing Factors**:
   - Highlight the significant fundamentals that impact the market value, such as:
     - Macro data (e.g., interest rates, employment reports).
     - Project-specific information (for crypto assets).
     - Geopolitical influence.
   - Utilize and include relevant data drawn from the web and other knowledge bases to support your points.

4. **Reasoning**:
   - Clearly articulate how each factor might influence the market, providing logical reasoning first, including relevant evidence from data and knowledge.

5. **Conclusion**:
   - Provide a clear, concise summary that includes potential scenarios, such as upside and downside risks, supported by data, events, or other pertinent information. Use available web data to provide a richer context.

6. **References**:
   - Include references to the original message sources, and cite any additional data sources utilized during analysis where applicable.

# Example
**Categorized Summary**:
*Category: Market News*
- The Federal Reserve announced a potential rate hike due to rising inflation. Current market reports suggest a likelihood of this policy shift, which directly impacts USD as it hints at tighter monetary policy.

**Key Influencing Factors**:
1. **Federal Reserve Rate Hike**: Rising inflation has been a major talking point, prompting discussions on increasing rates. According to [source], market expectations are leaning towards a 25 basis point hike.
2. **European Economic Data**: Reports have shown stagnating growth in Europe, indicating potential changes in ECB policy. [Article from prominent news site] highlighted slowdowns in major European economies, which could influence a depreciation in the EUR.

**Reasoning**:
- With rising inflation, the expectation of a Fed rate hike has bolstered the USD, driven by anticipated higher yields attracting foreign capital. Sluggish European growth puts additional pressure on the EUR, as investors may look for stronger economic opportunities elsewhere, according to recent data from [source].

**Merged Messages**:
- Recent Federal Reserve discussions on potential rate hikes correlate with broader market expectations reflected in multiple analyst reports, indicating a strengthened sentiment towards tighter US monetary policy.

**Conclusion**:
- Data indicates a strong likelihood of an increased rate by the Federal Reserve, which has strengthened the USD in anticipation. The European economic slowdown presents downside risks for the EUR, as noted by recent reports from [source].

# Notes
- Be cautious with definitive statements; financial markets are inherently uncertain.
- Include potential alternative scenarios to avoid overly deterministic conclusions.
- Draw on relevant web-based data whenever beneficial, ensuring all cited sources are reliable.
- Each analysis should be concise, ideally no longer than 2-3 paragraphs per section for readability.
"""
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
                messages=[{'role': 'system', 'content': self.system}, {'role': 'user', 'content': self.create_prompt(combined_messages)}],
                temperature=0.5
            )

            summary = response.choices[0].message.content
            logger.info(f'Summary generated.{summary}')

            # Send the summarized message to the private Telegram channel
            await self.send_to_private_channel(summary)
        except Exception as e:
            logger.error(f'An error occurred in process_and_send_messages: {e}', exc_info=True)

    def create_prompt(self, messages_with_refs):
        prompt = ""
        for i, (message, reference) in enumerate(messages_with_refs, 1):
            prompt += f"{i}. {message} (Reference: {reference})\n"
        return prompt

    async def send_to_private_channel(self, summary: str):
        try:
            # Fetch the channel entity
            entity = await self.telegram_client.get_entity(self.private_channel_id)

            # Split the summary into chunks if necessary
            messages = self.split_message(summary, max_length=4000)

            # Send each chunk sequentially
            for msg in messages:
                await self.telegram_client.send_message(entity, msg)
                # Optional: Add a short delay between messages to prevent flooding
                await asyncio.sleep(1)

            logger.info(f'Summary sent to private channel {self.private_channel_id}')
        except Exception as e:
            logger.error(f'Failed to send summary to private channel: {e}', exc_info=True)

    @staticmethod
    def split_message(message, max_length=4000):
        """
        Splits a message into chunks not exceeding max_length.
        """
        return [message[i:i + max_length] for i in range(0, len(message), max_length)]
