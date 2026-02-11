"""
Groq API service using LangChain 1.x.
Handles LLM interactions with Groq's models.
"""

from typing import Optional, AsyncGenerator
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings


class GroqService:
    """Service for interacting with Groq API through LangChain"""

    def __init__(self):
        """Initialize Groq LLM with configuration"""
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,  # IMPORTANT: model (not model_name in v1.x)
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )

        # System prompt for AI Tutor
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
    # Standard Response
    # ------------------------------------------------------------------
    async def generate_response(
        self,
        message: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate a response using Groq LLM.

        Args:
            message: User's message
            context: Optional conversation context

        Returns:
            AI-generated response
        """
        try:
            messages = [
                SystemMessage(content=self.system_prompt)
            ]

            if context:
                messages.append(SystemMessage(content=f"Context: {context}"))

            messages.append(HumanMessage(content=message))

            response = await self.llm.ainvoke(messages)

            return response.content

        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."

    # ------------------------------------------------------------------
    # Streaming Response
    # ------------------------------------------------------------------
    async def generate_streaming_response(
        self,
        message: str,
        context: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response.

        Yields:
            Response chunks
        """
        try:
            messages = [
                SystemMessage(content=self.system_prompt)
            ]

            if context:
                messages.append(SystemMessage(content=f"Context: {context}"))

            messages.append(HumanMessage(content=message))

            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            yield f"I encountered an error: {str(e)}. Please try again."

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

        return await self.generate_response(prompt)

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

        return await self.generate_response(prompt)

    # ------------------------------------------------------------------
    # Motivation Generator
    # ------------------------------------------------------------------
    async def motivate_user(self, mood: str = "neutral") -> str:
        prompt = f"""
The student is feeling {mood}.
Provide a motivational message.

Include:
1. Acknowledge their feelings
2. Encouragement
3. A short inspiring quote
4. One small actionable step

Be supportive and uplifting.
"""

        return await self.generate_response(prompt)
