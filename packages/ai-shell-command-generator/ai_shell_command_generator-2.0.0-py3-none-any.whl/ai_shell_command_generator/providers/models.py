"""Model registry with focused selection of current models."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ModelInfo:
    """Information about an AI model."""
    name: str
    display_name: str
    context_window: int
    max_tokens: int
    cost_per_1m_input: float  # in USD
    cost_per_1m_output: float
    description: str
    recommended_for: List[str]
    released: str


class ModelRegistry:
    """Registry of available models per provider (October 2025) - Focused Selection."""
    
    # OpenAI GPT-5 Family ONLY
    OPENAI_MODELS = {
        "gpt-5": ModelInfo(
            name="gpt-5",
            display_name="GPT-5",
            context_window=2000000,  # Estimated
            max_tokens=32768,  # Estimated
            cost_per_1m_input=1.25,  # From image
            cost_per_1m_output=1.25,  # Estimated
            description="Flagship GPT-5 model with advanced capabilities",
            recommended_for=["complex", "teaching", "critical"],
            released="Oct 2025"
        ),
        "gpt-5-mini": ModelInfo(
            name="gpt-5-mini",
            display_name="GPT-5 Mini",
            context_window=1000000,  # Estimated
            max_tokens=16384,  # Estimated
            cost_per_1m_input=0.25,  # From image
            cost_per_1m_output=0.25,  # Estimated
            description="Cost-effective GPT-5 variant",
            recommended_for=["general", "teaching"],
            released="Oct 2025"
        ),
        "gpt-5-nano": ModelInfo(
            name="gpt-5-nano",
            display_name="GPT-5 Nano",
            context_window=500000,  # Estimated
            max_tokens=8192,  # Estimated
            cost_per_1m_input=0.05,  # From image
            cost_per_1m_output=0.05,  # Estimated
            description="Ultra cost-effective GPT-5 variant",
            recommended_for=["quick", "simple"],
            released="Oct 2025"
        ),
    }
    
    # Anthropic Claude - Only 3.5 Haiku and 4.1+ models
    ANTHROPIC_MODELS = {
        # Claude 4.x Series (4.1 and above)
        "claude-sonnet-4-5-20250929": ModelInfo(
            name="claude-sonnet-4-5-20250929",
            display_name="Claude Sonnet 4.5",
            context_window=200000,
            max_tokens=8096,
            cost_per_1m_input=3.00,
            cost_per_1m_output=15.00,
            description="Latest Claude model, balanced performance and cost",
            recommended_for=["general", "teaching", "complex"],
            released="Sep 2025"
        ),
        "claude-opus-4-1-20250805": ModelInfo(
            name="claude-opus-4-1-20250805",
            display_name="Claude Opus 4.1",
            context_window=200000,
            max_tokens=8096,
            cost_per_1m_input=15.00,
            cost_per_1m_output=75.00,
            description="Most powerful Claude model, best for complex reasoning",
            recommended_for=["complex", "teaching", "critical"],
            released="Aug 2025"
        ),
        
        # Claude 3.5 Haiku (as specifically requested)
        "claude-3-5-haiku-20241022": ModelInfo(
            name="claude-3-5-haiku-20241022",
            display_name="Claude Haiku 3.5",
            context_window=200000,
            max_tokens=8096,
            cost_per_1m_input=1.00,
            cost_per_1m_output=5.00,
            description="Fast and cost-effective Claude model",
            recommended_for=["quick", "simple", "cost-effective"],
            released="Oct 2024"
        ),
    }
    
    @classmethod
    def get_default_model(cls, provider: str) -> str:
        """Get default model for a provider (balanced performance/cost)."""
        defaults = {
            'anthropic': 'claude-sonnet-4-5-20250929',  # Latest Sonnet
            'openai': 'gpt-5-mini',  # Best balance in GPT-5 family
            'ollama': 'gpt-oss:latest',  # Ollama default
        }
        return defaults.get(provider, '')
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available providers."""
        return ['anthropic', 'openai', 'ollama']
    
    @classmethod
    def get_models_for_provider(cls, provider: str) -> Dict[str, ModelInfo]:
        """Get all models for a specific provider."""
        if provider == 'anthropic':
            return cls.ANTHROPIC_MODELS
        elif provider == 'openai':
            return cls.OPENAI_MODELS
        else:
            return {}
    
    @classmethod
    def get_model_info(cls, provider: str, model: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        models = cls.get_models_for_provider(provider)
        return models.get(model)
    
    @classmethod
    def get_recommended_models(cls, provider: str, use_case: str = "general") -> List[str]:
        """Get recommended models for a use case."""
        models = cls.get_models_for_provider(provider)
        recommended = []
        
        for model_name, info in models.items():
            if use_case in info.recommended_for:
                recommended.append(model_name)
        
        return recommended
    
    @classmethod
    def is_valid_model(cls, provider: str, model: str) -> bool:
        """Check if a model is valid for a provider."""
        # Ollama models are dynamic, so we don't validate them
        if provider.lower() == 'ollama':
            return True
        
        models = cls.get_models_for_provider(provider)
        return model in models
