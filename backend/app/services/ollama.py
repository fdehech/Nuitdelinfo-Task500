import httpx
from fastapi import HTTPException
from app.core.config import settings

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_API_URL
        self.model = "llama3.1" # Default model

    async def analyze_text(self, text: str):
        """
        Sends text to Ollama for summarization and tagging.
        """
        prompt = f"""
        Analyze the following document text and provide:
        1. A brief summary (max 2 sentences).
        2. A list of 5 relevant tags.
        
        Format the output as JSON with keys 'summary' and 'tags'.
        
        Text:
        {text[:2000]} 
        """
        # Truncate text to avoid context limit issues
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json" 
                    },
                    timeout=60.0
                )
                resp.raise_for_status()
                result = resp.json()
                return result.get("response", "{}")
            except Exception as e:
                print(f"Ollama Error: {e}")
                raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {e}")

    async def chat(self, messages: list):
        """
        Sends chat messages to Ollama.
        """
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False
                    },
                    timeout=60.0
                )
                resp.raise_for_status()
                result = resp.json()
                return result.get("message", {}).get("content", "")
            except Exception as e:
                print(f"Ollama Chat Error: {e}")
                raise HTTPException(status_code=503, detail=f"Ollama chat service unavailable: {e}")

ollama_service = OllamaService()
