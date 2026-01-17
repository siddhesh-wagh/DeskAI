"""
Default Configuration - Template settings and apps
"""
from pathlib import Path
import json
import platform


def get_default_settings() -> dict:
    """Get default settings configuration"""
    return {
        "_comment": "DeskAI User Settings - Edit values below",
        
        "user": {
            "name": "User",
            "language": "en-US",
            "timezone": "auto"
        },
        
        "voice": {
            "enabled": True,
            "rate": 175,
            "volume": 1.0,
            "voice_id": None,
            "_comment_voice_id": "Set to specific voice ID or null for default"
        },
        
        "speech_recognition": {
            "timeout": 6,
            "phrase_time_limit": 12,
            "ambient_duration": 1.0,
            "language": "en-IN"
        },
        
        "ui": {
            "theme": "dark",
            "window_size": "700x650",
            "always_on_top": False,
            "start_minimized": False
        },
        
        "assistant": {
            "auto_start": False,
            "greeting_enabled": True,
            "confirmation_on_exit": True
        },
        
        "notifications": {
            "enabled": True,
            "sound": True,
            "timeout": 10
        },
        
        "paths": {
            "screenshot_dir": "auto",
            "notes_file": "auto",
            "_comment": "Use 'auto' for default paths or specify custom paths"
        },
        
        "advanced": {
            "log_level": "INFO",
            "debug_mode": False,
            "max_command_history": 100
        }
    }


def get_default_apps() -> dict:
    """Get default application mappings based on platform"""
    system = platform.system().lower()
    
    base_apps = {
        "_comment": "DeskAI Application Mappings",
        "_instructions": [
            "Add your custom applications here",
            "Format: 'app_name': 'command_or_path'",
            "Use lowercase for app names",
            "Examples below for each platform"
        ],
        
        "websites": {
            "_comment": "These work on all platforms",
            "youtube": "https://www.youtube.com",
            "google": "https://google.com",
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "linkedin": "https://linkedin.com",
            "twitter": "https://twitter.com",
            "reddit": "https://reddit.com",
            "stackoverflow": "https://stackoverflow.com",
            "weather": "https://weather.com",
            "maps": "https://maps.google.com"
        }
    }
    
    # Platform-specific apps
    if system == "windows":
        base_apps["apps"] = {
            "_comment": "Windows applications",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            
            "_comment_custom": "Add your custom Windows apps below:",
            "_example_chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "_example_vscode": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            "_example_spotify": "spotify.exe"
        }
    
    elif system == "linux":
        base_apps["apps"] = {
            "_comment": "Linux applications",
            "calculator": "gnome-calculator",
            "files": "nautilus",
            "text editor": "gedit",
            "terminal": "gnome-terminal",
            "settings": "gnome-control-center",
            
            "_comment_custom": "Add your custom Linux apps below:",
            "_example_firefox": "firefox",
            "_example_vscode": "code",
            "_example_spotify": "spotify"
        }
    
    elif system == "darwin":  # macOS
        base_apps["apps"] = {
            "_comment": "macOS applications",
            "calculator": "Calculator.app",
            "files": "Finder.app",
            "text edit": "TextEdit.app",
            "terminal": "Terminal.app",
            "safari": "Safari.app",
            
            "_comment_custom": "Add your custom macOS apps below:",
            "_example_chrome": "Google Chrome.app",
            "_example_vscode": "Visual Studio Code.app",
            "_example_spotify": "Spotify.app"
        }
    
    else:
        base_apps["apps"] = {
            "_comment": "Generic applications - add paths for your system"
        }
    
    return base_apps


def get_default_command_aliases() -> dict:
    """Get default command aliases/shortcuts"""
    return {
        "_comment": "Command Aliases - Create shortcuts for longer commands",
        "_instructions": [
            "Format: 'short_alias': 'full_command'",
            "Example: 'cpu': 'system info'"
        ],
        
        "aliases": {
            "hi": "hello",
            "hey": "hello",
            "bye": "exit",
            "quit": "exit",
            "calc": "calculate",
            "wiki": "wikipedia",
            "ss": "screenshot",
            "vol": "volume",
            "bat": "battery",
            "cpu": "system info"
        }
    }


def ensure_config_files(config_dir: Path):
    """
    Create default configuration files if they don't exist.
    
    Args:
        config_dir: Path to .deskai config directory
    """
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # settings.json
    settings_file = config_dir / "settings.json"
    if not settings_file.exists():
        with open(settings_file, 'w') as f:
            json.dump(get_default_settings(), f, indent=2)
        print(f"✓ Created default settings: {settings_file}")
    
    # apps.json
    apps_file = config_dir / "apps.json"
    if not apps_file.exists():
        with open(apps_file, 'w') as f:
            json.dump(get_default_apps(), f, indent=2)
        print(f"✓ Created default apps config: {apps_file}")
    
    # aliases.json
    aliases_file = config_dir / "aliases.json"
    if not aliases_file.exists():
        with open(aliases_file, 'w') as f:
            json.dump(get_default_command_aliases(), f, indent=2)
        print(f"✓ Created default aliases: {aliases_file}")
    
    # README.md for config directory
    readme_file = config_dir / "README.md"
    if not readme_file.exists():
        readme_content = """# DeskAI Configuration

This directory contains your personal DeskAI configuration files.

## Files

### settings.json
Main configuration file for DeskAI behavior, voice settings, UI preferences, etc.

### apps.json
Custom application mappings. Add your frequently used apps here.

Format:
```json
{
  "apps": {
    "app_name": "command_or_path"
  }
}
```

### aliases.json
Command shortcuts. Create short aliases for longer commands.

Example:
```json
{
  "aliases": {
    "cpu": "system info",
    "calc": "calculate"
  }
}
```

### notes.json
Your saved notes (auto-created when you save your first note).

## Editing

1. Edit files with any text editor
2. Restart DeskAI to apply changes
3. Keep valid JSON format (check with jsonlint.com)

## Backup

These files contain your personal settings. Back them up regularly!

## Reset

To reset to defaults, delete the file(s) and restart DeskAI.
"""
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        print(f"✓ Created config README: {readme_file}")


def load_config_file(config_dir: Path, filename: str, default_func) -> dict:
    """
    Load a configuration file with fallback to defaults.
    
    Args:
        config_dir: Config directory path
        filename: Config file name
        default_func: Function that returns default config
    
    Returns:
        Configuration dictionary
    """
    config_file = config_dir / filename
    
    if config_file.exists():
        try:
            with open(config_file) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠ Error parsing {filename}: {e}")
            print(f"  Using default configuration instead")
            return default_func()
        except Exception as e:
            print(f"⚠ Error loading {filename}: {e}")
            return default_func()
    else:
        return default_func()


def save_config_file(config_dir: Path, filename: str, config: dict):
    """
    Save configuration to file.
    
    Args:
        config_dir: Config directory path
        filename: Config file name
        config: Configuration dictionary to save
    """
    config_file = config_dir / filename
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"⚠ Error saving {filename}: {e}")