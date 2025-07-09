"""
LLM Provider Implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
import openai
import anthropic
import logging
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self.setup_client()
    
    @abstractmethod
    def setup_client(self):
        """Setup the API client"""
        pass
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from the LLM"""
        pass
    
    @abstractmethod
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from the LLM"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API Provider"""
    
    def setup_client(self):
        """Setup OpenAI client"""
        try:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from OpenAI"""
        try:
            start_time = datetime.now()
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "execution_time": execution_time,
                "provider": "openai"
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI"""
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]


class AnthropicProvider(BaseLLMProvider):
    """Anthropic API Provider"""
    
    def setup_client(self):
        """Setup Anthropic client"""
        try:
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            logger.info("Anthropic client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-sonnet-20240229",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Anthropic"""
        try:
            start_time = datetime.now()
            
            # Convert messages format for Anthropic
            system_message = ""
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = await self.client.messages.create(
                model=model,
                messages=anthropic_messages,
                system=system_message if system_message else anthropic.NOT_GIVEN,
                max_tokens=kwargs.get("max_tokens", 1000),
                **{k: v for k, v in kwargs.items() if k != "max_tokens"}
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                "content": response.content[0].text,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "model": response.model,
                "execution_time": execution_time,
                "provider": "anthropic"
            }
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-sonnet-20240229",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from Anthropic"""
        try:
            # Convert messages format for Anthropic
            system_message = ""
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            async with self.client.messages.stream(
                model=model,
                messages=anthropic_messages,
                system=system_message if system_message else anthropic.NOT_GIVEN,
                max_tokens=kwargs.get("max_tokens", 1000),
                **{k: v for k, v in kwargs.items() if k != "max_tokens"}
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get available Anthropic models"""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]