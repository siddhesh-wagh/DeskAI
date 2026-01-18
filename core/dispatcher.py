"""
Command Dispatcher - Intent routing with decorator-based registration
"""
from typing import Callable, List, Optional, Dict, Any
from dataclasses import dataclass
import logging

from core.context import AssistantContext


@dataclass
class CommandHandler:
    """Metadata for a registered command"""
    patterns: List[str]          # Trigger patterns/keywords
    handler: Callable
    priority: int = 0            # Higher priority handlers checked first
    exact_match: bool = False    # Require exact match vs contains


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
        self._logger = logging.getLogger(__name__)

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
            priority: Higher priority = checked first
            exact_match: If True, query must exactly match pattern
        """
        def decorator(func: Callable):
            handler = CommandHandler(
                patterns=[p.lower() for p in patterns],
                handler=func,
                priority=priority,
                exact_match=exact_match
            )
            self._handlers.append(handler)
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
        """
        if not query:
            return None

        query_lower = query.lower().strip()
        self._logger.debug(f"Dispatching query: '{query_lower}'")

        for handler in self._handlers:
            matched_pattern = None

            for pattern in handler.patterns:
                if handler.exact_match:
                    if query_lower == pattern:
                        matched_pattern = pattern
                        break
                else:
                    if pattern in query_lower:
                        matched_pattern = pattern
                        break

            if not matched_pattern:
                continue

            self._logger.debug(
                f"Matched pattern '{matched_pattern}' "
                f"(priority {handler.priority})"
            )

            try:
                result = handler.handler(context, query)

                # Allow handler to opt out
                if result is None:
                    self._logger.debug(
                        f"Handler {handler.handler.__name__} returned None, continuing"
                    )
                    continue

                self._logger.info(
                    f"Command executed: '{matched_pattern}' "
                    f"-> {handler.handler.__name__}"
                )

                if isinstance(result, dict):
                    return result
                return {"response": str(result)}

            except Exception as e:
                self._logger.exception(
                    f"Handler {handler.handler.__name__} failed"
                )
                return {
                    "response": f"Command failed: {e}",
                    "error": True
                }

        self._logger.warning(f"No handler matched query: '{query_lower}'")
        return None

    def list_commands(self) -> List[str]:
        """Get all registered command patterns"""
        patterns = []
        for handler in self._handlers:
            patterns.extend(handler.patterns)
        return sorted(set(patterns))

    def get_handler_count(self) -> int:
        """Get number of registered handlers"""
        return len(self._handlers)


# Global dispatcher instance
_global_dispatcher = CommandDispatcher()


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
