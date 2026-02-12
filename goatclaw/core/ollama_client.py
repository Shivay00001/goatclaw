import aiohttp
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("goatclaw.core.ollama")


class OllamaClient:
    """
    Client for interacting with local Ollama models.
    Local-first, cost-efficient model execution.
    """
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        logger.info(f"OllamaClient initialized with base_url: {base_url}")

    async def list_models(self) -> List[str]:
        """List available Ollama models."""
        url = f"{self.base_url}/api/tags"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def generate(self, model: str, prompt: str, system: Optional[str] = None) -> str:
        """Generate response from local model."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system

        try:
            # Long timeout for local models (can be slow on CPU)
            timeout = aiohttp.ClientTimeout(total=300)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    
                    error_text = await response.text()
                    logger.error(f"Ollama error {response.status}: {error_text}")
                    
                    # Parse error for better message
                    if "more system memory" in error_text or "out of memory" in error_text.lower():
                        raise RuntimeError(
                            f"Model '{model}' requires more RAM than available. "
                            f"Try a smaller model: ollama pull tinyllama"
                        )
                    if response.status == 404:
                        raise RuntimeError(
                            f"Model '{model}' not found. Pull it: ollama pull {model}"
                        )
                    raise RuntimeError(f"Ollama API error {response.status}: {error_text[:200]}")
                    
        except aiohttp.ClientConnectorError:
            raise RuntimeError(
                "Cannot connect to Ollama. Start it: ollama serve"
            )
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to communicate with Ollama: {e}")
            raise RuntimeError(f"Ollama communication error: {e}")

    async def chat(self, model: str, messages: List[Dict[str, str]]) -> str:
        """Chat with local model."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }

        try:
            timeout = aiohttp.ClientTimeout(total=300)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("message", {}).get("content", "")
                    
                    error_text = await response.text()
                    logger.error(f"Ollama chat error {response.status}: {error_text}")
                    
                    if "more system memory" in error_text:
                        raise RuntimeError(
                            f"Model '{model}' requires more RAM. Try: ollama pull tinyllama"
                        )
                    raise RuntimeError(f"Ollama API error {response.status}: {error_text[:200]}")
                    
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to communicate with Ollama: {e}")
            raise RuntimeError(f"Ollama communication error: {e}")


# Global Ollama Client Instance
ollama_client = OllamaClient()
