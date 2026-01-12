"""
Speech Engine - Text-to-Speech and Speech-to-Text abstraction
"""
import logging
from typing import Optional, Callable
from threading import Lock
import pyttsx3
import speech_recognition as sr


class SpeechEngine:
    """
    Thread-safe TTS engine wrapper.
    Handles initialization, voice configuration, and graceful failures.
    """
    
    def __init__(self, rate: int = 175, voice_id: Optional[str] = None):
        self._engine = None
        self._lock = Lock()
        self._is_speaking = False
        self._logger = logging.getLogger(__name__)
        
        try:
            self._init_engine(rate, voice_id)
        except Exception as e:
            self._logger.error(f"TTS initialization failed: {e}")
    
    def _init_engine(self, rate: int, voice_id: Optional[str]):
        """Initialize pyttsx3 engine with fallback"""
        try:
            self._engine = pyttsx3.init('sapi5')
        except Exception:
            self._logger.warning("SAPI5 unavailable, using default TTS")
            try:
                self._engine = pyttsx3.init()
            except Exception as e:
                self._logger.error(f"No TTS engine available: {e}")
                return
        
        # Configure voice
        voices = self._engine.getProperty('voices')
        if voice_id:
            self._engine.setProperty('voice', voice_id)
        elif len(voices) > 1:
            self._engine.setProperty('voice', voices[1].id)
        else:
            self._engine.setProperty('voice', voices[0].id)
        
        self._engine.setProperty('rate', rate)
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Speak text using TTS engine.
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        
        Returns:
            True if successful, False if TTS unavailable
        """
        if not self._engine:
            self._logger.warning("TTS engine not available")
            return False
        
        with self._lock:
            try:
                self._is_speaking = True
                self._engine.say(text)
                if blocking:
                    self._engine.runAndWait()
                return True
            except Exception as e:
                self._logger.error(f"TTS error: {e}")
                return False
            finally:
                self._is_speaking = False
    
    def stop(self):
        """Stop current speech"""
        if self._engine:
            try:
                self._engine.stop()
            except Exception as e:
                self._logger.error(f"Stop TTS error: {e}")
        self._is_speaking = False
    
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self._is_speaking
    
    def set_rate(self, rate: int):
        """Change speech rate"""
        if self._engine:
            with self._lock:
                self._engine.setProperty('rate', rate)


class SpeechRecognizer:
    """
    Speech-to-Text wrapper with configurable timeouts and error handling.
    """
    
    def __init__(
        self,
        timeout: int = 6,
        phrase_time_limit: int = 12,
        ambient_duration: float = 1.0
    ):
        self._recognizer = sr.Recognizer()
        self._timeout = timeout
        self._phrase_time_limit = phrase_time_limit
        self._ambient_duration = ambient_duration
        self._logger = logging.getLogger(__name__)
    
    def listen(
        self,
        on_listening: Optional[Callable] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """
        Listen for voice input and convert to text.
        
        Args:
            on_listening: Callback when listening starts
            on_error: Callback on error with error message
        
        Returns:
            Recognized text or None on failure
        """
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self._recognizer.adjust_for_ambient_noise(
                    source, 
                    duration=self._ambient_duration
                )
                
                if on_listening:
                    on_listening()
                
                # Listen for audio
                audio = self._recognizer.listen(
                    source,
                    timeout=self._timeout,
                    phrase_time_limit=self._phrase_time_limit
                )
        
        except sr.WaitTimeoutError:
            error_msg = "No speech detected within timeout"
            self._logger.warning(error_msg)
            if on_error:
                on_error(error_msg)
            return None
        
        except sr.MicrophoneError as e:
            error_msg = f"Microphone access error: {e}"
            self._logger.error(error_msg)
            if on_error:
                on_error(error_msg)
            return None
        
        except Exception as e:
            error_msg = f"Listening error: {e}"
            self._logger.error(error_msg)
            if on_error:
                on_error(error_msg)
            return None
        
        # Recognize speech
        try:
            text = self._recognizer.recognize_google(
                audio, 
                language='en-in'
            ).lower()
            
            self._logger.info(f"Recognized: {text}")
            return text
        
        except sr.UnknownValueError:
            error_msg = "Speech not understood"
            self._logger.warning(error_msg)
            if on_error:
                on_error(error_msg)
            return None
        
        except sr.RequestError as e:
            error_msg = f"Recognition service error: {e}"
            self._logger.error(error_msg)
            if on_error:
                on_error(error_msg)
            return None
        
        except Exception as e:
            error_msg = f"Recognition error: {e}"
            self._logger.error(error_msg)
            if on_error:
                on_error(error_msg)
            return None