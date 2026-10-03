from typing import Dict, Optional
from services.ai_core.provider_base import BaseProvider
from services.ai_core.adapters.mock_provider import MockProvider
from services.ai_core.adapters.openai_provider import OpenAIProvider
from services.ai_core.adapters.anthropic_provider import AnthropicProvider
from services.ai_core.adapters.google_provider import GoogleProvider
from services.ai_core.adapters.local_provider import LocalProvider
from apps.api.config import settings

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._init_providers()

    def _init_providers(self):
        # Register standard providers
        self.register_provider(MockProvider())
        self.register_provider(OpenAIProvider(api_key=settings.OPENAI_API_KEY))
        self.register_provider(AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY))
        self.register_provider(GoogleProvider(api_key=settings.GOOGLE_AI_API_KEY))
        self.register_provider(LocalProvider())

    def register_provider(self, provider: BaseProvider):
        self._providers[provider.name.lower()] = provider

    def get_provider(self, name: Optional[str] = None) -> BaseProvider:
        provider_name = (name or settings.DEFAULT_AI_PROVIDER).lower()
        if provider_name in self._providers:
            return self._providers[provider_name]
        return self._providers["mock"]

    def list_providers(self) -> Dict[str, dict]:
        return {
            name: {
                "name": p.name,
                "capabilities": [c.value for c in p.supported_capabilities()],
                "configured": bool(getattr(p, "api_key", True))
            }
            for name, p in self._providers.items()
        }

provider_registry = ProviderRegistry()

def get_provider_registry() -> ProviderRegistry:
    return provider_registry
