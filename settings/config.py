import os

from dotenv import load_dotenv

load_dotenv()


class ConfigBot:
    TOKEN = os.getenv("TOKEN")


NUMBER = os.getenv("NUMBER")
TELEGRAM = os.getenv("TELEGRAM")
INSTAGRAM = os.getenv("INSTAGRAM")
DEVELOPMENT = os.getenv("DEVELOPMENT")
