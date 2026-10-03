import asyncio
import logging
from typing import Dict, Any, List, Optional
from apps.api.config import settings

logger = logging.getLogger("nova.database")

class InMemoryCollection:
    """Async in-memory MongoDB-compatible collection for resilient zero-dependency development."""
    def __init__(self, name: str):
        self.name = name
        self._docs: Dict[str, Dict[str, Any]] = {}

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for doc in self._docs.values():
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return dict(doc)
        return None

    async def find(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        query = query or {}
        results = []
        for doc in self._docs.values():
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                results.append(dict(doc))
        return results

    async def count_documents(self, query: Dict[str, Any] = None) -> int:
        docs = await self.find(query)
        return len(docs)

    async def insert_one(self, doc: Dict[str, Any]):
        doc_id = str(doc.get("id") or doc.get("_id") or len(self._docs) + 1)
        doc_copy = dict(doc)
        doc_copy["_id"] = doc_id
        if "id" not in doc_copy:
            doc_copy["id"] = doc_id
        self._docs[doc_id] = doc_copy
        return type("InsertResult", (), {"inserted_id": doc_id})()

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]):
        existing = await self.find_one(query)
        if existing:
            doc_id = existing["_id"]
            if "$set" in update:
                self._docs[doc_id].update(update["$set"])
            else:
                self._docs[doc_id].update(update)
            return type("UpdateResult", (), {"modified_count": 1})()
        return type("UpdateResult", (), {"modified_count": 0})()

    async def delete_one(self, query: Dict[str, Any]):
        existing = await self.find_one(query)
        if existing:
            del self._docs[existing["_id"]]
            return type("DeleteResult", (), {"deleted_count": 1})()
        return type("DeleteResult", (), {"deleted_count": 0})()

class DatabaseManager:
    def __init__(self):
        self._is_in_memory = True
        self._collections: Dict[str, InMemoryCollection] = {}
        self._mongo_client = None
        self._mongo_db = None

    async def connect(self):
        if not settings.USE_IN_MEMORY_FALLBACK:
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                self._mongo_client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
                await self._mongo_client.server_info()
                self._mongo_db = self._mongo_client.get_default_database()
                self._is_in_memory = False
                logger.info("Connected to MongoDB at %s", settings.MONGODB_URL)
                return
            except Exception as e:
                logger.warning("MongoDB connection failed (%s), falling back to In-Memory DB", e)

        self._is_in_memory = True
        logger.info("Using Resilient In-Memory Database store")

    def get_collection(self, name: str):
        if not self._is_in_memory and self._mongo_db is not None:
            return self._mongo_db[name]
        if name not in self._collections:
            self._collections[name] = InMemoryCollection(name)
        return self._collections[name]

    @property
    def is_in_memory(self) -> bool:
        return self._is_in_memory

db_manager = DatabaseManager()

def get_db():
    return db_manager
