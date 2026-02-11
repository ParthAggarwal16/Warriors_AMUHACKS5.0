"""
Groq API service using LangChain.
Handles LLM interactions with Groq's models.
"""
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict, Any, Optional

from app.config import settings

class GroqService:
    """Service for interacting with Groq API through LangChain"""
    
    def __init__(self):
        """Initialize Groq LLM with configuration"""
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
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
    
    async def generate_response(
        self, 
        message: str, 
        context: Optional[str] = None
    ) -> str:
        """
        Generate a response using Groq LLM.
        
        Args:
            message: User's message
            context: Optional context or conversation history
            
        Returns:
            str: AI-generated response
        """
        try:
            # Prepare messages
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=message)
            ]
            
            # Add context if provided
            if context:
                messages.insert(1, SystemMessage(content=f"Context: {context}"))
            
            # Generate response
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text
            
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."
    
    async def generate_streaming_response(
        self, 
        message: str, 
        context: Optional[str] = None
    ):
        """
        Generate a streaming response using Groq LLM.
        
        Args:
            message: User's message
            context: Optional context
            
        Yields:
            str: Chunks of the AI-generated response
        """
        try:
            # Prepare messages
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=message)
            ]
            
            # Add context if provided
            if context:
                messages.insert(1, SystemMessage(content=f"Context: {context}"))
            
            # Stream response
            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                    
        except Exception as e:
            yield f"I encountered an error: {str(e)}. Please try again."
    
    async def create_study_plan(
        self, 
        topic: str, 
        days: int, 
        hours_per_day: int = 2
    ) -> str:
        """
        Create a structured study plan.
        
        Args:
            topic: Subject to study
            days: Number of days available
            hours_per_day: Hours per day for studying
            
        Returns:
            str: Detailed study plan
        """
        prompt = f"""
        Create a detailed study plan for learning {topic}.
        
        Requirements:
        - Duration: {days} days, {hours_per_day} hours per day
        - Include daily topics and objectives
        - Include recommended resources
        - Include practice exercises
        - Include assessment methods
        - Make it realistic and achievable
        
        Format the plan clearly with sections for each week/day.
        """
        
        return await self.generate_response(prompt)
    
    async def summarize_text(self, text: str, max_length: int = 300) -> str:
        """
        Summarize long text content.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            str: Concise summary
        """
        prompt = f"""
        Summarize the following text in {max_length} words or less:
        
        {text}
        
        Focus on the main ideas and key points.
        Keep the summary clear and concise.
        """
        
        return await self.generate_response(prompt)
    
    async def motivate_user(self, mood: str = "neutral") -> str:
        """
        Provide motivational messages based on user's mood.
        
        Args:
            mood: User's current mood
            
        Returns:
            str: Motivational message
        """
        prompt = f"""
        The student is feeling {mood}. 
        Provide an encouraging and motivational message.
        
        Include:
        1. Acknowledge their feelings
        2. Offer encouragement
        3. Share a relevant quote or insight
        4. Suggest a small, actionable step
        
        Be supportive and uplifting.
        """
        
        return await self.generate_response(prompt)