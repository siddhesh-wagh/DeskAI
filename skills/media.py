"""
Media Operations Skill - Screenshots, clipboard, window management
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from utils.os_utils import OSManager
from typing import Dict, Any
from PIL import ImageGrab
from datetime import datetime
import pyautogui


class ScreenshotSkill(BaseSkill):
    """Take a screenshot"""
    
    def __init__(self):
        super().__init__()
        self.os_manager = OSManager()
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            # Get screenshot save path
            screenshot_dir = self.os_manager.get_screenshot_path()
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = screenshot_dir / filename
            
            # Take screenshot
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            return SkillResult()\
                .with_message(f"Screenshot saved as {filename}")\
                .with_data({
                    'filepath': str(filepath),
                    'filename': filename
                })\
                .build()
        
        except Exception as e:
            return self.error_response(f"Screenshot failed: {e}")


class ClipboardReadSkill(BaseSkill):
    """Read clipboard content"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            import pyperclip
            content = pyperclip.paste()
            
            if not content:
                return self.success_response("Clipboard is empty")
            
            # Truncate long content for display
            display_content = content[:200]
            if len(content) > 200:
                display_content += "..."
            
            return SkillResult()\
                .with_message(f"Clipboard contains: {display_content}")\
                .with_data({
                    'content': content,
                    'length': len(content)
                })\
                .build()
        
        except ImportError:
            return self.error_response(
                "Clipboard module not available. Install pyperclip."
            )
        except Exception as e:
            return self.error_response(f"Failed to read clipboard: {e}")


class ClipboardCopySkill(BaseSkill):
    """Copy text to clipboard"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        text = params.get('text')
        
        if not text:
            return self.error_response("Text required to copy to clipboard")
        
        try:
            import pyperclip
            pyperclip.copy(text)
            
            return self.success_response("Copied to clipboard")
        
        except ImportError:
            return self.error_response(
                "Clipboard module not available. Install pyperclip."
            )
        except Exception as e:
            return self.error_response(f"Failed to copy to clipboard: {e}")


class WindowManagementSkill(BaseSkill):
    """Window management operations"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        action = params.get('action', '').lower()
        q = query.lower()
        
        try:
            if "alt tab" in q or "switch" in q:
                pyautogui.hotkey("alt", "tab")
                return self.success_response("Switched window")
            
            elif "minimize" in q:
                pyautogui.hotkey("win", "down")
                return self.success_response("Window minimized")
            
            elif "maximize" in q:
                pyautogui.hotkey("win", "up")
                return self.success_response("Window maximized")
            
            elif "close window" in q or "close app" in q:
                pyautogui.hotkey("alt", "f4")
                return self.success_response("Closing window")
            
            elif "split" in q and "left" in q:
                pyautogui.hotkey("win", "left")
                return self.success_response("Window split left")
            
            elif "split" in q and "right" in q:
                pyautogui.hotkey("win", "right")
                return self.success_response("Window split right")
            
            elif "lock" in q or "lock screen" in q:
                os_manager = OSManager()
                os_manager.lock_screen()
                return self.success_response("Screen locked")
            
            else:
                return self.error_response(
                    "Unknown window command. Try: minimize, maximize, close, split left/right, lock"
                )
        
        except Exception as e:
            return self.error_response(f"Window management failed: {e}")


class ThemeToggleSkill(BaseSkill):
    """Toggle dark/light mode (Windows only)"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        q = query.lower()
        
        try:
            if "dark mode" in q:
                # This is a placeholder - actual implementation varies by OS
                pyautogui.hotkey("ctrl", "shift", "d")
                return self.success_response("Dark mode toggled")
            
            elif "light mode" in q:
                pyautogui.hotkey("ctrl", "shift", "l")
                return self.success_response("Light mode toggled")
            
            else:
                return self.error_response("Specify 'dark mode' or 'light mode'")
        
        except Exception as e:
            return self.error_response(f"Theme toggle failed: {e}")


# Register commands
@command(["screenshot", "take screenshot", "screen capture"], priority=10)
def cmd_screenshot(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ScreenshotSkill().execute(ctx, query)


@command(["read clipboard", "clipboard content", "what's in clipboard"], priority=10)
def cmd_read_clipboard(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ClipboardReadSkill().execute(ctx, query)


@command(["alt tab", "switch window", "minimize", "maximize", "close window", "split"], priority=10)
def cmd_window_management(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return WindowManagementSkill().execute(ctx, query)


@command(["lock screen", "lock"], priority=10)
def cmd_lock_screen(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return WindowManagementSkill().execute(ctx, query, action="lock")


@command(["dark mode", "light mode"], priority=10)
def cmd_theme_toggle(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ThemeToggleSkill().execute(ctx, query)