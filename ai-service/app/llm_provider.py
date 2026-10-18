import httpx
from typing import Dict, Any, Optional
from .config import settings

class LLMProvider:
    """Interface for LLM inference using llama.cpp server."""
    
    def __init__(self):
        self.base_url = settings.llm_base_url
        self.model = settings.llm_model
        self.timeout = settings.llm_timeout
        self.max_tokens = settings.llm_max_tokens
        self.client = httpx.Client(timeout=self.timeout)
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": self.max_tokens,
                    "temperature": 0.7,
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise Exception(f"LLM HTTP error: {e}")
        except Exception as e:
            raise Exception(f"LLM generation failed: {e}")
    
    async def health(self) -> Dict[str, Any]:
        """Check if LLM service is healthy."""
        try:
            response = self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return {
                "status": "healthy",
                "model": self.model,
                "available": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model,
                "available": False,
                "error": str(e)
            }
    
    def close(self):
        """Close HTTP client."""
        self.client.close()
