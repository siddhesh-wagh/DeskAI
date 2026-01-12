"""
Assistant Core - Main event loop and coordination
"""
import logging
from typing import Optional, Callable, Dict, Any
from core.context import AssistantContext
from core.speech import SpeechEngine, SpeechRecognizer
from core.dispatcher import CommandDispatcher
from datetime import datetime


class DeskAI:
    """
    Main assistant coordinator.
    Manages lifecycle, speech I/O, and command routing.
    """
    
    def __init__(
        self,
        context: AssistantContext,
        dispatcher: CommandDispatcher,
        on_response: Optional[Callable[[str, bool], None]] = None,
        on_command: Optional[Callable[[str], None]] = None,
        on_listening: Optional[Callable[[bool], None]] = None
    ):
        """
        Initialize assistant.
        
        Args:
            context: Shared state container
            dispatcher: Command routing system
            on_response: Callback for assistant responses (text, is_error)
            on_command: Callback when command received
            on_listening: Callback for listening state changes
        """
        self.context = context
        self.dispatcher = dispatcher
        self._logger = logging.getLogger(__name__)
        
        # Event callbacks (for UI integration)
        self._on_response = on_response or (lambda text, error: print(f"DeskAI: {text}"))
        self._on_command = on_command or (lambda cmd: print(f"User: {cmd}"))
        self._on_listening = on_listening or (lambda state: None)
        
        # Initialize speech engines
        self.tts = SpeechEngine(
            rate=context.voice_rate,
            voice_id=context.preferred_voice_id
        )
        self.stt = SpeechRecognizer()
        
        self._running = False
    
    def respond(self, message: str, speak: bool = True, is_error: bool = False):
        """
        Send response to user.
        
        Args:
            message: Response text
            speak: Whether to use TTS
            is_error: Whether this is an error message
        """
        # Always notify UI
        self._on_response(message, is_error)
        
        # Speak if enabled and requested
        if speak and self.context.voice_enabled:
            self.tts.speak(message)
    
    def greet(self) -> str:
        """Generate contextual greeting"""
        hour = datetime.now().hour
        
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        
        return f"{greeting}! I am DeskAI, your personal assistant. How may I help you?"
    
    def listen_once(self) -> Optional[str]:
        """
        Listen for a single command.
        
        Returns:
            Recognized command text or None
        """
        self.context.set_state(is_listening=True)
        self._on_listening(True)
        
        def on_listening_start():
            self.respond("Listening...", speak=False)
        
        def on_error(error_msg: str):
            self.respond(f"Listening error: {error_msg}", is_error=True)
        
        command = self.stt.listen(
            on_listening=on_listening_start,
            on_error=on_error
        )
        
        self.context.set_state(is_listening=False)
        self._on_listening(False)
        
        if command:
            self.context.set_state(last_command=command)
            self._on_command(command)
        
        return command
    
    def process_command(self, command: str) -> bool:
        """
        Route command to appropriate handler.
        
        Args:
            command: User's voice command
        
        Returns:
            True if should continue, False if exit requested
        """
        # Dispatch to handlers
        result = self.dispatcher.dispatch(command, self.context)
        
        if result is None:
            # No handler matched
            self.respond(
                "I didn't understand that. Say 'help' for available commands.",
                is_error=True
            )
            return True
        
        # Handle response
        if "response" in result:
            is_error = result.get("error", False)
            self.respond(result["response"], is_error=is_error)
        
        # Check for special actions
        action = result.get("action")
        if action == "exit":
            return False
        
        return True
    
    def run_once(self) -> bool:
        """
        Single iteration of assistant loop.
        
        Returns:
            True to continue, False to exit
        """
        command = self.listen_once()
        
        if not command:
            return True  # Continue despite empty command
        
        return self.process_command(command)
    
    def run(self):
        """
        Main assistant loop.
        Blocks until exit command or error.
        """
        self._running = True
        
        # Initial greeting
        greeting = self.greet()
        self.respond(greeting)
        
        # Main loop
        while self._running:
            try:
                should_continue = self.run_once()
                if not should_continue:
                    break
            
            except KeyboardInterrupt:
                self._logger.info("Interrupted by user")
                break
            
            except Exception as e:
                self._logger.error(f"Loop error: {e}", exc_info=True)
                self.respond(f"Internal error: {e}", is_error=True)
        
        self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        self._running = False
        self.respond("Goodbye!")
        self.tts.stop()
        self._logger.info("Assistant shutdown complete")