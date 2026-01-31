from dotenv import load_dotenv
import os

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")

if not LLM_API_KEY:
    raise RuntimeError("Missing LLM_API_KEY")