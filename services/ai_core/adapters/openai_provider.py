import json
import httpx
from typing import List, Dict, Any, AsyncIterator, Optional, Set
from services.ai_core.provider_base import BaseProvider, ModelCapability, ChatMessagePayload, StreamChunk

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        super().__init__("openai")
        self.api_key = api_key
        self.base_url = base_url

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
        model: Optional[str] = "gpt-4o",
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncIterator[StreamChunk]:
        if not self.api_key:
            # Yield error token if key not provided
            yield StreamChunk(token="[OpenAI API key not configured. Fallback to mock generation active.]\n\n")
            yield StreamChunk(done=True)
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or "gpt-4o",
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            yield StreamChunk(done=True)
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0]["delta"]
                            token = delta.get("content")
                            if token:
                                yield StreamChunk(token=token)
                        except Exception:
                            continue

    async def generate_embeddings(self, texts: List[str], model: Optional[str] = "text-embedding-3-small") -> List[List[float]]:
        if not self.api_key:
            return [[0.0] * 1536 for _ in texts]

        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json={"input": texts, "model": model or "text-embedding-3-small"}
            )
            data = res.json()
            return [item["embedding"] for item in data["data"]]
