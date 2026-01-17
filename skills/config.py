"""
Configuration Management Skill - View and modify settings
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from config.defaults import load_config_file, save_config_file, get_default_settings
from typing import Dict, Any
import json


class ViewSettingsSkill(BaseSkill):
    """Display current settings"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            settings = load_config_file(
                context.config_dir,
                "settings.json",
                get_default_settings
            )
            
            # Format settings for display
            response = "Current Settings:\n\n"
            response += f"👤 User: {settings.get('user', {}).get('name', 'User')}\n"
            response += f"🔊 Voice: {'Enabled' if settings.get('voice', {}).get('enabled', True) else 'Disabled'}\n"
            response += f"⚡ Speech Rate: {settings.get('voice', {}).get('rate', 175)}\n"
            response += f"🎨 Theme: {settings.get('ui', {}).get('theme', 'dark').title()}\n"
            response += f"🔔 Notifications: {'Enabled' if settings.get('notifications', {}).get('enabled', True) else 'Disabled'}\n"
            response += f"\n📁 Config location: {context.config_dir}"
            
            return SkillResult()\
                .with_message(response)\
                .with_data({"settings": settings})\
                .build()
        
        except Exception as e:
            return self.error_response(f"Failed to load settings: {e}")


class ViewAppsSkill(BaseSkill):
    """Display configured applications"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            from config.defaults import get_default_apps
            apps_config = load_config_file(
                context.config_dir,
                "apps.json",
                get_default_apps
            )
            
            # Get custom apps (filter out comments and examples)
            custom_apps = {}
            if "apps" in apps_config:
                custom_apps = {
                    k: v for k, v in apps_config["apps"].items()
                    if not k.startswith("_")
                }
            
            if not custom_apps:
                return self.success_response(
                    "No custom apps configured yet. "
                    f"Edit {context.config_dir / 'apps.json'} to add your applications."
                )
            
            response = f"Configured Applications ({len(custom_apps)}):\n\n"
            for name, path in sorted(custom_apps.items()):
                response += f"📱 {name}: {path}\n"
            
            response += f"\n💡 Tip: Say 'open [app name]' to launch"
            
            return SkillResult()\
                .with_message(response)\
                .with_data({"apps": custom_apps})\
                .build()
        
        except Exception as e:
            return self.error_response(f"Failed to load apps: {e}")


class SetPreferenceSkill(BaseSkill):
    """Change a setting value"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        setting_name = params.get('setting')
        value = params.get('value')
        
        if not setting_name or value is None:
            return self.error_response(
                "Usage: 'set [setting] to [value]'\n"
                "Examples:\n"
                "  - 'set voice rate to 200'\n"
                "  - 'set theme to light'\n"
                "  - 'set user name to John'"
            )
        
        try:
            settings = load_config_file(
                context.config_dir,
                "settings.json",
                get_default_settings
            )
            
            # Map setting names to config paths
            setting_map = {
                "voice rate": ("voice", "rate", int),
                "speech rate": ("voice", "rate", int),
                "user name": ("user", "name", str),
                "username": ("user", "name", str),
                "theme": ("ui", "theme", str),
                "language": ("user", "language", str),
            }
            
            setting_lower = setting_name.lower()
            if setting_lower not in setting_map:
                return self.error_response(
                    f"Unknown setting: {setting_name}\n"
                    f"Available: {', '.join(setting_map.keys())}"
                )
            
            # Update setting
            section, key, value_type = setting_map[setting_lower]
            
            if section not in settings:
                settings[section] = {}
            
            # Convert value to correct type
            try:
                converted_value = value_type(value)
            except ValueError:
                return self.error_response(
                    f"Invalid value for {setting_name}. Expected {value_type.__name__}."
                )
            
            settings[section][key] = converted_value
            
            # Save settings
            save_config_file(context.config_dir, "settings.json", settings)
            
            # Apply to context immediately if relevant
            if setting_lower in ["voice rate", "speech rate"]:
                context.voice_rate = converted_value
            elif setting_lower in ["user name", "username"]:
                context.user_name = converted_value
            
            return self.success_response(
                f"Setting updated: {setting_name} = {converted_value}\n"
                f"Restart DeskAI to apply all changes."
            )
        
        except Exception as e:
            return self.error_response(f"Failed to update setting: {e}")


class OpenConfigFolderSkill(BaseSkill):
    """Open configuration folder in file explorer"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            import os
            import platform
            
            config_path = str(context.config_dir)
            
            if platform.system() == "Windows":
                os.startfile(config_path)
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open '{config_path}'")
            else:  # Linux
                os.system(f"xdg-open '{config_path}'")
            
            return self.success_response(
                f"Opening config folder:\n{config_path}"
            )
        
        except Exception as e:
            return self.error_response(f"Failed to open folder: {e}")


class ReloadConfigSkill(BaseSkill):
    """Reload configuration from files"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            # Reload settings into context
            context._load_settings()
            
            return self.success_response(
                "Configuration reloaded successfully!\n"
                "Note: Some changes may require restart."
            )
        
        except Exception as e:
            return self.error_response(f"Failed to reload config: {e}")


# Register commands
@command(["show settings", "view settings", "my settings"], priority=10)
def cmd_view_settings(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ViewSettingsSkill().execute(ctx, query)


@command(["show apps", "list apps", "my apps", "configured apps"], priority=10)
def cmd_view_apps(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ViewAppsSkill().execute(ctx, query)


@command(["set preference", "set setting", "change setting"], priority=15)
def cmd_set_preference(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    # Try to parse "set X to Y"
    import re
    match = re.search(r'set (.+?) to (.+)', query, re.IGNORECASE)
    
    if match:
        setting = match.group(1).strip()
        value = match.group(2).strip()
        return SetPreferenceSkill().execute(ctx, query, setting=setting, value=value)
    
    return SetPreferenceSkill().execute(ctx, query)


@command(["open config", "open settings folder", "show config folder"], priority=10)
def cmd_open_config(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return OpenConfigFolderSkill().execute(ctx, query)


@command(["reload config", "refresh config", "reload settings"], priority=10)
def cmd_reload_config(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ReloadConfigSkill().execute(ctx, query)