import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.services.tools import (
    get_youtube_recommendations,
    create_study_plan,
    summarize_content,
    motivate_user,
    search_internet
)

class GroqTutorAgent:
    def __init__(self, user_id: str, conversation_id: str):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.llm = self._initialize_llm()
        self.memory = self._initialize_memory()
        self.vector_store = self._initialize_vector_store()
        self.agent = self._initialize_agent()
    
    def _initialize_llm(self):
        return ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            streaming=True
        )
    
    def _initialize_memory(self):
        return ConversationBufferWindowMemory(
            k=settings.MEMORY_WINDOW_SIZE,
            return_messages=True,
            memory_key="chat_history",
            output_key="output"
        )
    
    def _initialize_vector_store(self):
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        client = QdrantClient(url=settings.QDRANT_URL)
        return Qdrant(
            client=client,
            collection_name=settings.QDRANT_COLLECTION,
            embeddings=embeddings
        )
    
    def _initialize_agent(self):
        tools = [
            Tool(
                name="YouTubeRecommendations",
                func=get_youtube_recommendations,
                description="Get YouTube video recommendations for educational topics"
            ),
            Tool(
                name="CreateStudyPlan",
                func=create_study_plan,
                description="Create a study plan with topics and deadlines"
            ),
            Tool(
                name="SummarizeContent",
                func=summarize_content,
                description="Summarize long texts or articles"
            ),
            Tool(
                name="MotivateUser",
                func=motivate_user,
                description="Provide motivational quotes and encouragement"
            ),
            Tool(
                name="SearchInternet",
                func=search_internet,
                description="Search the internet for current information"
            )
        ]
        
        system_prompt = """
        You are an AI Tutor Assistant. Your goal is to help students learn effectively.
        You can:
        1. Answer academic questions
        2. Recommend educational YouTube videos
        3. Create study plans with deadlines
        4. Summarize content
        5. Provide motivation and encouragement
        6. Help with research and explanations
        
        Always be supportive, patient, and encouraging.
        Use the available tools when needed.
        """
        
        prompt = PromptTemplate.from_template(system_prompt)
        
        return create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
    
    async def process_message(self, message: str) -> str:
        try:
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.agent.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True
            )
            
            response = await agent_executor.ainvoke({"input": message})
            
            self._store_in_memory(message, response["output"])
            
            return response["output"]
        except Exception as e:
            return f"Error processing message: {str(e)}"
    
    def _store_in_memory(self, query: str, response: str):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        texts = text_splitter.split_text(f"Q: {query}\nA: {response}")
        
        metadatas = [{
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "timestamp": datetime.now().isoformat(),
            "type": "conversation"
        } for _ in texts]
        
        self.vector_store.add_texts(texts, metadatas=metadatas)
    
    def search_memory(self, query: str, k: int = 5):
        return self.vector_store.similarity_search(query, k=k)
    
    async def get_conversation_summary(self):
        if hasattr(self.memory, 'predict_new_summary'):
            messages = self.memory.chat_memory.messages
            if len(messages) > 2:
                return self.memory.predict_new_summary(messages, "")
        return "No summary available"