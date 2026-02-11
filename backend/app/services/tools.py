from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from googleapiclient.discovery import build
from langchain.tools import tool
from langchain.utilities import GoogleSearchAPIWrapper
import requests
from youtube_transcript_api import YouTubeTranscriptApi

from app.core.config import settings

@tool
def get_youtube_recommendations(topic: str, max_results: int = 5) -> str:
    """Get YouTube video recommendations for a given educational topic."""
    try:
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        
        request = youtube.search().list(
            q=f"{topic} tutorial education learn",
            part="snippet",
            type="video",
            maxResults=max_results,
            relevanceLanguage="en",
            videoDuration="medium",
            videoCategoryId="27"  # Education category
        )
        
        response = request.execute()
        
        recommendations = []
        for item in response.get('items', []):
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            description = item['snippet']['description'][:150] + "..." if len(item['snippet']['description']) > 150 else item['snippet']['description']
            
            video_info = {
                'title': title,
                'channel': channel,
                'description': description,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'video_id': video_id
            }
            recommendations.append(video_info)
        
        result = f"Top {len(recommendations)} YouTube recommendations for '{topic}':\n\n"
        for i, rec in enumerate(recommendations, 1):
            result += f"{i}. {rec['title']}\n"
            result += f"   Channel: {rec['channel']}\n"
            result += f"   Description: {rec['description']}\n"
            result += f"   URL: {rec['url']}\n\n"
        
        return result
    except Exception as e:
        return f"Error fetching YouTube recommendations: {str(e)}"

@tool
def create_study_plan(topic: str, days_available: int, hours_per_day: int = 2) -> str:
    """Create a structured study plan for a topic with deadlines."""
    try:
        days_available = max(1, min(days_available, 30))
        hours_per_day = max(1, min(hours_per_day, 8))
        
        total_hours = days_available * hours_per_day
        
        plan_structure = {
            "topic": topic,
            "total_days": days_available,
            "hours_per_day": hours_per_day,
            "total_hours": total_hours,
            "plan": []
        }
        
        phases = [
            ("Foundation", 0.3, "Learn basic concepts and terminology"),
            ("Core Concepts", 0.4, "Master main topics and principles"),
            ("Practice & Application", 0.2, "Apply knowledge through exercises"),
            ("Review & Assessment", 0.1, "Review and test understanding")
        ]
        
        current_day = 1
        for phase_name, percentage, description in phases:
            phase_hours = int(total_hours * percentage)
            phase_days = max(1, phase_hours // hours_per_day)
            
            phase_plan = {
                "phase": phase_name,
                "duration_days": phase_days,
                "days": f"Day {current_day} - Day {current_day + phase_days - 1}",
                "description": description,
                "activities": []
            }
            
            if phase_name == "Foundation":
                phase_plan["activities"] = [
                    "Watch introductory videos",
                    "Read basic concepts",
                    "Take notes on key terms"
                ]
            elif phase_name == "Core Concepts":
                phase_plan["activities"] = [
                    "Study detailed explanations",
                    "Work through examples",
                    "Solve practice problems"
                ]
            elif phase_name == "Practice & Application":
                phase_plan["activities"] = [
                    "Complete assignments",
                    "Work on projects",
                    "Join study groups"
                ]
            else:
                phase_plan["activities"] = [
                    "Review all material",
                    "Take practice tests",
                    "Identify weak areas"
                ]
            
            plan_structure["plan"].append(phase_plan)
            current_day += phase_days
        
        result = f"Study Plan for '{topic}':\n"
        result += f"Total Duration: {days_available} days ({hours_per_day} hours/day)\n\n"
        
        for phase in plan_structure["plan"]:
            result += f"{phase['phase']} ({phase['duration_days']} days):\n"
            result += f"Days: {phase['days']}\n"
            result += f"Focus: {phase['description']}\n"
            result += "Activities:\n"
            for activity in phase["activities"]:
                result += f"  • {activity}\n"
            result += "\n"
        
        result += "\nTips:\n"
        result += "1. Take regular breaks (Pomodoro technique)\n"
        result += "2. Review previous day's material\n"
        result += "3. Practice consistently\n"
        result += "4. Ask for help when needed\n"
        
        return result
    except Exception as e:
        return f"Error creating study plan: {str(e)}"

@tool
def summarize_content(text: str, max_length: int = 300) -> str:
    """Summarize long text content concisely."""
    try:
        if len(text) <= max_length:
            return text
        
        sentences = text.split('. ')
        if len(sentences) <= 3:
            return text
        
        summary = '. '.join(sentences[:3]) + '.'
        
        if len(summary) > max_length:
            words = summary.split(' ')
            while len(' '.join(words)) > max_length and len(words) > 1:
                words = words[:-1]
            summary = ' '.join(words) + '...'
        
        return f"Summary: {summary}"
    except Exception as e:
        return f"Error summarizing content: {str(e)}"

@tool
def motivate_user(mood: str = "neutral") -> str:
    """Provide motivational quotes and encouragement based on user's mood."""
    try:
        motivations = {
            "tired": [
                "The expert in anything was once a beginner. Keep going!",
                "Every master was once a disaster. Persistence is key!",
                "Small progress is still progress. Celebrate every step!"
            ],
            "stressed": [
                "You don't have to see the whole staircase, just take the first step.",
                "Pressure creates diamonds. You're being shaped into something brilliant!",
                "This challenge is temporary, but what you learn will last forever."
            ],
            "demotivated": [
                "The only way to do great work is to love what you do. Find the joy in learning!",
                "Success is the sum of small efforts repeated day in and day out.",
                "Your future self will thank you for not giving up today."
            ],
            "neutral": [
                "Learning is a treasure that will follow its owner everywhere.",
                "The beautiful thing about learning is that no one can take it away from you.",
                "Education is the most powerful weapon which you can use to change the world."
            ],
            "excited": [
                "Your enthusiasm is contagious! Keep that energy flowing!",
                "With your current mindset, you can achieve anything you set your mind to!",
                "This excitement is fuel for your learning journey. Use it well!"
            ]
        }
        
        import random
        quotes = motivations.get(mood.lower(), motivations["neutral"])
        quote = random.choice(quotes)
        
        encouragement = f"💪 Motivational Thought: {quote}\n\n"
        
        if mood in ["tired", "stressed"]:
            encouragement += "Remember to:\n• Take short breaks\n• Stay hydrated\n• Practice deep breathing\n• You've got this! 🌟"
        elif mood == "demotivated":
            encouragement += "Try these:\n• Set small, achievable goals\n• Reward yourself for progress\n• Remember why you started\n• Keep going! 🚀"
        else:
            encouragement += "Keep up the great work! Your dedication is inspiring! ✨"
        
        return encouragement
    except Exception as e:
        return f"Stay positive! Remember: 'This too shall pass.' Keep learning and growing! 🌱"

@tool
def search_internet(query: str) -> str:
    """Search the internet for current information on a topic."""
    try:
        search = GoogleSearchAPIWrapper()
        results = search.results(query, 3)
        
        if not results:
            return "No results found. Try a different search query."
        
        response = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            response += f"{i}. {result['title']}\n"
            response += f"   {result['snippet']}\n"
            response += f"   URL: {result['link']}\n\n"
        
        return response
    except Exception as e:
        return f"Error searching internet: {str(e)}"

def get_youtube_transcript(video_id: str) -> str:
    """Get transcript of a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([entry['text'] for entry in transcript])
        return text
    except:
        return ""