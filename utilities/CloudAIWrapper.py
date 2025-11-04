"""
Cloud AI Wrapper
Provides a unified interface for Gemini and OpenAI APIs.
Defaults to Gemini but allows switching between providers.
"""

import os
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

# Try to import Google Gen AI SDK
try:
    from google.genai import Client as GenAIClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Try to import OpenAI API
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content from a prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class GeminiProvider(AIProvider):
    """Gemini API provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self._available = False
        
        if not GEMINI_AVAILABLE:
            print("Warning: google-genai not installed. Install with: pip install google-genai")
            return
        
        if not self.api_key:
            print("Note: No Gemini API key provided. Set GEMINI_API_KEY environment variable.")
            return
        
        try:
            self.client = GenAIClient(api_key=self.api_key)
            self._available = True
            print("✓ Gemini API configured")
        except Exception as e:
            print(f"Warning: Failed to configure Gemini API: {e}")
            self._available = False
    
    def generate_content(self, prompt: str, model: str = "gemini-2.5-flash", **kwargs) -> str:
        """Generate content using Gemini API."""
        if not self._available or not self.client:
            raise ValueError("Gemini API is not available")
        
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            return ""
        except Exception as e:
            raise ValueError(f"Gemini API error: {e}")
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self._available


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self._available = False
        
        if not OPENAI_AVAILABLE:
            print("Warning: openai not installed. Install with: pip install openai")
            return
        
        if not self.api_key:
            print("Note: No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
            return
        
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
            self._available = True
            print("✓ OpenAI API configured")
        except Exception as e:
            print(f"Warning: Failed to configure OpenAI API: {e}")
            self._available = False
    
    def generate_content(self, prompt: str, model: str = "gpt-4", **kwargs) -> str:
        """Generate content using OpenAI API."""
        if not self._available or not self.client:
            raise ValueError("OpenAI API is not available")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            if response and response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            return ""
        except Exception as e:
            raise ValueError(f"OpenAI API error: {e}")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self._available


class CloudAIWrapper:
    """Unified wrapper for cloud AI services."""
    
    def __init__(self, provider: str = "gemini", 
                 gemini_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        """
        Initialize Cloud AI Wrapper.
        
        Args:
            provider: "gemini" or "openai" (default: "gemini")
            gemini_api_key: Optional Gemini API key
            openai_api_key: Optional OpenAI API key
        """
        self.provider_name = provider.lower()
        self.gemini = GeminiProvider(gemini_api_key)
        self.openai = OpenAIProvider(openai_api_key)
        
        # Select provider
        if self.provider_name == "gemini":
            if self.gemini.is_available():
                self.provider = self.gemini
            elif self.openai.is_available():
                print("Warning: Gemini not available, falling back to OpenAI")
                self.provider = self.openai
                self.provider_name = "openai"
            else:
                raise ValueError("No AI provider is available. Please configure API keys.")
        elif self.provider_name == "openai":
            if self.openai.is_available():
                self.provider = self.openai
            elif self.gemini.is_available():
                print("Warning: OpenAI not available, falling back to Gemini")
                self.provider = self.gemini
                self.provider_name = "gemini"
            else:
                raise ValueError("No AI provider is available. Please configure API keys.")
        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: 'gemini', 'openai'")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate content using the configured provider.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional arguments for the provider
            
        Returns:
            Generated text content
        """
        return self.provider.generate_content(prompt, **kwargs)
    
    def switch_provider(self, provider: str):
        """
        Switch to a different provider.
        
        Args:
            provider: "gemini" or "openai"
        """
        provider = provider.lower()
        if provider == "gemini" and self.gemini.is_available():
            self.provider = self.gemini
            self.provider_name = "gemini"
        elif provider == "openai" and self.openai.is_available():
            self.provider = self.openai
            self.provider_name = "openai"
        else:
            raise ValueError(f"Cannot switch to {provider}: not available")
    
    def is_available(self) -> bool:
        """Check if the current provider is available."""
        return self.provider.is_available()
    
    def get_provider(self) -> str:
        """Get the name of the current provider."""
        return self.provider_name

