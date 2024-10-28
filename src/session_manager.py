# src/session_manager.py
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from src.logger_config import get_logger
from src.settings import settings

logger = get_logger(__name__)

class SessionManager:
    def __init__(self):
        self.session_string = settings.get('session_string')
        self.session_path = settings.get('session_path', 'session.txt')
        self.api_id = settings.api_id
        self.api_hash = settings.api_hash

    def get_client(self):
        if self.session_string:
            logger.debug("Using session string from settings.")
            session = StringSession(self.session_string)
        elif os.path.exists(self.session_path):
            logger.debug(f"Using session file at {self.session_path}.")
            with open(self.session_path, 'r') as f:
                session_string = f.read().strip()
            session = StringSession(session_string)
        else:
            logger.error("No session string or session file found.")
            raise ValueError("Session string is required.")

        client = TelegramClient(session, self.api_id, self.api_hash)
        return client
