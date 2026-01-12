"""
Web Operations Skill - Wikipedia, Google search, weather, jokes
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from typing import Dict, Any
import webbrowser
import wikipedia
import pyjokes
import requests


class WikipediaSkill(BaseSkill):
    """Search Wikipedia"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        # Extract search term
        search_term = params.get('term')
        
        if not search_term:
            # Extract from query: "wikipedia Albert Einstein" -> "Albert Einstein"
            term = query.lower().replace('wikipedia', '').strip()
            if not term:
                return self.error_response(
                    "Search term required. Example: 'wikipedia Albert Einstein'"
                )
            search_term = term
        
        try:
            # Search Wikipedia
            summary = wikipedia.summary(search_term, sentences=2)
            
            return SkillResult()\
                .with_message(f"According to Wikipedia: {summary}")\
                .with_data({
                    'term': search_term,
                    'summary': summary
                })\
                .build()
        
        except wikipedia.exceptions.DisambiguationError as e:
            # Multiple results
            options = ', '.join(e.options[:5])
            return self.error_response(
                f"Multiple results found for '{search_term}'. "
                f"Try: {options}"
            )
        
        except wikipedia.exceptions.PageError:
            return self.error_response(
                f"No Wikipedia page found for '{search_term}'"
            )
        
        except Exception as e:
            return self.error_response(f"Wikipedia search failed: {e}")


class GoogleSearchSkill(BaseSkill):
    """Open Google search in browser"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        search_term = params.get('term')
        
        if not search_term:
            # Extract from query
            term = query.lower()
            for keyword in ['search for', 'search', 'google']:
                term = term.replace(keyword, '')
            term = term.strip()
            
            if not term:
                return self.error_response(
                    "Search term required. Example: 'search for Python programming'"
                )
            search_term = term
        
        try:
            # Open Google search
            search_url = f"https://www.google.com/search?q={search_term}"
            webbrowser.open(search_url)
            
            return self.success_response(f"Searching Google for '{search_term}'")
        
        except Exception as e:
            return self.error_response(f"Failed to open search: {e}")


class WeatherSkill(BaseSkill):
    """Get weather information"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        city = params.get('city')
        
        if not city:
            # Extract from query: "weather in Mumbai" -> "Mumbai"
            import re
            match = re.search(r'weather in (.+)', query.lower())
            if match:
                city = match.group(1).strip()
            else:
                city = "auto"  # Auto-detect location
        
        try:
            # Use wttr.in service (no API key needed)
            url = f"https://wttr.in/{city}?format=%C+%t+%h+%w"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                weather_data = response.text.strip()
                return self.success_response(f"Current weather: {weather_data}")
            else:
                return self.error_response("Could not fetch weather information")
        
        except requests.RequestException as e:
            return self.error_response(
                f"Weather service unavailable: {e}. Check internet connection."
            )
        except Exception as e:
            return self.error_response(f"Weather fetch failed: {e}")


class JokeSkill(BaseSkill):
    """Tell a random joke"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            joke = pyjokes.get_joke()
            return self.success_response(joke)
        
        except Exception as e:
            return self.error_response(f"Failed to get joke: {e}")


class NewsSkill(BaseSkill):
    """Open news websites"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            # Open Google News
            webbrowser.open("https://news.google.com")
            return self.success_response("Opening Google News")
        
        except Exception as e:
            return self.error_response(f"Failed to open news: {e}")


class YouTubeSearchSkill(BaseSkill):
    """Search YouTube"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        search_term = params.get('term')
        
        if not search_term:
            # Extract from query
            term = query.lower()
            for keyword in ['youtube', 'search youtube for', 'play']:
                term = term.replace(keyword, '')
            term = term.strip()
            
            if not term:
                return self.error_response(
                    "Search term required. Example: 'search youtube for music'"
                )
            search_term = term
        
        try:
            # Open YouTube search
            search_url = f"https://www.youtube.com/results?search_query={search_term}"
            webbrowser.open(search_url)
            
            return self.success_response(f"Searching YouTube for '{search_term}'")
        
        except Exception as e:
            return self.error_response(f"Failed to open YouTube: {e}")


# Register commands
@command(["wikipedia", "wiki"], priority=10)
def cmd_wikipedia(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return WikipediaSkill().execute(ctx, query)


@command(["search for", "search", "google"], priority=5)
def cmd_google_search(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return GoogleSearchSkill().execute(ctx, query)


@command(["weather"], priority=10)
def cmd_weather(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return WeatherSkill().execute(ctx, query)


@command(["joke", "tell me a joke", "make me laugh"], priority=10)
def cmd_joke(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return JokeSkill().execute(ctx, query)


@command(["news", "latest news"], priority=10)
def cmd_news(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return NewsSkill().execute(ctx, query)


@command(["search youtube", "youtube search", "play on youtube"], priority=10)
def cmd_youtube_search(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return YouTubeSearchSkill().execute(ctx, query)