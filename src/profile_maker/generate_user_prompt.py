import json
from pathlib import Path
import requests
from .src.settings import LLM_API_KEY
from .src.config import Config

CHAT_FILE = "profile_maker/data/chat_user.txt"
OUTPUT_FILE = "profile_maker/data/user_style_prompt.txt"
CHUNK_SIZE = 200

class UserStyleAnalyzer:
    """Analyze a user's messages and generate a style description."""

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        self.system_context = self._load_system_context()
        self.style_prompt = ""  # progressively updated

    def _load_system_context(self, filepath: str = Config.CHATBOT_CONTEXT_FILEPATH) -> str:
        """Optional system context to include in LLM calls."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: {filepath} not found. Using empty system context.")
            return ""

    def _build_messages(self, new_messages: list) -> list:
        """
        Build the message array for the API request.

        Args:
            new_messages: List of user messages to feed in this chunk

        Returns:
            List of messages formatted for the API
        """
        messages = []

        # Include system context if any
        if self.system_context:
            messages.append({"role": "system", "content": self.system_context})

        # Include current style prompt
        if self.style_prompt:
            messages.append({"role": "system", "content": f"Current user style description:\n{self.style_prompt}"})

        # Add new user messages
        if new_messages:
            content = json.dumps(new_messages, indent=2)
            messages.append({
                "role": "user",
                "content": f"Analyze these messages and update the user's writing style description:\n{content}"
            })

        return messages

    def clean_response(self, s: str) -> str:
        """Remove leading/trailing whitespace."""
        return s.strip()

    def update_style(self, new_messages: list):
        """Send new messages to LLM and update style_prompt."""
        messages = self._build_messages(new_messages)
        payload = {
            "model": Config.MODEL,
            "messages": messages
        }

        response = requests.post(Config.API_URL, headers=self.headers, json=payload)
        response.raise_for_status()

        data = response.json()
        updated_style = data["choices"][0]["message"]["content"]
        self.style_prompt = self.clean_response(updated_style)
        return self.style_prompt

    @staticmethod
    def read_user_messages(file_path: str):
        """Read messages from chat file and strip timestamps/user prefixes."""
        messages = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    # remove timestamp | user: prefix if present
                    if "|" in line:
                        parts = line.split("|", 1)
                        if ":" in parts[1]:
                            _, content = parts[1].split(":", 1)
                            line = content.strip()
                    messages.append(line)
        return messages

    @staticmethod
    def chunk_messages(messages: list, chunk_size: int):
        """Split messages into chunks for incremental processing."""
        return [messages[i:i + chunk_size] for i in range(0, len(messages), chunk_size)]


def main():
    if not Path(CHAT_FILE).exists():
        print(f"User chat file '{CHAT_FILE}' not found.")
        return

    analyzer = UserStyleAnalyzer()
    messages = analyzer.read_user_messages(CHAT_FILE)
    chunks = analyzer.chunk_messages(messages, CHUNK_SIZE)

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} messages)...")
        style_description = analyzer.update_style(chunk)

    # save final style description
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(style_description)

    print(f"Finished! Style description saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()