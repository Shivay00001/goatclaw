"""
DevOS LLM Adapters
Provides unified interface for different LLM providers
"""

import os
import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class LLMAdapter(ABC):
    """Abstract base class for LLM adapters"""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Generate response from LLM"""
        pass


class OllamaAdapter(LLMAdapter):
    """Adapter for Ollama local LLM"""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        super().__init__(model=model, base_url=base_url)
    
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Generate response using Ollama"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama. Is it running? (ollama serve)")
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")


class OpenAIAdapter(LLMAdapter):
    """Adapter for OpenAI API"""
    
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None):
        super().__init__(model=model, api_key=api_key or os.getenv('OPENAI_API_KEY'))
        if not self.api_key:
            raise ValueError("OpenAI API key required")
    
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Generate response using OpenAI"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are DevOS, an AI-native developer assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            raise Exception(f"OpenAI generation failed: {str(e)}")


class AnthropicAdapter(LLMAdapter):
    """Adapter for Anthropic Claude API"""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        super().__init__(model=model, api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        if not self.api_key:
            raise ValueError("Anthropic API key required")
    
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Generate response using Anthropic"""
        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['content'][0]['text']
            
        except Exception as e:
            raise Exception(f"Anthropic generation failed: {str(e)}")


class GeminiAdapter(LLMAdapter):
    """Adapter for Google Gemini API"""
    
    def __init__(self, model: str = "gemini-pro", api_key: Optional[str] = None):
        super().__init__(model=model, api_key=api_key or os.getenv('GOOGLE_API_KEY'))
        if not self.api_key:
            raise ValueError("Google API key required")
    
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Generate response using Gemini"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
            
        except Exception as e:
            raise Exception(f"Gemini generation failed: {str(e)}")


def get_adapter(provider: str, model: str, api_key: Optional[str] = None, 
                base_url: Optional[str] = None) -> LLMAdapter:
    """
    Factory function to get the appropriate LLM adapter
    
    Args:
        provider: LLM provider name (ollama, openai, anthropic, gemini)
        model: Model name
        api_key: API key (optional, can use env vars)
        base_url: Base URL for API (optional, for Ollama)
    
    Returns:
        LLMAdapter instance
    """
    adapters = {
        'ollama': OllamaAdapter,
        'openai': OpenAIAdapter,
        'anthropic': AnthropicAdapter,
        'gemini': GeminiAdapter,
    }
    
    adapter_class = adapters.get(provider.lower())
    if not adapter_class:
        raise ValueError(f"Unsupported provider: {provider}")
    
    if provider.lower() == 'ollama':
        return adapter_class(model=model, base_url=base_url or "http://localhost:11434")
    else:
        return adapter_class(model=model, api_key=api_key)
