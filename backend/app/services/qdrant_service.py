from typing import List, Dict, Any, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from langchain.embeddings import HuggingFaceEmbeddings
import json

from app.core.config import settings

class QdrantMemoryManager:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        self._ensure_collection()
    
    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if settings.QDRANT_COLLECTION not in collection_names:
                self.client.create_collection(
                    collection_name=settings.QDRANT_COLLECTION,
                    vectors_config=VectorParams(
                        size=384,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            print(f"Error ensuring collection: {e}")
            raise
    
    def store_conversation(
        self,
        user_id: str,
        conversation_id: str,
        messages: List[Dict[str, Any]]
    ):
        try:
            points = []
            
            for message in messages:
                if 'content' in message:
                    text = message['content']
                    vector = self.embeddings.embed_query(text)
                    
                    point = PointStruct(
                        id=hash(f"{user_id}{conversation_id}{text}{datetime.now().isoformat()}") % (2**63),
                        vector=vector,
                        payload={
                            "user_id": user_id,
                            "conversation_id": conversation_id,
                            "content": text,
                            "role": message.get('role', 'user'),
                            "timestamp": datetime.now().isoformat(),
                            "type": "conversation"
                        }
                    )
                    points.append(point)
            
            if points:
                self.client.upsert(
                    collection_name=settings.QDRANT_COLLECTION,
                    points=points
                )
                
        except Exception as e:
            print(f"Error storing conversation: {e}")
    
    def retrieve_relevant_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        try:
            query_vector = self.embeddings.embed_query(query)
            
            search_result = self.client.search(
                collection_name=settings.QDRANT_COLLECTION,
                query_vector=query_vector,
                query_filter=Filter(
                    must=[
                        {"key": "user_id", "match": {"value": user_id}}
                    ]
                ),
                limit=limit
            )
            
            memories = []
            for result in search_result:
                memories.append({
                    "content": result.payload.get("content", ""),
                    "role": result.payload.get("role", "user"),
                    "timestamp": result.payload.get("timestamp", ""),
                    "score": result.score
                })
            
            return memories
            
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    def get_conversation_history(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        try:
            scroll_result = self.client.scroll(
                collection_name=settings.QDRANT_COLLECTION,
                scroll_filter=Filter(
                    must=[
                        {"key": "user_id", "match": {"value": user_id}},
                        {"key": "conversation_id", "match": {"value": conversation_id}}
                    ]
                ),
                limit=limit,
                with_payload=True
            )
            
            messages = []
            for point in scroll_result[0]:
                messages.append({
                    "content": point.payload.get("content", ""),
                    "role": point.payload.get("role", "user"),
                    "timestamp": point.payload.get("timestamp", "")
                })
            
            return sorted(messages, key=lambda x: x['timestamp'])
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def delete_conversation(self, user_id: str, conversation_id: str):
        try:
            self.client.delete(
                collection_name=settings.QDRANT_COLLECTION,
                points_selector=Filter(
                    must=[
                        {"key": "user_id", "match": {"value": user_id}},
                        {"key": "conversation_id", "match": {"value": conversation_id}}
                    ]
                )
            )
        except Exception as e:
            print(f"Error deleting conversation: {e}")