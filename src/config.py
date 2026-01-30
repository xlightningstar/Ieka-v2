class Config:
    """Bot configuration constants."""
    
    # Queue settings
    QUEUE_MAX_SIZE = 1
    COOLDOWN_SECONDS = 0
    
    # History settings
    HISTORY_SIZE = 10  # Number of messages to keep in history
    MAX_HISTORY_CHARS = 10000  # Maximum characters for history context
    
    # LLM settings
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = "google/gemini-2.0-flash-lite-001"
    
    # Context file path
    CHATBOT_CONTEXT_FILEPATH = "src/context_files/chatbot_context.txt"
    AGENT_TOOLS_CONTEXT_FILEPATH = "src/context_files/agent_tools_context.txt"