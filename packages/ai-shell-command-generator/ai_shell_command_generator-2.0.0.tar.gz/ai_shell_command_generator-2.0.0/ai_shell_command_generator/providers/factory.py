"""Factory for creating AI provider instances."""

from typing import Optional
from ai_shell_command_generator.providers.base import BaseProvider


class ProviderFactory:
    """Factory for creating AI provider instances."""
    
    @staticmethod
    def create_provider(
        provider_name: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> BaseProvider:
        """
        Create a provider instance based on configuration.
        
        Args:
            provider_name: 'anthropic', 'openai', or 'ollama'
            model: Specific model to use
            api_key: API key (for cloud providers)
            **kwargs: Additional provider-specific arguments
        
        Returns:
            BaseProvider instance
            
        Raises:
            ValueError: If provider_name is not recognized
            ImportError: If required dependencies are not installed
        """
        providers = {
            'anthropic': ProviderFactory._create_anthropic_provider,
            'openai': ProviderFactory._create_openai_provider,
            'ollama': ProviderFactory._create_ollama_provider,
        }
        
        if provider_name.lower() not in providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        create_func = providers[provider_name.lower()]
        
        # Handle model defaults
        if not model:
            model = ProviderFactory.get_default_model(provider_name)
        
        return create_func(model=model, api_key=api_key, **kwargs)
    
    @staticmethod
    def _create_anthropic_provider(model: str, api_key: Optional[str] = None, **kwargs) -> BaseProvider:
        """Create Anthropic provider."""
        try:
            from ai_shell_command_generator.providers.anthropic_provider import AnthropicProvider
            return AnthropicProvider(model=model, api_key=api_key, **kwargs)
        except ImportError as e:
            raise ImportError(f"Anthropic provider requires anthropic package: {e}")
    
    @staticmethod
    def _create_openai_provider(model: str, api_key: Optional[str] = None, **kwargs) -> BaseProvider:
        """Create OpenAI provider."""
        try:
            from ai_shell_command_generator.providers.openai_provider import OpenAIProvider
            return OpenAIProvider(model=model, api_key=api_key, **kwargs)
        except ImportError as e:
            raise ImportError(f"OpenAI provider requires openai package: {e}")
    
    @staticmethod
    def _create_ollama_provider(model: str, api_key: Optional[str] = None, **kwargs) -> BaseProvider:
        """Create Ollama provider."""
        try:
            from ai_shell_command_generator.providers.ollama_provider import OllamaProvider
            return OllamaProvider(model=model, **kwargs)
        except ImportError as e:
            raise ImportError(f"Ollama provider requires ollama package: {e}")
    
    @staticmethod
    def get_default_model(provider_name: str) -> str:
        """Get default model for a provider."""
        defaults = {
            'anthropic': 'claude-sonnet-4-5-20250929',
            'openai': 'gpt-5-mini',
            'ollama': 'gpt-oss:latest',
        }
        return defaults.get(provider_name.lower(), '')
    
    @staticmethod
    def list_providers() -> list[str]:
        """List all available providers."""
        return ['anthropic', 'openai', 'ollama']
    
    @staticmethod
    def is_provider_available(provider_name: str) -> bool:
        """Check if a provider is available (dependencies installed)."""
        try:
            if provider_name.lower() == 'anthropic':
                import anthropic
                return True
            elif provider_name.lower() == 'openai':
                import openai
                return True
            elif provider_name.lower() == 'ollama':
                import ollama
                return True
            return False
        except ImportError:
            return False
