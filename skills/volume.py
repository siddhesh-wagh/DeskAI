"""
Volume Control Skill - Adjust system volume
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from typing import Dict, Any
import platform


class VolumeController(BaseSkill):
    """System volume control with platform support"""
    
    def __init__(self):
        super().__init__()
        self._platform = platform.system().lower()
        self._volume_interface = None
        
        if self._platform == "windows":
            self._init_windows_volume()
    
    def _init_windows_volume(self):
        """Initialize Windows volume control"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, 
                CLSCTX_ALL, 
                None
            )
            self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            self._logger.error(f"Windows volume init failed: {e}")
    
    def _get_current_volume(self) -> float:
        """Get current volume level (0.0 to 1.0)"""
        if self._platform == "windows" and self._volume_interface:
            return self._volume_interface.GetMasterVolumeLevelScalar()
        return 0.5  # Default
    
    def _set_volume(self, level: float):
        """Set volume level (0.0 to 1.0)"""
        level = max(0.0, min(1.0, level))  # Clamp to valid range
        
        if self._platform == "windows" and self._volume_interface:
            self._volume_interface.SetMasterVolumeLevelScalar(level, None)
        else:
            raise NotImplementedError(f"Volume control not supported on {self._platform}")
    
    def _mute(self):
        """Mute system volume"""
        if self._platform == "windows" and self._volume_interface:
            self._volume_interface.SetMute(1, None)
        else:
            raise NotImplementedError(f"Mute not supported on {self._platform}")
    
    def _unmute(self):
        """Unmute system volume"""
        if self._platform == "windows" and self._volume_interface:
            self._volume_interface.SetMute(0, None)
        else:
            raise NotImplementedError(f"Unmute not supported on {self._platform}")


class VolumeUpSkill(VolumeController):
    """Increase volume by 10%"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            current = self._get_current_volume()
            new_volume = min(current + 0.10, 1.0)
            self._set_volume(new_volume)
            
            percentage = int(new_volume * 100)
            return self.success_response(f"Volume increased to {percentage}%")
        
        except NotImplementedError as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response(f"Failed to increase volume: {e}")


class VolumeDownSkill(VolumeController):
    """Decrease volume by 10%"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            current = self._get_current_volume()
            new_volume = max(current - 0.10, 0.0)
            self._set_volume(new_volume)
            
            percentage = int(new_volume * 100)
            return self.success_response(f"Volume decreased to {percentage}%")
        
        except NotImplementedError as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response(f"Failed to decrease volume: {e}")


class SetVolumeSkill(VolumeController):
    """Set volume to specific level"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        level = params.get('level')
        
        if level is None:
            # Try to extract from query
            import re
            match = re.search(r'(\d+)', query)
            if match:
                level = int(match.group(1))
            else:
                return self.error_response(
                    "Volume level required. Example: 'set volume to 50'"
                )
        
        try:
            level = int(level)
            if not 0 <= level <= 100:
                return self.error_response("Volume must be between 0 and 100")
            
            self._set_volume(level / 100.0)
            return self.success_response(f"Volume set to {level}%")
        
        except NotImplementedError as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response(f"Failed to set volume: {e}")


class MuteSkill(VolumeController):
    """Mute system volume"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            self._mute()
            return self.success_response("Muted")
        
        except NotImplementedError as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response(f"Failed to mute: {e}")


class UnmuteSkill(VolumeController):
    """Unmute system volume"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            self._unmute()
            return self.success_response("Unmuted")
        
        except NotImplementedError as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response(f"Failed to unmute: {e}")


# Register commands
@command(["increase volume", "volume up", "louder"], priority=10)
def cmd_volume_up(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return VolumeUpSkill().execute(ctx, query)


@command(["decrease volume", "volume down", "quieter", "lower volume"], priority=10)
def cmd_volume_down(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return VolumeDownSkill().execute(ctx, query)


@command(["set volume", "volume"], priority=10)
def cmd_set_volume(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return SetVolumeSkill().execute(ctx, query)


@command(["mute"], priority=10)
def cmd_mute(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return MuteSkill().execute(ctx, query)


@command(["unmute"], priority=10)
def cmd_unmute(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return UnmuteSkill().execute(ctx, query)