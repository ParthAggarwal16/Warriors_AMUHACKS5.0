"""
Qdrant vector database service for conversation memory.
Handles vector storage, retrieval, and pruning of conversation history.
Only warns if collection or payload indexes are missing.
"""

from typing import List, Dict, Any
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue

# LangChain 1.x imports
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


class QdrantService:
    """Service for Qdrant vector database operations"""

    def __init__(self):
        """Initialize Qdrant client and embeddings"""
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=getattr(settings, "QDRANT_API_KEY", None),
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )

        self._initialize_collection()

    # ----------------------- Collection & Payload Check ----------------------- #
    def _initialize_collection(self):
        """Check if collection exists, warn if not, and check payload indexes"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if settings.QDRANT_COLLECTION_NAME not in collection_names:
                print(
                    f"⚠️ Collection '{settings.QDRANT_COLLECTION_NAME}' does not exist in Qdrant. "
                    "Please create it via Qdrant console or API."
                )
            else:
                self._check_payload_indexes()

        except Exception as e:
            print(f"Error checking collection: {e}")

    def _check_payload_indexes(self):
        """Check payload indexes and warn if missing"""
        try:
            required_fields = ["user_id", "conversation_id",]

            existing_indexes = self.client.get_payload_indexes(
                collection_name=settings.QDRANT_COLLECTION_NAME
            ).result
            existing_fields = [idx.name for idx in existing_indexes]

            missing_fields = [f for f in required_fields if f not in existing_fields]

            if missing_fields:
                print(
                    f"⚠️ Missing payload indexes in '{settings.QDRANT_COLLECTION_NAME}': "
                    f"{', '.join(missing_fields)}. "
                    "Filtered search on these fields will not work until added."
                )

        except Exception as e:
            print(f"Error checking payload indexes: {e}")

    # ----------------------- Store Conversation ----------------------- #
    async def store_conversation(
        self,
        user_id: int,
        conversation_id: str,
        messages: List[Dict[str, Any]],
    ):
        """Store conversation messages in vector database"""
        try:
            documents = []
            metadatas = []

            for message in messages:
                if "content" in message:
                    chunks = self.text_splitter.split_text(message["content"])
                    for chunk in chunks:
                        documents.append(chunk)
                        metadatas.append(
                            {
                                "user_id": str(user_id),
                                "conversation_id": conversation_id,
                                "role": message.get("role", "user"),
                                "timestamp": datetime.now().isoformat(),
                                "page_content": chunk,
                            }
                        )

            if documents:
                vector_store = Qdrant(
                    client=self.client,
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    embeddings=self.embeddings,
                )

                vector_store.add_texts(
                    texts=documents,
                    metadatas=metadatas,
                )
                print(f"Storing messages for user_id={user_id}, conversation_id={conversation_id}")
                for m in messages:
                    print(m["role"], ":", m["content"])

        except Exception as e:
            print(f"Error storing conversation: {e}")

    # ----------------------- Retrieve Messages ----------------------- #
    async def retrieve_recent_messages(
        self,
        user_id: int,
        conversation_id: str,
        limit: int = 5,
    ):
        """Retrieve the most recent N messages for context"""
        try:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=str(user_id)),
                    ),
                    FieldCondition(
                        key="conversation_id",
                        match=MatchValue(value=conversation_id),
                    ),
                ]
            )

            scroll_result = self.client.scroll(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                scroll_filter=filter_condition,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )

            messages = [
                {
                    "role": point.payload.get("role", "user"),
                    "content": point.payload.get("page_content", ""),
                    "timestamp": point.payload.get("timestamp", ""),
                    "point_id": point.id,
                }
                for point in scroll_result[0]
            ]

            messages.sort(key=lambda x: x.get("timestamp", ""))
            print(f"Retrieved {len(messages)} messages for user_id={user_id}, conversation_id={conversation_id}")
            for m in messages:
                print(m["role"], ":", m["content"])
            return messages

        except Exception as e:
            print(f"Error retrieving recent messages: {e}")
            return []

    # ----------------------- Prune Old Messages ----------------------- #
    async def prune_old_messages(
        self,
        user_id: int,
        conversation_id: str,
        keep_last: int = 5,
    ):
        """Delete older messages keeping only the last N"""
        messages = await self.retrieve_recent_messages(
            user_id=user_id, conversation_id=conversation_id, limit=1000
        )
        if len(messages) > keep_last:
            old_points = [m["point_id"] for m in messages[:-keep_last]]
            try:
                self.client.delete(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    points_selector={"ids": old_points},
                )
            except Exception as e:
                print(f"Error pruning old messages: {e}")

    # ----------------------- Chat With Memory ----------------------- #
    async def chat_with_memory(
        self,
        user_id: int,
        conversation_id: str,
        user_query: str,
        llm_chain,
        memory_limit: int = 5,
    ) -> str:
        """
        Handle a user query with memory context:
        - Retrieves last N messages
        - Combines with new query
        - Sends to LLM
        - Stores both user query and AI response
        - Prunes older messages
        """
        recent_messages = await self.retrieve_recent_messages(
            user_id=user_id, conversation_id=conversation_id, limit=memory_limit
        )

        context_text = "\n".join([m["content"] for m in recent_messages])
        prompt = f"{context_text}\nUser: {user_query}\nAI:"

        ai_response = llm_chain.run(prompt)

        await self.store_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            messages=[
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": ai_response},
            ],
        )

        await self.prune_old_messages(
            user_id=user_id, conversation_id=conversation_id, keep_last=memory_limit
        )

        return ai_response
