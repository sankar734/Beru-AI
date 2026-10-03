from typing import List, Dict, Any, AsyncIterator, Optional, Set
from services.ai_core.provider_base import BaseProvider, ModelCapability, ChatMessagePayload, StreamChunk

class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("anthropic")
        self.api_key = api_key

    def supported_capabilities(self) -> Set[ModelCapability]:
        return {
            ModelCapability.CHAT,
            ModelCapability.REASONING,
            ModelCapability.VISION,
            ModelCapability.TOOL_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
        }

    async def chat_stream(
        self,
        messages: List[ChatMessagePayload],
        model: Optional[str] = "claude-3-5-sonnet-20241022",
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncIterator[StreamChunk]:
        yield StreamChunk(thought="Anthropic Claude 3.5 Sonnet processing prompt...")
        yield StreamChunk(token=f"Response from Anthropic ({model}):\n\nUnderstood your instruction.")
        yield StreamChunk(done=True)

    async def generate_embeddings(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        # Anthropic does not provide embeddings directly, uses third-party or voyage
        return [[0.0] * 1024 for _ in texts]
