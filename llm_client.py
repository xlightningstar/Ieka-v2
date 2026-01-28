import requests
from settings import LLM_API_KEY

api_url = "https://openrouter.ai/api/v1/chat/completions"
model = "google/gemini-2.0-flash-lite-001"

class LLMClient:
    def __init__(self):
        self.generate_header()

    def load_extra_context(self, filepath="context.txt") -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def generate_header(self):
        self.headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }

    def get_context(self):
        return self.load_extra_context()

    def generate_payload(self, prompt):
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self.get_context()},
                {"role": "user", "content": prompt}
            ]
        }
        return payload

    def get_response(self, prompt):
        payload = self.generate_payload(prompt)
        response = requests.post(api_url, headers=self.headers, json=payload)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]