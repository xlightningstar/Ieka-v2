import requests
from src.settings import LLM_API_KEY
from src.config import Config

class LLMClient:
    """Client for interacting with the LLM API."""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        self.system_context = self._load_system_context()
    
    def _load_system_context(self, filepath: str = Config.CONTEXT_FILE_PATH) -> str:
        """Load system context from file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: {filepath} not found. Using empty system context.")
            return ""
    
    def _build_messages(self, history: list = None) -> list:
        """Build the message array for the API request.
        
        Args:
            history: List of previous messages in format [{"role": str, "author": str, "content": str}, ...]
        
        Returns:
            List of messages formatted for the API
        """
        messages = []
        
        # Add system context
        if self.system_context:
            messages.append({
                "role": "system",
                "content": self.system_context
            })
        
        # Add conversation history if available
        if history:
            for msg in history:
                # Format message with author name for context
                content = f"{msg['author']}: {msg['content']}" if msg['role'] == 'user' else msg['content']
                messages.append({
                    "role": msg["role"],
                    "content": content
                })
        
        return messages
    
    def get_response(self, history: list = None) -> str:
        """Get a response from the LLM.
        
        Args:
            prompt: The user's prompt
            history: Optional conversation history
        
        Returns:
            The LLM's response text
        
        Raises:
            requests.HTTPError: If the API request fails
        """
        messages = self._build_messages(history)
        
        payload = {
            "model": Config.MODEL,
            "messages": messages
        }
        
        #response = requests.post(Config.API_URL, headers=self.headers, json=payload)
        #response.raise_for_status()
        
        #data = response.json()
        #return data["choices"][0]["message"]["content"]
        print(messages)
        return "This is a mock response."