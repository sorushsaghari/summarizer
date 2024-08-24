// src/index.ts
import 'dotenv/config';
import { TelegramSource } from './src/source/TelegramSource';
import { Bot } from './src/Bot';
import path from 'path';
import {PrismaClient} from "@prisma/client";

// Load environment variables
const telegramApiId = parseInt(process.env.TELEGRAM_API_ID!, 10);
const telegramApiHash = process.env.TELEGRAM_API_HASH!;
const telegramChannelUsername = process.env.TELEGRAM_CHANNEL_USERNAME!;
const sessionFile = path.join(__dirname, 'session.txt'); // Path to the saved session file
const prisma = new PrismaClient()

// Initialize the Telegram source and bot
const telegramSource = new TelegramSource(telegramApiId, telegramApiHash, sessionFile, prisma, telegramChannelUsername);
const bot = new Bot(telegramSource);

// Function to run the bot
async function runBot() {
    try {
        await telegramSource.start();
        await bot.run();
    } catch (error) {
        console.error('Error running bot:', error);
    } finally {
        await telegramSource.close();
    }
}

// Schedule the bot to run every hour
runBot();

