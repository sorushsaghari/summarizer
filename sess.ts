import { TelegramClient } from 'telegram';
import { StringSession } from 'telegram/sessions';
import * as dotenv from 'dotenv';
import readline from 'readline';
import fs from 'fs';
import path from 'path';

dotenv.config();

const apiId = parseInt(process.env.TELEGRAM_API_ID!, 10);
const apiHash = process.env.TELEGRAM_API_HASH!;
const phoneNumber = process.env.TELEGRAM_PHONE_NUMBER!;
const sessionFile = path.join(__dirname, 'session.txt'); // The file where the session string will be saved

async function getCodeFromUser(): Promise<string> {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    return new Promise<string>((resolve) => {
        rl.question('Please enter the code you received: ', (code) => {
            rl.close();
            resolve(code.trim());
        });
    });
}

async function getPasswordFromUser(): Promise<string> {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    return new Promise<string>((resolve) => {
        rl.question('Please enter your 2FA password (if any): ', (password) => {
            rl.close();
            resolve(password.trim());
        });
    });
}

async function main() {
    const stringSession = new StringSession(''); // Empty string to start with no session
    const client = new TelegramClient(stringSession, apiId, apiHash, {
        connectionRetries: 5,
    });

    try {
        await client.start({
            phoneNumber: async () => phoneNumber,
            password: async () => process.env.TELEGRAM_PASSWORD || await getPasswordFromUser(),
            phoneCode: async () => await getCodeFromUser(),
            onError: (err) => console.error('Telegram login error:', err),
        });

        console.log('You are now connected to Telegram!');

        // Retrieve the session string after login
        const sessionString = client.session.save();

        // Check if sessionString is not void
        if (typeof sessionString === 'string' && sessionString) {
            fs.writeFileSync(sessionFile, sessionString, 'utf-8');
            console.log('Session saved to', sessionFile);
        } else {
            console.error('Failed to save session. Session string is empty or invalid.');
        }
    } catch (error) {
        console.error('Error during Telegram login:', error);
    } finally {
        await client.disconnect();
        console.log('Disconnected from Telegram');
    }
}

main();
