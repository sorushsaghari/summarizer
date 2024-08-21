// src/TelegramSource.ts
import { TelegramClient } from 'telegram';
import { StringSession } from 'telegram/sessions';
import fs from 'fs';
import path from 'path';
import { Source } from './Source';

export class TelegramSource implements Source {
    private client: TelegramClient;
    private channelUsername: string;
    private lastMessageIdFile: string;

    constructor(apiId: number, apiHash: string, sessionFile: string, channelUsername: string) {
        let sessionString = '';

        // Check if session file exists and read it
        if (fs.existsSync(sessionFile)) {
            sessionString = fs.readFileSync(sessionFile, 'utf-8');
        } else {
            console.error(`Session file not found at ${sessionFile}. Make sure to run the session utility first.`);
            throw new Error('Session file not found.');
        }

        const stringSession = new StringSession(sessionString); // Load session from file
        this.client = new TelegramClient(stringSession, apiId, apiHash, {
            connectionRetries: 5,
        });
        this.channelUsername = channelUsername;
        this.lastMessageIdFile = path.join(__dirname, `${channelUsername}_lastMessageId.txt`);
    }

    async start() {
        await this.client.connect(); // Connect using the existing session
        console.log('Connected to Telegram using saved session.');
    }

    async fetchData(): Promise<string[]> {
        const channel = await this.client.getEntity(this.channelUsername);
        const lastMessageId = this.getLastMessageId();

        const messages = await this.client.getMessages(channel, {
            minId: lastMessageId,
        });

        if (messages.length > 0) {
            this.saveLastMessageId(messages[0].id);
        }

        return messages.map((message) => message.message);
    }

    async close() {
        await this.client.disconnect();
        console.log('Disconnected from Telegram');
    }

    private getLastMessageId(): number {
        if (fs.existsSync(this.lastMessageIdFile)) {
            const lastMessageId = fs.readFileSync(this.lastMessageIdFile, 'utf-8');
            return parseInt(lastMessageId, 10);
        }
        return 0; // Return 0 if no last message ID is saved, meaning fetch from the latest messages
    }

    private saveLastMessageId(messageId: number) {
        fs.writeFileSync(this.lastMessageIdFile, messageId.toString(), 'utf-8');
    }
}
