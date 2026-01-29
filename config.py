class Config:
    """Bot configuration constants."""
    QUEUE_MAX_SIZE = 1
    COOLDOWN_SECONDS = 0
    HISTORY_SIZE = 10  # Number of messages to keep in history
    MAX_HISTORY_CHARS = 10000  # Maximum characters for history context
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = "google/gemini-2.0-flash-lite-001"
    CONTEXT_FILE_PATH = "context.txt"