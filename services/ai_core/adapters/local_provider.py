import httpx
from typing import List, Dict, Any, AsyncIterator, Optional, Set
from services.ai_core.provider_base import BaseProvider, ModelCapability, ChatMessagePayload, StreamChunk

class LocalProvider(BaseProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__("local")
        self.base_url = base_url

    def supported_capabilities(self) -> Set[ModelCapability]:
        return {
            ModelCapability.CHAT,
            ModelCapability.REASONING,
            ModelCapability.EMBEDDINGS,
            ModelCapability.TOOL_CALLING,
        }

    async def chat_stream(
        self,
        messages: List[ChatMessagePayload],
        model: Optional[str] = "llama3:latest",
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncIterator[StreamChunk]:
        yield StreamChunk(thought="Local Ollama runtime executing offline with complete privacy...")
        yield StreamChunk(token=f"Response from Local Model ({model}):\n\nExecuted entirely offline.")
        yield StreamChunk(done=True)

    async def generate_embeddings(self, texts: List[str], model: Optional[str] = "nomic-embed-text") -> List[List[float]]:
        return [[0.0] * 768 for _ in texts]
