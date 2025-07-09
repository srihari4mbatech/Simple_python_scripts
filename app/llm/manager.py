"""
LLM Manager for handling multiple providers
"""

from typing import Dict, List, Optional, Any, AsyncGenerator
import logging

from .providers import OpenAIProvider, AnthropicProvider, BaseLLMProvider
from app.config import settings, validate_llm_apis

logger = logging.getLogger(__name__)


class LLMManager:
    """Manager class for handling multiple LLM providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.initialize_providers()
    
    def initialize_providers(self):
        """Initialize available LLM providers based on configuration"""
        available_apis = validate_llm_apis()
        
        # Initialize OpenAI provider if API key is available
        if available_apis.get("openai") and settings.openai_api_key:
            try:
                self.providers["openai"] = OpenAIProvider(settings.openai_api_key)
                logger.info("OpenAI provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI provider: {e}")
        
        # Initialize Anthropic provider if API key is available
        if available_apis.get("anthropic") and settings.anthropic_api_key:
            try:
                self.providers["anthropic"] = AnthropicProvider(settings.anthropic_api_key)
                logger.info("Anthropic provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic provider: {e}")
        
        if not self.providers:
            logger.warning("No LLM providers were initialized. Please check your API keys.")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_provider(self, provider_name: str) -> Optional[BaseLLMProvider]:
        """Get a specific provider by name"""
        return self.providers.get(provider_name)
    
    def get_available_models(self, provider_name: Optional[str] = None) -> Dict[str, List[str]]:
        """Get available models for all or specific provider"""
        if provider_name:
            provider = self.get_provider(provider_name)
            if provider:
                return {provider_name: provider.get_available_models()}
            return {}
        
        models = {}
        for name, provider in self.providers.items():
            models[name] = provider.get_available_models()
        return models
    
    async def generate_response(
        self,
        provider_name: str,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using specified provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not available")
        
        return await provider.generate_response(messages, model, **kwargs)
    
    async def stream_response(
        self,
        provider_name: str,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response using specified provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not available")
        
        async for chunk in provider.stream_response(messages, model, **kwargs):
            yield chunk
    
    def get_default_provider(self) -> Optional[str]:
        """Get the default provider (first available)"""
        providers = self.get_available_providers()
        return providers[0] if providers else None
    
    def get_recommended_model(self, provider_name: str, task_type: str = "general") -> Optional[str]:
        """Get recommended model for a given provider and task type"""
        provider = self.get_provider(provider_name)
        if not provider:
            return None
        
        models = provider.get_available_models()
        if not models:
            return None
        
        # Define recommended models by task type
        recommendations = {
            "openai": {
                "general": "gpt-3.5-turbo",
                "complex": "gpt-4",
                "fast": "gpt-3.5-turbo",
                "creative": "gpt-4"
            },
            "anthropic": {
                "general": "claude-3-sonnet-20240229",
                "complex": "claude-3-opus-20240229",
                "fast": "claude-3-haiku-20240307",
                "creative": "claude-3-opus-20240229"
            }
        }
        
        provider_recommendations = recommendations.get(provider_name, {})
        recommended = provider_recommendations.get(task_type, models[0])
        
        # Return the recommended model if available, otherwise return first available
        return recommended if recommended in models else models[0]
    
    async def chat_completion(
        self,
        user_message: str,
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Simplified chat completion interface
        
        Args:
            user_message: The user's message
            provider_name: LLM provider to use (auto-select if None)
            model: Model to use (auto-select if None)
            conversation_history: Previous conversation messages
            system_prompt: System prompt to use
            stream: Whether to stream the response
            **kwargs: Additional arguments for the LLM API
        """
        # Auto-select provider if not specified
        if not provider_name:
            provider_name = self.get_default_provider()
            if not provider_name:
                raise ValueError("No LLM providers are available")
        
        # Auto-select model if not specified
        if not model:
            model = self.get_recommended_model(provider_name, "general")
            if not model:
                raise ValueError(f"No models available for provider '{provider_name}'")
        
        # Build messages list
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        if stream:
            return self.stream_response(provider_name, messages, model, **kwargs)
        else:
            return await self.generate_response(provider_name, messages, model, **kwargs)


# Global LLM manager instance
llm_manager = LLMManager()