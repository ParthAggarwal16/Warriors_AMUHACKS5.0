"""
Groq API service using LangChain 1.x.
Handles LLM interactions with Groq's models and Qdrant memory for conversation context.
"""

from typing import Optional, AsyncGenerator, List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import uuid

from app.config import settings
from app.services.qdrant_service import QdrantService  # Qdrant memory service


class GroqService:
    """Service for interacting with Groq API through LangChain with memory"""

    def __init__(self):
        """Initialize Groq LLM and Qdrant memory service"""
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )

        self.qdrant_service = QdrantService()  # Memory service

        self.system_prompt = """
You are an AI Tutor Assistant. Your goal is to help students learn effectively.

Capabilities:
1. Answer academic questions across all subjects
2. Explain concepts in simple, understandable terms
3. Create structured study plans with deadlines
4. Recommend educational resources
5. Provide motivation and encouragement
6. Help with problem-solving and critical thinking

Teaching Style:
- Be patient, supportive, and encouraging
- Break down complex topics into manageable parts
- Use analogies and examples when helpful
- Check for understanding periodically
- Adapt to the student's learning style

Always aim to build confidence and foster a love for learning.
"""

    # ------------------------------------------------------------------
    # Streaming Response with Memory
    # ------------------------------------------------------------------
    async def generate_streaming_response(
        self,
        user_id: int,
        conversation_id: str,
        message: str,
        memory_limit: int = 5,
    ) -> AsyncGenerator[str, None]:
        """
        Stream AI response including memory context:
        - Retrieves last N messages from Qdrant
        - Combines with user query
        - Streams response
        - Stores messages and prunes older messages
        """
        try:
            # Retrieve previous messages inside this service
            recent_messages = await self.qdrant_service.retrieve_recent_messages(
                user_id=user_id,
                conversation_id=conversation_id,
                limit=memory_limit
            )

            # Build context
            context_text = "\n".join(
                [f"{m['role'].capitalize()}: {m['content']}" for m in recent_messages]
            )

            # Prepare messages for LLM
            messages = [SystemMessage(content=self.system_prompt)]
            if context_text:
                messages.append(SystemMessage(content=f"Context:\n{context_text}"))
            messages.append(HumanMessage(content=message))

            # Stream response and accumulate content for storage
            ai_response_content = ""
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    ai_response_content += chunk.content
                    yield chunk.content

            # Store user query + AI response in Qdrant
            await self.qdrant_service.store_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                messages=[
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": ai_response_content},
                ]
            )

            # Prune old messages to keep only last N
            await self.qdrant_service.prune_old_messages(
                user_id=user_id,
                conversation_id=conversation_id,
                keep_last=memory_limit
            )

        except Exception as e:
            yield f"I encountered an error: {str(e)}. Please try again."

    # ------------------------------------------------------------------
    # Standard Response (non-stream, with memory)
    # ------------------------------------------------------------------
    async def generate_response(
        self,
        user_id: int,
        conversation_id: str,
        message: str,
        memory_limit: int = 5,
    ) -> str:
        """
        Generate a standard AI response using memory context.
        Retrieves previous messages automatically.
        """
        try:
            # Retrieve recent messages
            recent_messages = await self.qdrant_service.retrieve_recent_messages(
                user_id=user_id,
                conversation_id=conversation_id,
                limit=memory_limit
            )

            # Build context
            context_text = "\n".join(
                [f"{m['role'].capitalize()}: {m['content']}" for m in recent_messages]
            )

            messages = [SystemMessage(content=self.system_prompt)]
            if context_text:
                messages.append(SystemMessage(content=f"Context:\n{context_text}"))
            messages.append(HumanMessage(content=message))

            # Get AI response
            response = await self.llm.ainvoke(messages)

            # Store conversation
            await self.qdrant_service.store_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                messages=[
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response.content},
                ]
            )

            # Prune old messages
            await self.qdrant_service.prune_old_messages(
                user_id=user_id,
                conversation_id=conversation_id,
                keep_last=memory_limit
            )

            return response.content

        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."

    # ------------------------------------------------------------------
    # Study Plan Generator
    # ------------------------------------------------------------------
    async def create_study_plan(
        self,
        topic: str,
        days: int,
        hours_per_day: int = 2,
    ) -> str:
        prompt = f"""
Create a detailed study plan for learning {topic}.

Requirements:
- Duration: {days} days
- {hours_per_day} hours per day
- Include daily objectives
- Include recommended resources
- Include practice exercises
- Include assessment methods
- Make it realistic and achievable

Format clearly with structured sections.
"""
        return await self.generate_response(
            user_id=0,  # dummy user_id for study plan
            conversation_id=str(topic),  # dummy conversation
            message=prompt,
            memory_limit=0  # no memory needed
        )

    # ------------------------------------------------------------------
    # Text Summarizer
    # ------------------------------------------------------------------
    async def summarize_text(
        self,
        text: str,
        max_length: int = 300,
    ) -> str:
        prompt = f"""
Summarize the following text in {max_length} words or less:

{text}

Focus on key ideas and keep it concise.
"""
        return await self.generate_response(
            user_id=0,
            conversation_id=str(hash(text)),
            message=prompt,
            memory_limit=0
        )
