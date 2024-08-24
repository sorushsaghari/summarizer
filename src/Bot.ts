// src/Bot.ts
import {TelegramSource} from './source/TelegramSource';
import OpenAI from 'openai';

export class Bot {
    private telegramSource: TelegramSource;

    constructor(telegramSource: TelegramSource) {
        this.telegramSource = telegramSource;
    }

    async run() {
        try {
            console.log('Fetching messages...');
            const messages = await this.telegramSource.fetchData(); // Fetch the last 10 messages
            await this.processMessages(messages);
        } catch (error) {
            console.error('An error occurred while fetching messages:', error);
        }
    }

    private async processMessages(messages: string[]) {
        if (messages.length === 0) {
            console.log('No new messages to process.');
            return;
        }

        const client = new OpenAI({
            apiKey: process.env['OPENAI_API_KEY'], // This is the default and can be omitted
        });

        const chatCompletion = await client.chat.completions.create({
            messages: [
                {
                    role: 'system',
                    content: 'You are a helpful assistant that summarizes text.',
                },
                {
                    role: 'user',
                    content: `Please summarize the following post: "${messages}"`,
                },
            ],
            model: 'gpt-3.5-turbo',
        });

        console.log('Processing messages:');
        messages.forEach((message, index) => {
            console.log(`${index + 1}: ${message}`);
        });
    }
}
