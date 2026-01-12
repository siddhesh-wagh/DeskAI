"""
DeskAI GUI - CustomTkinter Interface
"""
import customtkinter as ctk
from threading import Thread
import logging
from typing import Optional
from core.assistant import DeskAI


class DeskAIWindow:
    """
    Main GUI window for DeskAI.
    Integrates with DeskAI assistant via callbacks.
    """
    
    def __init__(self, assistant: DeskAI):
        """
        Initialize GUI window.
        
        Args:
            assistant: DeskAI instance to control
        """
        self.assistant = assistant
        self._logger = logging.getLogger(__name__)
        
        # Animation state
        self._listening_active = False
        self._animation_phrases = [
            "Zzz... 😴", 
            "Taking a nap... 💤", 
            "Dreaming of commands... ✨",
            "Waiting for your voice ✨...", 
            "🥱", 
            "Ready when you are... 🎤"
        ]
        self._current_phrase_index = 0
        self._current_dot_count = 1
        
        # Create window
        self._create_window()
        
        # Wire up callbacks to assistant
        self._wire_callbacks()
    
    def _create_window(self):
        """Create and configure the main window"""
        self.app = ctk.CTk()
        self.app.title("DeskAI - Enhanced Voice Assistant")
        self.app.geometry("700x650")
        self.app.resizable(False, False)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create UI elements
        self._create_header()
        self._create_display_area()
        self._create_buttons()
        self._create_footer()
    
    def _create_header(self):
        """Create header section"""
        header_frame = ctk.CTkFrame(
            self.app, 
            fg_color="#2E86AB", 
            corner_radius=10
        )
        header_frame.pack(pady=15, padx=20, fill="x")
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🤖 DeskAI", 
            text_color="white", 
            font=("Segoe UI", 32, "bold")
        )
        title_label.pack(pady=(10, 5))
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="Enhanced Voice Assistant", 
            text_color="white", 
            font=("Segoe UI", 14)
        )
        subtitle_label.pack(pady=(0, 10))
    
    def _create_display_area(self):
        """Create command and response display boxes"""
        display_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        display_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # "You said" section
        you_said_label = ctk.CTkLabel(
            display_frame, 
            text="You said:", 
            anchor="w", 
            font=("Segoe UI", 14, "bold")
        )
        you_said_label.pack(anchor="w", pady=(0, 3))
        
        self.command_box = ctk.CTkTextbox(
            display_frame, 
            height=50, 
            font=("Segoe UI", 13), 
            wrap="word"
        )
        self.command_box.configure(state="disabled")
        self.command_box.pack(fill="x", pady=(0, 10))
        
        # "DeskAI says" section
        assistant_says_label = ctk.CTkLabel(
            display_frame, 
            text="DeskAI says:", 
            anchor="w", 
            font=("Segoe UI", 14, "bold")
        )
        assistant_says_label.pack(anchor="w", pady=(0, 3))
        
        self.response_box = ctk.CTkTextbox(
            display_frame, 
            font=("Segoe UI", 12), 
            wrap="word"
        )
        self.response_box.configure(state="disabled")
        self.response_box.pack(fill="both", expand=True)
    
    def _create_buttons(self):
        """Create control buttons"""
        button_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Voice toggle button
        self.toggle_btn = ctk.CTkButton(
            button_frame, 
            text="🔊 Voice ON", 
            command=self._toggle_voice,
            font=("Segoe UI", 16), 
            height=45, 
            width=150, 
            corner_radius=20,
            fg_color="#27ae60", 
            hover_color="#2ecc71"
        )
        self.toggle_btn.pack(side="left", padx=8)
        
        # Tap to speak button
        self.listen_btn = ctk.CTkButton(
            button_frame, 
            text="🎤 Tap to Speak",
            command=self._on_tap_to_speak,
            font=("Segoe UI", 16), 
            height=45, 
            width=200, 
            corner_radius=20,
            fg_color="#8e44ad", 
            hover_color="#9b59b6"
        )
        self.listen_btn.pack(side="left", padx=8)
        
        # Help button
        self.help_btn = ctk.CTkButton(
            button_frame, 
            text="❓ Help",
            command=self._show_help,
            font=("Segoe UI", 16), 
            height=45, 
            width=120, 
            corner_radius=20,
            fg_color="#3498db", 
            hover_color="#2980b9"
        )
        self.help_btn.pack(side="left", padx=8)
    
    def _create_footer(self):
        """Create footer label"""
        footer_label = ctk.CTkLabel(
            self.app, 
            text="Say 'Help' for available commands", 
            font=("Segoe UI", 11), 
            text_color="#95a5a6"
        )
        footer_label.pack(pady=(5, 10), side="bottom")
    
    def _wire_callbacks(self):
        """Wire GUI callbacks to assistant"""
        # Override assistant callbacks to update GUI
        original_on_response = self.assistant._on_response
        original_on_command = self.assistant._on_command
        original_on_listening = self.assistant._on_listening
        
        def on_response(text: str, is_error: bool):
            self._update_response_box(text, is_error)
            # Still call original for logging
            original_on_response(text, is_error)
        
        def on_command(command: str):
            self._update_command_box(f"You said: {command}")
            original_on_command(command)
        
        def on_listening(is_listening: bool):
            self._listening_active = is_listening
            if is_listening:
                self._update_command_box("Listening your voice ✨...")
            original_on_listening(is_listening)
        
        # Replace callbacks
        self.assistant._on_response = on_response
        self.assistant._on_command = on_command
        self.assistant._on_listening = on_listening
    
    # === GUI UPDATE METHODS (Thread-safe) ===
    
    def _update_command_box(self, text: str):
        """Update command box (thread-safe)"""
        def _update():
            self.command_box.configure(state="normal")
            self.command_box.delete("0.0", "end")
            self.command_box.insert("0.0", text)
            self.command_box.configure(state="disabled")
        
        self.app.after(0, _update)
    
    def _update_response_box(self, text: str, is_error: bool = False):
        """Update response box (thread-safe)"""
        def _update():
            self.response_box.configure(state="normal")
            prefix = "❌ ERROR" if is_error else "DeskAI"
            self.response_box.insert("end", f"{prefix}: {text}\n")
            self.response_box.see("end")
            self.response_box.configure(state="disabled")
        
        self.app.after(0, _update)
    
    # === BUTTON HANDLERS ===
    
    def _toggle_voice(self):
        """Toggle voice on/off"""
        self.assistant.context.voice_enabled = not self.assistant.context.voice_enabled
        
        if self.assistant.context.voice_enabled:
            self.toggle_btn.configure(
                text="🔊 Voice ON", 
                fg_color="#27ae60"
            )
            self._update_response_box("Voice activated.")
        else:
            self.toggle_btn.configure(
                text="🔇 Voice OFF", 
                fg_color="#e74c3c"
            )
            self._update_response_box("Voice muted.")
            self.assistant.tts.stop()
    
    def _on_tap_to_speak(self):
        """Handle tap-to-speak button"""
        # Run assistant.run_once() in background thread
        def listen_thread():
            try:
                should_continue = self.assistant.run_once()
                if not should_continue:
                    # Exit requested
                    self.app.after(100, self.app.destroy)
            except Exception as e:
                self._logger.error(f"Listen thread error: {e}", exc_info=True)
        
        Thread(target=listen_thread, daemon=True).start()
    
    def _show_help(self):
        """Show help commands"""
        help_text = """
📋 AVAILABLE COMMANDS:

🔍 INFORMATION:
    • "Wikipedia [topic]" - Search Wikipedia
    • "What time is it?" - Current time
    • "What's the date?" - Current date
    • "Weather" - Weather info
    • "Tell me a joke" - Random joke

🖥️ SYSTEM:
    • "System info" - CPU, RAM, disk usage
    • "Battery status" - Battery level & time
    • "Running apps" - List active apps

🌐 APPLICATIONS:
    • "Open YouTube/Google/Gmail/etc."
    • "Open Calculator/Notepad/etc."

🧮 CALCULATOR:
    • "Calculate [expression]" - Math
    • "20% of 500" - Percentage
    • "What is 5 plus 3 times 2"

⚙️ SYSTEM ACTIONS:
    • "Shutdown/Restart/Log off/Sleep"

❌ EXIT:
    • "Exit/Quit/Goodbye" - Close DeskAI
"""
        self._update_response_box(help_text.strip())
    
    # === IDLE ANIMATION ===
    
    def _animate_idle_state(self):
        """Animate command box when idle"""
        if not self._listening_active and not self.assistant.tts.is_speaking():
            phrase = self._animation_phrases[self._current_phrase_index]
            text = f"{phrase}{'.' * self._current_dot_count}"
            self._update_command_box(text)
            
            self._current_dot_count += 1
            if self._current_dot_count > 5:
                self._current_dot_count = 1
                self._current_phrase_index = (
                    self._current_phrase_index + 1
                ) % len(self._animation_phrases)
        
        # Schedule next animation frame
        self.app.after(500, self._animate_idle_state)
    
    # === MAIN LOOP ===
    
    def run(self):
        """Start GUI main loop"""
        # Start idle animation
        self.app.after(0, self._animate_idle_state)
        
        # Run main loop (blocks until window closed)
        self.app.mainloop()