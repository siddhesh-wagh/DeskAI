"""
Application Launcher - Configuration-driven app and website opening
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from utils.os_utils import OSManager
from typing import Dict, Any, Optional
import webbrowser
import json
import shutil
from pathlib import Path


class AppLauncher(BaseSkill):
    """
    Launch applications and websites.
    Uses configuration file for app mappings instead of hardcoded paths.
    """
    
    def __init__(self):
        super().__init__()
        self.os_manager = OSManager()
        self._load_app_config()
    
    def _load_app_config(self):
        """Load application configurations from file"""
        # Default websites (platform-agnostic)
        self.websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://google.com",
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "linkedin": "https://linkedin.com",
            "twitter": "https://twitter.com",
            "facebook": "https://facebook.com",
            "instagram": "https://instagram.com",
            "reddit": "https://reddit.com",
            "stack overflow": "https://stackoverflow.com",
            "weather": "https://weather.com"
        }
        
        # Platform-specific system apps
        self.system_apps = self.os_manager.get_system_apps()
        
        # User-configured apps from config file
        self.user_apps = self._load_user_apps()
    
    def _load_user_apps(self) -> Dict[str, str]:
        """Load user-configured applications from JSON"""
        config_path = Path.home() / ".deskai" / "apps.json"
        
        if not config_path.exists():
            # Create default config
            default_config = {
                "_comment": "Add your custom applications here",
                "_example": {
                    "app_name": "path/to/executable or command"
                }
            }
            
            try:
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
            except Exception as e:
                self._logger.warning(f"Could not create apps.json: {e}")
            
            return {}
        
        try:
            with open(config_path) as f:
                config = json.load(f)
                # Filter out comment keys
                return {
                    k: v for k, v in config.items() 
                    if not k.startswith("_")
                }
        except Exception as e:
            self._logger.error(f"Error loading apps.json: {e}")
            return {}
    
    def find_app_command(self, app_name: str) -> Optional[str]:
        """
        Find application command using multiple strategies.
        
        Returns command/path if found, None otherwise.
        """
        # 1. Check user-configured apps
        if app_name in self.user_apps:
            return self.user_apps[app_name]
        
        # 2. Check system apps
        if app_name in self.system_apps:
            return self.system_apps[app_name]
        
        # 3. Try to find in PATH
        command = shutil.which(app_name)
        if command:
            return command
        
        # 4. Try common variations
        variations = [
            app_name,
            app_name.replace(" ", ""),
            app_name.replace(" ", "-"),
            app_name.replace(" ", "_")
        ]
        
        for variation in variations:
            command = shutil.which(variation)
            if command:
                return command
        
        return None
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        q = query.lower()
        
        # Check for websites first
        for site_name, url in self.websites.items():
            if site_name in q:
                try:
                    webbrowser.open(url)
                    return self.success_response(f"Opening {site_name}")
                except Exception as e:
                    return self.error_response(f"Failed to open {site_name}: {e}")
        
        # Check for applications
        for app_name in list(self.user_apps.keys()) + list(self.system_apps.keys()):
            if app_name.lower() in q:
                command = self.find_app_command(app_name)
                if command:
                    try:
                        self.os_manager.launch_app(command)
                        return self.success_response(f"Opening {app_name}")
                    except Exception as e:
                        return self.error_response(f"Failed to open {app_name}: {e}")
        
        # Try to extract app name from query
        # Patterns: "open X", "launch X", "start X"
        import re
        patterns = [
            r'open\s+(.+)',
            r'launch\s+(.+)',
            r'start\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, q)
            if match:
                app_name = match.group(1).strip()
                command = self.find_app_command(app_name)
                
                if command:
                    try:
                        self.os_manager.launch_app(command)
                        return self.success_response(f"Opening {app_name}")
                    except Exception as e:
                        return self.error_response(f"Failed to open {app_name}: {e}")
                else:
                    return self.error_response(
                        f"Application '{app_name}' not found. "
                        f"Add it to ~/.deskai/apps.json"
                    )
        
        return self.error_response("Could not identify application to open")


# Register open/launch commands
@command(["open", "launch", "start"], priority=20)
def cmd_launch_app(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return AppLauncher().execute(ctx, query)