"""
Qdrant vector database service for conversation memory.
Handles vector storage and retrieval of conversation history.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, 
    FieldCondition, MatchValue
)
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.config import settings

class QdrantService:
    """Service for Qdrant vector database operations"""
    
    def __init__(self):
        """Initialize Qdrant client and embeddings"""
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize Qdrant collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if settings.QDRANT_COLLECTION_NAME not in collection_names:
                self.client.create_collection(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=384,  # all-MiniLM-L6-v2 embedding size
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {settings.QDRANT_COLLECTION_NAME}")
        except Exception as e:
            print(f"Error initializing collection: {e}")
    
    async def store_conversation(
        self,
        user_id: int,
        conversation_id: str,
        messages: List[Dict[str, Any]]
    ):
        """
        Store conversation messages in vector database.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            messages: List of message dictionaries
        """
        try:
            # Prepare documents for vectorization
            documents = []
            metadatas = []
            
            for message in messages:
                if 'content' in message:
                    # Split long messages
                    chunks = self.text_splitter.split_text(message['content'])
                    
                    for chunk in chunks:
                        documents.append(chunk)
                        metadatas.append({
                            "user_id": str(user_id),
                            "conversation_id": conversation_id,
                            "role": message.get('role', 'user'),
                            "timestamp": datetime.now().isoformat(),
                            "type": "conversation"
                        })
            
            if documents:
                # Create vector store
                vector_store = Qdrant(
                    client=self.client,
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    embeddings=self.embeddings
                )
                
                # Add documents to vector store
                vector_store.add_texts(
                    texts=documents,
                    metadatas=metadatas
                )
                
        except Exception as e:
            print(f"Error storing conversation: {e}")
    
    async def retrieve_relevant_memories(
        self,
        user_id: int,
        query: str,
        conversation_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant conversation memories.
        
        Args:
            user_id: User identifier
            query: Search query
            conversation_id: Optional specific conversation
            limit: Maximum results to return
            
        Returns:
            List of relevant memory dictionaries
        """
        try:
            # Build filter
            filters = [FieldCondition(
                key="user_id",
                match=MatchValue(value=str(user_id))
            )]
            
            if conversation_id:
                filters.append(FieldCondition(
                    key="conversation_id",
                    match=MatchValue(value=conversation_id)
                ))
            
            filter_condition = Filter(must=filters) if filters else None
            
            # Create vector store for search
            vector_store = Qdrant(
                client=self.client,
                collection_name=settings.QDRANT_COLLECTION_NAME,
                embeddings=self.embeddings
            )
            
            # Search for relevant documents
            docs = vector_store.similarity_search(
                query=query,
                k=limit,
                filter=filter_condition
            )
            
            # Format results
            memories = []
            for doc in docs:
                memories.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": doc.metadata.get("score", 0)
                })
            
            return memories
            
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    async def get_conversation_history(
        self,
        user_id: int,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get full conversation history.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            limit: Maximum messages to return
            
        Returns:
            List of message dictionaries
        """
        try:
            # Search for conversation messages
            filter_condition = Filter(must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=str(user_id))
                ),
                FieldCondition(
                    key="conversation_id",
                    match=MatchValue(value=conversation_id)
                )
            ])
            
            # Scroll through collection
            scroll_result = self.client.scroll(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                scroll_filter=filter_condition,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            # Format messages
            messages = []
            for point in scroll_result[0]:
                messages.append({
                    "role": point.payload.get("role", "user"),
                    "content": point.payload.get("page_content", ""),
                    "timestamp": point.payload.get("timestamp", "")
                })
            
            # Sort by timestamp
            messages.sort(key=lambda x: x.get("timestamp", ""))
            
            return messages
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    async def delete_conversation(
        self,
        user_id: int,
        conversation_id: str
    ):
        """
        Delete a conversation from vector storage.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
        """
        try:
            self.client.delete(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                points_selector=Filter(must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=str(user_id))
                    ),
                    FieldCondition(
                        key="conversation_id",
                        match=MatchValue(value=conversation_id)
                    )
                ])
            )
        except Exception as e:
            print(f"Error deleting conversation: {e}")