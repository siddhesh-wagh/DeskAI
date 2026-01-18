"""
Diagnostics Skill - System information and debugging
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command, get_dispatcher
from core.context import AssistantContext
from typing import Dict, Any
import sys
from pathlib import Path


class ListCommandsSkill(BaseSkill):
    """List all available voice commands"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        dispatcher = get_dispatcher()
        commands = dispatcher.list_commands()
        
        if not commands:
            return self.error_response("No commands registered")
        
        # Group by category (simple heuristic)
        categories = {
            'System': [],
            'Apps': [],
            'Files': [],
            'Web': [],
            'Media': [],
            'Calculator': [],
            'Other': []
        }
        
        for cmd in sorted(commands):
            if any(w in cmd for w in ['shutdown', 'restart', 'battery', 'system', 'time', 'date']):
                categories['System'].append(cmd)
            elif any(w in cmd for w in ['open', 'launch', 'start']):
                categories['Apps'].append(cmd)
            elif any(w in cmd for w in ['file', 'folder', 'search', 'create']):
                categories['Files'].append(cmd)
            elif any(w in cmd for w in ['wikipedia', 'search', 'google', 'weather', 'joke']):
                categories['Web'].append(cmd)
            elif any(w in cmd for w in ['screenshot', 'clipboard', 'volume', 'mute']):
                categories['Media'].append(cmd)
            elif any(w in cmd for w in ['calculate', 'what is']):
                categories['Calculator'].append(cmd)
            else:
                categories['Other'].append(cmd)
        
        response = f"Available Commands ({len(commands)} total):\n\n"
        
        for category, cmds in categories.items():
            if cmds:
                response += f"[{category}]\n"  # Changed from emoji
                for cmd in cmds[:10]:  # Limit to 10 per category
                    response += f"  - {cmd}\n"  # Changed from bullet
                if len(cmds) > 10:
                    response += f"  ... and {len(cmds) - 10} more\n"
                response += "\n"
        
        return SkillResult()\
            .with_message(response.strip())\
            .with_data({'commands': commands, 'count': len(commands)})\
            .build()


class SystemStatusSkill(BaseSkill):
    """Show DeskAI system status"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        dispatcher = get_dispatcher()
        
        # Get loaded skills from context if skill_loader info is available
        skills_dir = Path(__file__).parent
        skill_files = [
            f.stem for f in skills_dir.glob("*.py")
            if f.stem not in ("__init__", "base") and not f.stem.startswith("_")
        ]
        
        response = "[DeskAI System Status]\n\n"  # Changed from emoji
        response += f"Python: {sys.version.split()[0]}\n"
        response += f"Commands: {dispatcher.get_handler_count()}\n"
        response += f"Skills Found: {len(skill_files)}\n"
        response += f"Voice: {'Enabled' if context.voice_enabled else 'Disabled'}\n"
        response += f"Config: {context.config_dir}\n"
        response += f"\nSay 'list commands' to see all available commands"
        
        return SkillResult()\
            .with_message(response)\
            .with_data({
                'python_version': sys.version,
                'command_count': dispatcher.get_handler_count(),
                'skills': skill_files
            })\
            .build()


class DebugModeSkill(BaseSkill):
    """Enable verbose logging"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        import logging
        
        if 'enable' in query.lower() or 'on' in query.lower():
            logging.getLogger().setLevel(logging.DEBUG)
            return self.success_response("Debug mode enabled - verbose logging active")
        elif 'disable' in query.lower() or 'off' in query.lower():
            logging.getLogger().setLevel(logging.INFO)
            return self.success_response("Debug mode disabled")
        else:
            current_level = logging.getLogger().level
            level_name = logging.getLevelName(current_level)
            return self.success_response(f"Current log level: {level_name}")


# Register commands
@command(["list commands", "show commands", "available commands", "help"], priority=100)
def cmd_list_commands(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ListCommandsSkill().execute(ctx, query)


@command(["system status", "status", "diagnostics"], priority=50)
def cmd_system_status(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return SystemStatusSkill().execute(ctx, query)


@command(["debug mode", "enable debug", "disable debug"], priority=50)
def cmd_debug_mode(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return DebugModeSkill().execute(ctx, query)