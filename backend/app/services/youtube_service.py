"""
YouTube API service using LangChain tools.
Handles video search, recommendations, and transcript retrieval.
"""
from typing import List, Dict, Any, Optional
from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import isodate

from app.config import settings

class YouTubeService:
    """Service for YouTube video search and recommendations"""
    
    def __init__(self):
        """Initialize YouTube API client"""
        self.youtube = build(
            'youtube', 
            'v3', 
            developerKey=settings.YOUTUBE_API_KEY
        )
        
        # Initialize search tool
        self.search_tool = GoogleSearchAPIWrapper()
    
    async def search_videos(
        self, 
        query: str, 
        max_results: int = 10,
        duration: Optional[str] = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Search for educational YouTube videos.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            duration: Video duration (short, medium, long)
            
        Returns:
            List of video information dictionaries
        """
        try:
            # Build search request
            request = self.youtube.search().list(
                q=f"{query} tutorial education",
                part="snippet",
                type="video",
                maxResults=max_results,
                relevanceLanguage="en",
                videoDuration=duration,
                videoCategoryId="27",  # Education
                order="relevance"
            )
            
            # Execute request
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                video_details = await self.get_video_details(video_id)
                
                video_info = {
                    'id': video_id,
                    'title': item['snippet']['title'],
                    'channel': item['snippet']['channelTitle'],
                    'description': item['snippet']['description'][:200] + "..." 
                        if len(item['snippet']['description']) > 200 
                        else item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'duration': video_details.get('duration', 'N/A'),
                    'views': video_details.get('views', 'N/A')
                }
                videos.append(video_info)
            
            return videos
            
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return []
    
    async def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video details
        """
        try:
            request = self.youtube.videos().list(
                part="contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return {}
            
            item = response['items'][0]
            duration = isodate.parse_duration(
                item['contentDetails']['duration']
            )
            
            return {
                'duration': str(duration),
                'views': item['statistics'].get('viewCount', '0')
            }
            
        except Exception as e:
            print(f"Error getting video details: {e}")
            return {}
    
    async def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Get transcript/subtitles for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Transcript text or None if not available
        """
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = ' '.join([entry['text'] for entry in transcript_list])
            return transcript
        except Exception as e:
            print(f"Error getting transcript: {e}")
            return None
    
    async def get_educational_recommendations(
        self, 
        topic: str, 
        max_results: int = 5
    ) -> str:
        """
        Get formatted educational video recommendations.
        
        Args:
            topic: Learning topic
            max_results: Number of recommendations
            
        Returns:
            Formatted string with video recommendations
        """
        videos = await self.search_videos(topic, max_results)
        
        if not videos:
            return f"No educational videos found for '{topic}'. Try a different search term."
        
        result = f"📚 **Educational Videos for '{topic}'**\n\n"
        
        for i, video in enumerate(videos, 1):
            result += f"{i}. **{video['title']}**\n"
            result += f"   👤 Channel: {video['channel']}\n"
            result += f"   ⏱️ Duration: {video['duration']}\n"
            result += f"   👁️ Views: {video['views']}\n"
            result += f"   📝 {video['description']}\n"
            result += f"   🔗 {video['url']}\n\n"
        
        result += "\n💡 **Tips for Effective Learning:**\n"
        result += "- Take notes while watching\n"
        result += "- Pause and practice concepts\n"
        result += "- Watch at 1.25x speed for review\n"
        result += "- Discuss with study groups\n"
        
        return result
    
    def get_search_tool(self) -> Tool:
        """
        Get LangChain tool for web search.
        
        Returns:
            LangChain Tool object for searching
        """
        return Tool(
            name="Web Search",
            func=self.search_tool.run,
            description="Search the web for current information"
        )