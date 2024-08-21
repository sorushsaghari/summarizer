// src/Bot.ts
import { TelegramSource } from './source/TelegramSource';

export class Bot {
    private telegramSource: TelegramSource;

    constructor(telegramSource: TelegramSource) {
        this.telegramSource = telegramSource;
    }

    async run() {
        try {
            console.log('Fetching messages...');
            const messages = await this.telegramSource.fetchData(); // Fetch the last 10 messages
            this.processMessages(messages);
        } catch (error) {
            console.error('An error occurred while fetching messages:', error);
        }
    }

    private processMessages(messages: string[]) {
        if (messages.length === 0) {
            console.log('No new messages to process.');
            return;
        }

        console.log('Processing messages:');
        messages.forEach((message, index) => {
            console.log(`${index + 1}: ${message}`);
            // Here you can add any logic you need to process the messages
            // For example, saving to a database, sending to another API, etc.
        });
    }
}
