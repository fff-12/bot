from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCESS_CODE = os.getenv("ACCESS_CODE")
DATABASE = os.getenv("DATABASE", "database.db")
SHEET_NAME = os.getenv("SHEET_NAME", "Bot Clients")
