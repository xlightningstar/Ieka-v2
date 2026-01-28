from dotenv import load_dotenv
import os

load_dotenv()

BOT_API_KEY = os.getenv("BOT_API_KEY")
LLM_API_KEY = os.getenv("LLM_API_KEY")

if not BOT_API_KEY:
    raise RuntimeError("Missing BOT_API_KEY")
if not LLM_API_KEY:
    raise RuntimeError("Missing LLM_API_KEY")