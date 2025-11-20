"""
Provider factory with lazy loading and singleton pattern.
Eliminates duplicate provider initialization code across services.

Usage:
    from shared.llm_providers.factory import ProviderFactory

    # Get a provider instance (lazily loaded, cached)
    provider = ProviderFactory.get_provider('xai')

    # Use the provider
    response = provider.analyze_image(img_bytes, "Describe this image")
"""

from typing import Dict, Optional


class ProviderFactory:
    """Singleton factory for lazy-loading LLM providers."""

    _instances: Dict[str, any] = {}

    @classmethod
    def get_provider(cls, provider_name: str):
        """
        Get or create a provider instance with lazy loading.

        Args:
            provider_name: Name of the provider ('xai', 'anthropic', 'openai', etc.)

        Returns:
            Provider instance (cached after first creation)

        Raises:
            ValueError: If provider_name is not recognized
        """
        if provider_name not in cls._instances:
            # Lazy import providers to avoid unnecessary dependencies
            provider_classes = cls._get_provider_classes()

            if provider_name not in provider_classes:
                available = list(provider_classes.keys())
                raise ValueError(
                    f"Unknown provider: {provider_name}. "
                    f"Available providers: {', '.join(available)}"
                )

            # Instantiate and cache the provider
            cls._instances[provider_name] = provider_classes[provider_name]()

        return cls._instances[provider_name]

    @classmethod
    def _get_provider_classes(cls) -> Dict[str, type]:
        """
        Get mapping of provider names to classes.
        Imports are done here to keep them lazy.
        """
        from .xai_provider import XAIProvider
        from .anthropic_provider import AnthropicProvider
        from .openai_provider import OpenAIProvider

        # Core providers that are always available
        providers = {
            'xai': XAIProvider,
            'anthropic': AnthropicProvider,
            'openai': OpenAIProvider,
        }

        # Optional providers (gracefully handle if not installed)
        try:
            from .mistral_provider import MistralProvider
            providers['mistral'] = MistralProvider
        except ImportError:
            pass

        try:
            from .cohere_provider import CohereProvider
            providers['cohere'] = CohereProvider
        except ImportError:
            pass

        try:
            from .gemini_provider import GeminiProvider
            providers['gemini'] = GeminiProvider
        except ImportError:
            pass

        try:
            from .perplexity_provider import PerplexityProvider
            providers['perplexity'] = PerplexityProvider
        except ImportError:
            pass

        try:
            from .huggingface_provider import HuggingFaceProvider
            providers['huggingface'] = HuggingFaceProvider
        except ImportError:
            pass

        try:
            from .groq_provider import GroqProvider
            providers['groq'] = GroqProvider
        except ImportError:
            pass

        try:
            from .manus_provider import ManusProvider
            providers['manus'] = ManusProvider
        except ImportError:
            pass

        try:
            from .elevenlabs_provider import ElevenLabsProvider
            providers['elevenlabs'] = ElevenLabsProvider
        except ImportError:
            pass

        return providers

    @classmethod
    def clear_cache(cls, provider_name: Optional[str] = None):
        """
        Clear cached provider instances.

        Args:
            provider_name: Specific provider to clear, or None to clear all
        """
        if provider_name:
            cls._instances.pop(provider_name, None)
        else:
            cls._instances.clear()

    @classmethod
    def list_providers(cls) -> list:
        """List all available provider names."""
        return list(cls._get_provider_classes().keys())
