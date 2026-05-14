import speech_recognition as sr
import logging
import threading
import time
from collections import deque

logger = logging.getLogger(__name__)

# ==========================================
# VOICE COMMAND CONFIGURATION
# ==========================================

VOICE_TIMEOUT = 10.0  # Seconds to listen for voice
VOICE_PHRASE_TIMEOUT = 5.0  # Max time for single phrase
COMMAND_QUEUE_MAX = 10  # Max pending commands
LISTEN_RETRIES = 3  # Retry attempts on error

# ==========================================
# VOICE STATE MANAGEMENT
# ==========================================

class VoiceState:
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"

class VoiceManager:
    """
    Thread-safe voice command recognition with background processing,
    command queueing, and error handling.
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Adjust sensitivity
        self.state = VoiceState.IDLE
        self.command_queue = deque(maxlen=COMMAND_QUEUE_MAX)
        self.thread = None
        self.running = False
        self.last_error = None
        self.last_command = None
        self.command_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
        logger.info("VoiceManager initialized")
    
    def start(self):
        """
        Start voice recognition in background thread.
        """
        with self.lock:
            if self.state in [VoiceState.LISTENING, VoiceState.PROCESSING]:
                logger.warning(f"Voice already {self.state}")
                return False
            
            self.state = VoiceState.IDLE
            self.running = True
            self.thread = threading.Thread(target=self._recognition_loop, daemon=True)
            self.thread.start()
            logger.info("Voice recognition started")
            return True
    
    def stop(self):
        """
        Stop voice recognition and cleanup.
        """
        with self.lock:
            if self.state == VoiceState.STOPPED:
                logger.warning("Voice already stopped")
                return True
            
            self.running = False
        
        # Wait for thread to finish (max 2 seconds)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        self.state = VoiceState.STOPPED
        logger.info("Voice recognition stopped")
        return True
    
    def _recognition_loop(self):
        """
        Background thread that listens for voice commands continuously.
        """
        try:
            while self.running:
                try:
                    with self.lock:
                        self.state = VoiceState.LISTENING
                    
                    # Listen with timeout
                    with sr.Microphone() as source:
                        logger.debug("Listening for voice command...")
                        audio = self.recognizer.listen(
                            source,
                            timeout=VOICE_TIMEOUT,
                            phrase_time_limit=VOICE_PHRASE_TIMEOUT
                        )
                    
                    with self.lock:
                        self.state = VoiceState.PROCESSING
                    
                    # Recognize speech
                    text = self.recognizer.recognize_google(audio)
                    text_lower = text.lower().strip()
                    
                    logger.info(f"Recognized: '{text}'")
                    
                    # Queue command
                    with self.lock:
                        self.command_queue.append({
                            'text': text_lower,
                            'timestamp': time.time(),
                            'confidence': 'high'  # Google API doesn't return confidence
                        })
                        self.last_command = text_lower
                        self.command_count += 1
                        self.state = VoiceState.IDLE
                        self.last_error = None
                    
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio")
                    with self.lock:
                        self.last_error = "Audio not understood"
                        self.error_count += 1
                        self.state = VoiceState.IDLE
                
                except sr.RequestError as e:
                    logger.error(f"Recognition service error: {e}")
                    with self.lock:
                        self.last_error = f"Service error: {str(e)}"
                        self.error_count += 1
                        self.state = VoiceState.ERROR
                    time.sleep(1)  # Back off on service error
                
                except sr.WaitTimeoutError:
                    logger.debug("Listening timeout (no input)")
                    with self.lock:
                        self.state = VoiceState.IDLE
                    continue
                
                except Exception as e:
                    logger.error(f"Unexpected voice error: {e}")
                    with self.lock:
                        self.last_error = str(e)
                        self.error_count += 1
                        self.state = VoiceState.ERROR
                    time.sleep(1)
        
        except Exception as e:
            logger.error(f"Recognition loop fatal error: {e}")
            with self.lock:
                self.state = VoiceState.ERROR
                self.last_error = str(e)
    
    def get_next_command(self):
        """
        Get the next command from queue (FIFO).
        Returns None if queue is empty.
        """
        with self.lock:
            if self.command_queue:
                return self.command_queue.popleft()
            return None
    
    def peek_next_command(self):
        """
        Peek at next command without removing it.
        """
        with self.lock:
            if self.command_queue:
                return self.command_queue[0]
            return None
    
    def clear_queue(self):
        """
        Clear all pending commands.
        """
        with self.lock:
            count = len(self.command_queue)
            self.command_queue.clear()
            logger.info(f"Cleared {count} commands from queue")
            return count
    
    def get_status(self):
        """
        Get voice recognition status and statistics.
        """
        with self.lock:
            return {
                "state": self.state,
                "running": self.running,
                "queue_size": len(self.command_queue),
                "queue_max": COMMAND_QUEUE_MAX,
                "command_count": self.command_count,
                "error_count": self.error_count,
                "last_command": self.last_command,
                "error": self.last_error,
                "timeout_seconds": VOICE_TIMEOUT,
                "phrase_timeout_seconds": VOICE_PHRASE_TIMEOUT
            }

# Global voice instance
voice_manager = VoiceManager()

# ==========================================
# PUBLIC API (Backward compatible)
# ==========================================

def listen():
    """
    Legacy function - returns next queued command.
    """
    cmd = voice_manager.get_next_command()
    return cmd['text'] if cmd else None

def start_voice_recognition():
    """
    Start voice recognition.
    """
    return voice_manager.start()

def stop_voice_recognition():
    """
    Stop voice recognition.
    """
    return voice_manager.stop()

def get_voice_status():
    """
    Get voice recognition status.
    """
    return voice_manager.get_status()

def get_voice_command():
    """
    Get next voice command from queue.
    """
    return voice_manager.get_next_command()

def clear_voice_queue():
    """
    Clear pending voice commands.
    """
    return voice_manager.clear_queue()