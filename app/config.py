"""Application settings for the Inquisitors chatbot."""

import os

from dotenv import load_dotenv


load_dotenv()


APP_NAME = "Inquisitors AI Assistant"
APP_VERSION = "1.0.0"
API_PREFIX = "/api"
MAX_MESSAGE_LENGTH = 4000
DEFAULT_SESSION_ID = "default-session"
ALLOWED_ORIGINS = [
	origin.strip()
	for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
	if origin.strip()
]
