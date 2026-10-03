import asyncio
from typing import List, Dict, Any, AsyncIterator, Optional, Set
from services.ai_core.provider_base import BaseProvider, ModelCapability, ChatMessagePayload, StreamChunk

class MockProvider(BaseProvider):
    def __init__(self):
        super().__init__("mock")

    def supported_capabilities(self) -> Set[ModelCapability]:
        return {
            ModelCapability.CHAT,
            ModelCapability.REASONING,
            ModelCapability.VISION,
            ModelCapability.EMBEDDINGS,
            ModelCapability.TOOL_CALLING,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.SPEECH_TO_TEXT,
            ModelCapability.TEXT_TO_SPEECH,
        }

    async def chat_stream(
        self,
        messages: List[ChatMessagePayload],
        model: Optional[str] = "mock-gpt-4o",
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncIterator[StreamChunk]:
        user_prompt = messages[-1].content if messages else "Hello"

        # 1. Yield thought chunk
        thought_msg = f"Decomposing user request: '{user_prompt[:40]}...' using mock reasoning chain."
        yield StreamChunk(thought=thought_msg)
        await asyncio.sleep(0.01)

        # 2. Yield token chunks
        response_text = (
            f"**NOVA X Intelligence Response** (Provider: Mock, Model: {model})\n\n"
            f"Processed query: *{user_prompt}*\n\n"
            "Execution verified through policy engine. Output generated deterministically."
        )

        words = response_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield StreamChunk(token=chunk)
            await asyncio.sleep(0.005)

        # 3. Final done chunk
        yield StreamChunk(done=True)

    async def generate_embeddings(self, texts: List[str], model: Optional[str] = "mock-embed") -> List[List[float]]:
        # Generates deterministic 128-dimensional normalized mock embedding vectors
        embeddings = []
        for text in texts:
            seed = sum(ord(c) for c in text) % 1000
            vector = [((seed + i) % 100) / 100.0 for i in range(128)]
            norm = (sum(x * x for x in vector) ** 0.5) or 1.0
            embeddings.append([x / norm for x in vector])
        return embeddings
