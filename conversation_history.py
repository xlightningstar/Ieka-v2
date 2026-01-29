from collections import deque
from config import Config


class ConversationHistory:
    """Manages conversation history per channel."""
    
    def __init__(self, max_size: int = Config.HISTORY_SIZE, max_chars: int = Config.MAX_HISTORY_CHARS):
        self.max_size = max_size
        self.max_chars = max_chars
        self.histories = {}  # channel_id -> deque of messages
    
    def add_message(self, channel_id: int, author: str, content: str, is_bot: bool = False):
        """Add a message to the channel's history."""
        if channel_id not in self.histories:
            self.histories[channel_id] = deque(maxlen=self.max_size)
        
        role = "assistant" if is_bot else "user"
        self.histories[channel_id].append({
            "role": role,
            "author": author,
            "content": content
        })
    
    def get_history(self, channel_id: int) -> list:
        """Get formatted history for a channel, respecting character limit."""
        if channel_id not in self.histories:
            return []
        
        history = list(self.histories[channel_id])
        
        # Trim history to fit within character limit
        total_chars = sum(len(msg["content"]) for msg in history)
        
        while total_chars > self.max_chars and len(history) > 1:
            # Remove oldest message
            removed = history.pop(0)
            total_chars -= len(removed["content"])
        
        return history
    
    def clear_history(self, channel_id: int):
        """Clear history for a specific channel."""
        if channel_id in self.histories:
            self.histories[channel_id].clear()
