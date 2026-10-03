from typing import List, Dict, Any, AsyncIterator, Optional, Set
from services.ai_core.provider_base import BaseProvider, ModelCapability, ChatMessagePayload, StreamChunk

class GoogleProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("google")
        self.api_key = api_key

    def supported_capabilities(self) -> Set[ModelCapability]:
        return {
            ModelCapability.CHAT,
            ModelCapability.REASONING,
            ModelCapability.VISION,
            ModelCapability.EMBEDDINGS,
            ModelCapability.IMAGE,
            ModelCapability.TOOL_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
        }

    async def chat_stream(
        self,
        messages: List[ChatMessagePayload],
        model: Optional[str] = "gemini-2.0-flash",
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncIterator[StreamChunk]:
        yield StreamChunk(thought="Google Gemini 2.0 processing request with multimodal reasoning...")
        yield StreamChunk(token=f"Response from Google Gemini ({model}):\n\nPrompt processed successfully.")
        yield StreamChunk(done=True)

    async def generate_embeddings(self, texts: List[str], model: Optional[str] = "text-embedding-004") -> List[List[float]]:
        return [[0.0] * 768 for _ in texts]
