// src/TelegramSource.ts
import {TelegramClient} from 'telegram';
import {StringSession} from 'telegram/sessions';
import fs from 'fs';
import path from 'path';
import {Source} from './Source';
import {Channel, PrismaClient} from "@prisma/client";

export class TelegramSource implements Source {
    private client: TelegramClient;
    private channelUsername: string;
    private lastMessageIdFile: string;
    private dbClient: PrismaClient;

    constructor(apiId: number, apiHash: string, sessionFile: string, dbClient: PrismaClient, channelUsername: string) {
        let sessionString = '';
        this.dbClient = dbClient;
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
        const lastMessageId = await this.getLastMessageId();
        let messages;
        if (lastMessageId == 0) {
            messages = await this.client.getMessages(channel, {limit: 10})
        }else{
            messages = await this.client.getMessages(channel, {limit: 10})
            // messages = await this.client.getMessages(channel, {
            //     minId: lastMessageId,
            // });
        }
        if (messages.length > 0) {
            await this.saveLastMessageId(messages[0].id);
        }

        return messages.map((message) => message.message);
    }

    async close() {
        await this.client.disconnect();
        console.log('Disconnected from Telegram');
    }

    private async getLastMessageId(): Promise<number> {
        const res =  await this.dbClient.channel.findUnique({
            where: {channelID: this.channelUsername},
        });
        return res?.messageID || 0;
    }

    private async saveLastMessageId(messageId: number) {
       await this.dbClient.channel.upsert({
            where: {channelID: this.channelUsername},
            update: {messageID: messageId},
            create: {channelID: this.channelUsername, messageID: messageId},
        });
    }
}
