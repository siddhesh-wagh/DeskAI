"""
Reusable UI Components for DeskAI
"""
import customtkinter as ctk
from typing import Callable, Optional


class AnimatedTextBox(ctk.CTkTextbox):
    """Text box with typing animation effect"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(state="disabled")
    
    def set_text(self, text: str):
        """Set text content"""
        self.configure(state="normal")
        self.delete("0.0", "end")
        self.insert("0.0", text)
        self.configure(state="disabled")
    
    def append_text(self, text: str):
        """Append text to existing content"""
        self.configure(state="normal")
        self.insert("end", text + "\n")
        self.see("end")
        self.configure(state="disabled")
    
    def clear(self):
        """Clear all text"""
        self.configure(state="normal")
        self.delete("0.0", "end")
        self.configure(state="disabled")


class StatusIndicator(ctk.CTkFrame):
    """Visual status indicator with color coding"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.indicator = ctk.CTkLabel(
            self,
            text="●",
            font=("Segoe UI", 20),
            text_color="#95a5a6"
        )
        self.indicator.pack(side="left", padx=5)
        
        self.label = ctk.CTkLabel(
            self,
            text="Ready",
            font=("Segoe UI", 12)
        )
        self.label.pack(side="left")
    
    def set_status(self, status: str, color: str = "#95a5a6"):
        """
        Update status display.
        
        Args:
            status: Status text
            color: Indicator color (hex)
        """
        self.label.configure(text=status)
        self.indicator.configure(text_color=color)


class VoiceButton(ctk.CTkButton):
    """Custom button with voice control styling"""
    
    def __init__(
        self, 
        parent, 
        text: str,
        command: Callable,
        icon: str = "",
        color: str = "#3498db",
        *args, 
        **kwargs
    ):
        super().__init__(
            parent,
            text=f"{icon} {text}" if icon else text,
            command=command,
            font=("Segoe UI", 16),
            height=45,
            corner_radius=20,
            fg_color=color,
            *args,
            **kwargs
        )


class ConfirmDialog(ctk.CTkToplevel):
    """Simple confirmation dialog"""
    
    def __init__(
        self, 
        parent,
        title: str,
        message: str,
        on_confirm: Callable,
        on_cancel: Optional[Callable] = None
    ):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Message
        msg_label = ctk.CTkLabel(
            self,
            text=message,
            font=("Segoe UI", 14),
            wraplength=350
        )
        msg_label.pack(pady=30, padx=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        def _on_confirm():
            on_confirm()
            self.destroy()
        
        def _on_cancel():
            if on_cancel:
                on_cancel()
            self.destroy()
        
        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="Confirm",
            command=_on_confirm,
            fg_color="#27ae60",
            width=120
        )
        confirm_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=_on_cancel,
            fg_color="#e74c3c",
            width=120
        )
        cancel_btn.pack(side="left", padx=10)


class InputDialog(ctk.CTkInputDialog):
    """Enhanced input dialog with validation"""
    
    def __init__(
        self,
        title: str,
        text: str,
        validator: Optional[Callable[[str], bool]] = None,
        error_message: str = "Invalid input"
    ):
        self._validator = validator
        self._error_message = error_message
        super().__init__(text=text, title=title)
    
    def get_input(self) -> Optional[str]:
        """Get validated input"""
        value = super().get_input()
        
        if value and self._validator:
            if not self._validator(value):
                # Could show error dialog here
                return None
        
        return value