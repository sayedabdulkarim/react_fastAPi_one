import requests
import httpx
from typing import List, Dict

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self._base_url = base_url

    async def list_models(self) -> List[Dict]:
        """Fetch all available models from Ollama"""
        try:
            response = requests.get(f"{self._base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    async def generate_response(self, model: str, prompt: str) -> str:
        """Generate response from the selected model"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={"model": model, "prompt": prompt}
            )
            if response.status_code == 200:
                return response.json()["response"]
            raise Exception(f"Failed to generate response: {response.text}")

# Generated by Copilot
