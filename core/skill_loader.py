"""
Skill Loader - Automatic skill discovery and loading
"""
import logging
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass


@dataclass
class SkillInfo:
    """Metadata about a loaded skill"""
    module_name: str
    file_path: Path
    command_count: int
    is_loaded: bool
    error: str = None


class SkillLoader:
    """
    Automatically discovers and loads skill modules.
    
    Features:
    - Auto-discovery of skills/*.py files
    - Error isolation (bad skills don't crash system)
    - Config-based enable/disable
    - Detailed logging
    """
    
    def __init__(self, skills_dir: Path = None, disabled_skills: Set[str] = None):
        """
        Initialize skill loader.
        
        Args:
            skills_dir: Path to skills directory (default: ./skills)
            disabled_skills: Set of skill names to skip (e.g., {'notes', 'reminders'})
        """
        self.skills_dir = skills_dir or Path(__file__).parent.parent / "skills"
        self.disabled_skills = disabled_skills or set()
        self._logger = logging.getLogger(__name__)
        self.loaded_skills: Dict[str, SkillInfo] = {}
    
    def discover_skills(self) -> List[Path]:
        """
        Find all skill modules in skills directory.
        
        Returns:
            List of skill module paths
        """
        if not self.skills_dir.exists():
            self._logger.warning(f"Skills directory not found: {self.skills_dir}")
            return []
        
        # Find all .py files except __init__.py and base.py
        skill_files = [
            f for f in self.skills_dir.glob("*.py")
            if f.stem not in ("__init__", "base") and not f.stem.startswith("_")
        ]
        
        self._logger.info(f"Discovered {len(skill_files)} potential skill modules")
        return skill_files
    
    def load_skill(self, skill_path: Path) -> SkillInfo:
        """
        Load a single skill module.
        
        Args:
            skill_path: Path to skill file
        
        Returns:
            SkillInfo with load status
        """
        skill_name = skill_path.stem
        module_name = f"skills.{skill_name}"
        
        # Check if disabled
        if skill_name in self.disabled_skills:
            self._logger.info(f"[SKIP] Skipping disabled skill: {skill_name}")
            return SkillInfo(
                module_name=module_name,
                file_path=skill_path,
                command_count=0,
                is_loaded=False,
                error="Disabled in config"
            )
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Count registered commands by checking for @command decorators
            command_count = self._count_commands(module)
            
            self._logger.info(f"[OK] Loaded skill: {skill_name} ({command_count} commands)")
            
            return SkillInfo(
                module_name=module_name,
                file_path=skill_path,
                command_count=command_count,
                is_loaded=True
            )
        
        except Exception as e:
            error_msg = f"Failed to load {skill_name}: {e}"
            self._logger.error(f"[FAIL] {error_msg}", exc_info=True)
            
            return SkillInfo(
                module_name=module_name,
                file_path=skill_path,
                command_count=0,
                is_loaded=False,
                error=str(e)
            )
    
    def _count_commands(self, module) -> int:
        """
        Count command registrations in module.
        
        Args:
            module: Imported module
        
        Returns:
            Number of commands registered
        """
        count = 0
        
        # Look for functions decorated with @command
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                # Functions starting with cmd_ are likely command handlers
                if name.startswith('cmd_'):
                    count += 1
        
        return count
    
    def load_all_skills(self) -> Dict[str, SkillInfo]:
        """
        Discover and load all skills.
        
        Returns:
            Dictionary of skill_name -> SkillInfo
        """
        skill_files = self.discover_skills()
        
        self._logger.info("="*50)
        self._logger.info("Loading Skills")
        self._logger.info("="*50)
        
        for skill_file in sorted(skill_files):
            skill_info = self.load_skill(skill_file)
            self.loaded_skills[skill_file.stem] = skill_info
        
        self._log_summary()
        
        return self.loaded_skills
    
    def _log_summary(self):
        """Log loading summary"""
        loaded = [s for s in self.loaded_skills.values() if s.is_loaded]
        failed = [s for s in self.loaded_skills.values() if not s.is_loaded and s.error != "Disabled in config"]
        disabled = [s for s in self.loaded_skills.values() if s.error == "Disabled in config"]
        
        total_commands = sum(s.command_count for s in loaded)
        
        self._logger.info("="*50)
        self._logger.info(f"[OK] Loaded: {len(loaded)} skills, {total_commands} commands")
        
        if disabled:
            self._logger.info(f"[SKIP] Disabled: {len(disabled)} skills")
        
        if failed:
            self._logger.warning(f"[FAIL] Failed: {len(failed)} skills")
            for skill in failed:
                self._logger.warning(f"  - {skill.module_name}: {skill.error}")
        
        self._logger.info("="*50)
    
    def get_loaded_skills(self) -> List[str]:
        """Get list of successfully loaded skill names"""
        return [
            name for name, info in self.loaded_skills.items()
            if info.is_loaded
        ]
    
    def get_failed_skills(self) -> List[str]:
        """Get list of skills that failed to load"""
        return [
            name for name, info in self.loaded_skills.items()
            if not info.is_loaded and info.error != "Disabled in config"
        ]
    
    def get_skill_info(self, skill_name: str) -> SkillInfo:
        """Get info about a specific skill"""
        return self.loaded_skills.get(skill_name)


def load_skills_from_config(config_dir: Path) -> SkillLoader:
    """
    Load skills with config-based disabling.
    
    Args:
        config_dir: Path to .deskai config directory
    
    Returns:
        SkillLoader instance
    """
    import json
    
    disabled_skills = set()
    
    # Load disabled skills from config
    settings_file = config_dir / "settings.json"
    if settings_file.exists():
        try:
            with open(settings_file) as f:
                settings = json.load(f)
                disabled_skills = set(settings.get("disabled_skills", []))
        except Exception:
            pass
    
    loader = SkillLoader(disabled_skills=disabled_skills)
    loader.load_all_skills()
    
    return loader