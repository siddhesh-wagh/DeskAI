"""
DeskAI - Professional Voice Assistant
======================================

Entry point and application initialization.
"""
import logging
import sys
import skills.config    # Configuration management
from pathlib import Path
from threading import Thread

# Ensure .deskai directory exists
deskai_dir = Path.home() / ".deskai"
deskai_dir.mkdir(parents=True, exist_ok=True)

# Configure logging before imports
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(deskai_dir / "deskai.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Core imports
from core.context import AssistantContext
from core.dispatcher import get_dispatcher
from core.assistant import DeskAI

# Import skills to register commands
# (Importing registers @command decorators)
import skills.system
import skills.calculator
import skills.apps
# Import other skills as you create them:
import skills.notes
import skills.files
import skills.web
# etc.


def create_assistant() -> DeskAI:
    """
    Factory function to create configured assistant instance.
    
    Returns:
        Initialized DeskAI instance
    """
    # Create context
    context = AssistantContext()
    
    # Get global dispatcher (already has registered commands from imports)
    dispatcher = get_dispatcher()
    
    logger.info(f"Loaded {dispatcher.get_handler_count()} command handlers")
    
    # Define UI callbacks (these will be overridden by GUI)
    def on_response(text: str, is_error: bool):
        prefix = "ERROR" if is_error else "DeskAI"
        print(f"[{prefix}] {text}")
    
    def on_command(command: str):
        print(f"[USER] {command}")
    
    def on_listening(is_listening: bool):
        status = "Listening..." if is_listening else "Ready"
        print(f"[STATUS] {status}")
    
    # Create assistant
    assistant = DeskAI(
        context=context,
        dispatcher=dispatcher,
        on_response=on_response,
        on_command=on_command,
        on_listening=on_listening
    )
    
    return assistant


def run_cli_mode():
    """Run assistant in CLI-only mode (no GUI)"""
    logger.info("Starting DeskAI in CLI mode")
    
    assistant = create_assistant()
    
    try:
        assistant.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        assistant.shutdown()


def run_gui_mode():
    """Run assistant with GUI"""
    logger.info("Starting DeskAI in GUI mode")
    
    try:
        from ui.gui import DeskAIWindow
    except ImportError as e:
        logger.error(f"GUI dependencies not available: {e}")
        logger.info("Falling back to CLI mode")
        run_cli_mode()
        return
    
    # Create assistant
    assistant = create_assistant()
    
    # Create and configure GUI
    window = DeskAIWindow(assistant)
    
    # Start assistant in background thread
    assistant_thread = Thread(target=assistant.run, daemon=True)
    assistant_thread.start()
    
    # Run GUI main loop (blocks until window closed)
    try:
        window.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"GUI error: {e}", exc_info=True)
    finally:
        assistant.shutdown()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DeskAI Voice Assistant")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode without GUI"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("="*50)
    logger.info("DeskAI Voice Assistant Starting")
    logger.info("="*50)
    
    if args.cli:
        run_cli_mode()
    else:
        run_gui_mode()


if __name__ == "__main__":
    main()