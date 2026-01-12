"""
Command Dispatcher - Intent routing with decorator-based registration
"""
from typing import Callable, List, Optional, Dict, Any
from dataclasses import dataclass
import re
from core.context import AssistantContext


@dataclass
class CommandHandler:
    """Metadata for a registered command"""
    patterns: List[str]  # Trigger patterns/keywords
    handler: Callable
    priority: int = 0  # Higher priority handlers checked first
    exact_match: bool = False  # Require exact match vs contains


class CommandDispatcher:
    """
    Decorator-based command routing system.
    
    Usage:
        dispatcher = CommandDispatcher()
        
        @dispatcher.command(["shutdown", "turn off"])
        def shutdown(ctx, query):
            return "Shutting down system"
    """
    
    def __init__(self):
        self._handlers: List[CommandHandler] = []
    
    def command(
        self, 
        patterns: List[str], 
        priority: int = 0, 
        exact_match: bool = False
    ):
        """
        Decorator to register a command handler.
        
        Args:
            patterns: List of trigger keywords/phrases
            priority: Higher priority = checked first (default: 0)
            exact_match: If True, query must exactly match pattern
        
        Returns:
            Decorated function
        """
        def decorator(func: Callable):
            handler = CommandHandler(
                patterns=[p.lower() for p in patterns],
                handler=func,
                priority=priority,
                exact_match=exact_match
            )
            self._handlers.append(handler)
            # Sort by priority (descending)
            self._handlers.sort(key=lambda h: h.priority, reverse=True)
            return func
        return decorator
    
    def dispatch(
        self, 
        query: str, 
        context: AssistantContext
    ) -> Optional[Dict[str, Any]]:
        """
        Route query to appropriate handler.
        
        Args:
            query: User's voice command (preprocessed)
            context: Current assistant context
        
        Returns:
            Dict with:
                - response: Text response to speak
                - action: Optional special action ("exit", etc.)
                - data: Optional structured data
        """
        if not query:
            return None
        
        query_lower = query.lower().strip()
        
        for handler in self._handlers:
            matched = False
            
            for pattern in handler.patterns:
                if handler.exact_match:
                    if query_lower == pattern:
                        matched = True
                        break
                else:
                    if pattern in query_lower:
                        matched = True
                        break
            
            if matched:
                try:
                    result = handler.handler(context, query)
                    
                    # Normalize response format
                    if isinstance(result, str):
                        return {"response": result}
                    elif isinstance(result, dict):
                        return result
                    else:
                        return {"response": str(result)}
                
                except Exception as e:
                    # Log error but don't crash dispatcher
                    return {
                        "response": f"Command failed: {str(e)}",
                        "error": True
                    }
        
        # No handler matched
        return None
    
    def list_commands(self) -> List[str]:
        """Get all registered command patterns for help display"""
        commands = []
        for handler in self._handlers:
            commands.extend(handler.patterns)
        return sorted(set(commands))
    
    def get_handler_count(self) -> int:
        """Get number of registered handlers"""
        return len(self._handlers)


# Global dispatcher instance for skill registration
_global_dispatcher = CommandDispatcher()


def get_dispatcher() -> CommandDispatcher:
    """Get the global dispatcher instance"""
    return _global_dispatcher


def get_dispatcher() -> CommandDispatcher:
    """Get the global dispatcher instance"""
    return _global_dispatcher


def command(*args, **kwargs):
    """
    Convenience decorator using global dispatcher.
    
    Usage:
        from core.dispatcher import command
        
        @command(["hello", "hi"])
        def greet(ctx, query):
            return f"Hello, {ctx.user_name}!"
    """
    return _global_dispatcher.command(*args, **kwargs)