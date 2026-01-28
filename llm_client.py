import requests
from settings import LLM_API_KEY

api_url = "https://openrouter.ai/api/v1/chat/completions"

class llm_client:
    def __init__(self):
        self.generate_header()

    def generate_header(self):
        self.headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }

    def generate_payload(self):
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Explain virtual environments in Python."}
            ]
        }
        return payload

    def get_response(self):
        payload = self.generate_payload()
        response = requests.post(api_url, headers=self.headers, json=payload)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]