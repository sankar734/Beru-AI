from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, AsyncIterator, Optional, Set
from pydantic import BaseModel

class ModelCapability(str, Enum):
    CHAT = "CHAT"
    REASONING = "REASONING"
    VISION = "VISION"
    EMBEDDINGS = "EMBEDDINGS"
    IMAGE = "IMAGE"
    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"
    TEXT_TO_SPEECH = "TEXT_TO_SPEECH"
    TOOL_CALLING = "TOOL_CALLING"
    STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"

class ChatRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class ChatMessagePayload(BaseModel):
    role: ChatRole
    content: str
    thought: Optional[str] = None
    images: Optional[List[str]] = None

class StreamChunk(BaseModel):
    token: Optional[str] = None
    thought: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    done: bool = False

class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def supported_capabilities(self) -> Set[ModelCapability]:
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[ChatMessagePayload],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncIterator[StreamChunk]:
        pass

    @abstractmethod
    async def generate_embeddings(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        pass
