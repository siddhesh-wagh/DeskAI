"""
OS Utilities - Platform-specific operations abstraction
"""
import platform
import subprocess
import logging
from typing import Dict, Optional
from pathlib import Path


class OSManager:
    """
    Cross-platform OS operations abstraction.
    Isolates platform-specific code from skills.
    """
    
    def __init__(self):
        self.platform = platform.system().lower()
        self._logger = logging.getLogger(__name__)
    
    def is_windows(self) -> bool:
        return self.platform == "windows"
    
    def is_linux(self) -> bool:
        return self.platform == "linux"
    
    def is_macos(self) -> bool:
        return self.platform == "darwin"
    
    def shutdown(self, delay: int = 1):
        """Shutdown system with optional delay"""
        if self.is_windows():
            subprocess.run(["shutdown", "/s", "/t", str(delay)], check=True)
        elif self.is_linux():
            subprocess.run(["shutdown", "-h", f"+{delay//60}"], check=True)
        elif self.is_macos():
            subprocess.run(["sudo", "shutdown", "-h", f"+{delay//60}"], check=True)
        else:
            raise OSError(f"Shutdown not supported on {self.platform}")
    
    def restart(self, delay: int = 1):
        """Restart system with optional delay"""
        if self.is_windows():
            subprocess.run(["shutdown", "/r", "/t", str(delay)], check=True)
        elif self.is_linux():
            subprocess.run(["shutdown", "-r", f"+{delay//60}"], check=True)
        elif self.is_macos():
            subprocess.run(["sudo", "shutdown", "-r", f"+{delay//60}"], check=True)
        else:
            raise OSError(f"Restart not supported on {self.platform}")
    
    def logout(self):
        """Log off current user"""
        if self.is_windows():
            subprocess.run(["shutdown", "/l"], check=True)
        elif self.is_linux():
            subprocess.run(["gnome-session-quit", "--logout", "--no-prompt"], check=True)
        elif self.is_macos():
            subprocess.run(["osascript", "-e", 'tell app "System Events" to log out'], check=True)
        else:
            raise OSError(f"Logout not supported on {self.platform}")
    
    def sleep(self):
        """Put system to sleep"""
        if self.is_windows():
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
        elif self.is_linux():
            subprocess.run(["systemctl", "suspend"], check=True)
        elif self.is_macos():
            subprocess.run(["pmset", "sleepnow"], check=True)
        else:
            raise OSError(f"Sleep not supported on {self.platform}")
    
    def lock_screen(self):
        """Lock the screen"""
        if self.is_windows():
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
        elif self.is_linux():
            # Try common lock commands
            for cmd in [["gnome-screensaver-command", "-l"], 
                       ["xdg-screensaver", "lock"],
                       ["loginctl", "lock-session"]]:
                try:
                    subprocess.run(cmd, check=True)
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            raise OSError("No screen lock command found")
        elif self.is_macos():
            subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"], check=True)
        else:
            raise OSError(f"Lock screen not supported on {self.platform}")
    
    def launch_app(self, app_path_or_cmd: str):
        """
        Launch application by path or command.
        
        Args:
            app_path_or_cmd: Path to executable or command name
        """
        if self.is_windows():
            # Handle special URIs (ms-settings:, microsoft.windows.camera:)
            if ":" in app_path_or_cmd and not app_path_or_cmd[1] == ":":
                subprocess.run(f"start {app_path_or_cmd}", shell=True, check=True)
            else:
                subprocess.Popen(app_path_or_cmd)
        
        elif self.is_linux():
            subprocess.Popen([app_path_or_cmd])
        
        elif self.is_macos():
            if app_path_or_cmd.endswith(".app"):
                subprocess.run(["open", "-a", app_path_or_cmd], check=True)
            else:
                subprocess.Popen([app_path_or_cmd])
        
        else:
            subprocess.Popen([app_path_or_cmd])
    
    def get_system_apps(self) -> Dict[str, str]:
        """
        Get platform-specific system applications.
        
        Returns:
            Dictionary mapping app names to commands/paths
        """
        if self.is_windows():
            return {
                "camera": "microsoft.windows.camera:",
                "calculator": "calc.exe",
                "files": "explorer.exe",
                "notepad": "notepad.exe",
                "paint": "mspaint.exe",
                "task manager": "taskmgr.exe",
                "control panel": "control.exe",
                "settings": "ms-settings:",
                "display settings": "ms-settings:display"
            }
        
        elif self.is_linux():
            return {
                "calculator": "gnome-calculator",
                "files": "nautilus",
                "text editor": "gedit",
                "terminal": "gnome-terminal",
                "settings": "gnome-control-center",
                "system monitor": "gnome-system-monitor"
            }
        
        elif self.is_macos():
            return {
                "calculator": "Calculator.app",
                "files": "Finder.app",
                "text edit": "TextEdit.app",
                "terminal": "Terminal.app",
                "system preferences": "System Preferences.app",
                "activity monitor": "Activity Monitor.app"
            }
        
        return {}
    
    def get_screenshot_path(self) -> Path:
        """Get platform-appropriate screenshot save location"""
        if self.is_windows():
            # Try OneDrive Screenshots first, fall back to Pictures
            onedrive_screenshots = Path.home() / "OneDrive" / "Pictures" / "Screenshots"
            if onedrive_screenshots.exists():
                return onedrive_screenshots
            
            pictures_screenshots = Path.home() / "Pictures" / "Screenshots"
            pictures_screenshots.mkdir(parents=True, exist_ok=True)
            return pictures_screenshots
        
        elif self.is_macos():
            # macOS default screenshot location
            return Path.home() / "Desktop"
        
        else:
            # Linux - typically Pictures
            pictures = Path.home() / "Pictures" / "Screenshots"
            pictures.mkdir(parents=True, exist_ok=True)
            return pictures