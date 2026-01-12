"""
Context Management - Thread-safe shared state
"""
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, Optional
from pathlib import Path
import json


@dataclass
class AssistantContext:
    """
    Centralized state container for the assistant.
    Thread-safe with explicit locking for concurrent access.
    """
    
    # User preferences
    user_name: str = "User"
    voice_enabled: bool = True
    voice_rate: int = 175
    preferred_voice_id: Optional[str] = None
    
    # Paths (platform-agnostic)
    home_dir: Path = field(default_factory=lambda: Path.home())
    config_dir: Path = field(default_factory=lambda: Path.home() / ".deskai")
    notes_file: Path = field(default_factory=lambda: Path.home() / ".deskai" / "notes.json")
    
    # Runtime state
    is_listening: bool = False
    is_speaking: bool = False
    last_command: str = ""
    
    # Configuration cache
    _config: Dict[str, Any] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock, repr=False)
    
    def __post_init__(self):
        """Ensure config directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def set_state(self, **kwargs):
        """Thread-safe state update"""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with caching"""
        with self._lock:
            if key in self._config:
                return self._config[key]
            
            # Load from settings file if exists
            settings_file = self.config_dir / "settings.json"
            if settings_file.exists():
                try:
                    with open(settings_file) as f:
                        settings = json.load(f)
                        self._config.update(settings)
                        return self._config.get(key, default)
                except Exception:
                    pass
            
            return default
    
    def set_config(self, key: str, value: Any):
        """Persist configuration value"""
        with self._lock:
            self._config[key] = value
            settings_file = self.config_dir / "settings.json"
            
            try:
                existing = {}
                if settings_file.exists():
                    with open(settings_file) as f:
                        existing = json.load(f)
                
                existing[key] = value
                
                with open(settings_file, 'w') as f:
                    json.dump(existing, f, indent=2)
            except Exception as e:
                # Non-critical, just log
                pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Export context as dictionary"""
        with self._lock:
            return {
                'user_name': self.user_name,
                'voice_enabled': self.voice_enabled,
                'voice_rate': self.voice_rate,
                'is_listening': self.is_listening,
                'is_speaking': self.is_speaking,
                'last_command': self.last_command
            }