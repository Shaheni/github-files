import cv2
import logging
import threading
import time
from collections import deque

logger = logging.getLogger(__name__)

# ==========================================
# CAMERA CONFIGURATION
# ==========================================

CAMERA_INDEX = 0  # Default camera device
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
MAX_FRAME_BUFFER = 2  # Keep only latest 2 frames
FRAME_ENCODING_QUALITY = 80  # JPEG quality
CAMERA_TIMEOUT = 5.0  # Seconds to wait for camera response

# ==========================================
# CAMERA STATE MANAGEMENT
# ==========================================

class CameraState:
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"

class CameraManager:
    """
    Thread-safe camera management with frame buffering,
    error handling, and resource cleanup.
    """
    
    def __init__(self):
        self.camera = None
        self.state = CameraState.IDLE
        self.frame_buffer = deque(maxlen=MAX_FRAME_BUFFER)
        self.thread = None
        self.running = False
        self.last_error = None
        self.last_frame_time = None
        self.frame_count = 0
        self.lock = threading.Lock()
        logger.info("CameraManager initialized")
    
    def start(self):
        """
        Start camera in background thread.
        Returns True if successful, False otherwise.
        """
        with self.lock:
            if self.state in [CameraState.RUNNING, CameraState.INITIALIZING]:
                logger.warning(f"Camera already {self.state}")
                return False
            
            self.state = CameraState.INITIALIZING
            self.running = True
            self.thread = threading.Thread(target=self._camera_loop, daemon=True)
            self.thread.start()
            logger.info("Camera start initiated")
            return True
    
    def stop(self):
        """
        Stop camera and clean up resources.
        """
        with self.lock:
            if self.state == CameraState.STOPPED:
                logger.warning("Camera already stopped")
                return True
            
            self.running = False
        
        # Wait for thread to finish (max 2 seconds)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        self._cleanup()
        self.state = CameraState.STOPPED
        logger.info("Camera stopped")
        return True
    
    def _camera_loop(self):
        """
        Background thread that captures frames continuously.
        """
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(CAMERA_INDEX)
            
            if not self.camera.isOpened():
                raise RuntimeError(f"Failed to open camera device {CAMERA_INDEX}")
            
            # Configure camera
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffering
            
            with self.lock:
                self.state = CameraState.RUNNING
            
            logger.info(f"Camera initialized: {CAMERA_WIDTH}x{CAMERA_HEIGHT} @ {CAMERA_FPS}fps")
            
            # Capture loop
            while self.running:
                ret, frame = self.camera.read()
                
                if not ret:
                    self.last_error = "Failed to read frame from camera"
                    logger.error(self.last_error)
                    with self.lock:
                        self.state = CameraState.ERROR
                    break
                
                # Encode frame to JPEG
                success, encoded = cv2.imencode('.jpg', frame, 
                    [cv2.IMWRITE_JPEG_QUALITY, FRAME_ENCODING_QUALITY])
                
                if not success:
                    logger.warning("Failed to encode frame")
                    continue
                
                # Add to buffer
                with self.lock:
                    self.frame_buffer.append(encoded.tobytes())
                    self.last_frame_time = time.time()
                    self.frame_count += 1
        
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Camera loop error: {self.last_error}")
            with self.lock:
                self.state = CameraState.ERROR
        
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """
        Release camera resources.
        """
        if self.camera:
            try:
                self.camera.release()
                logger.info("Camera released")
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")
            finally:
                self.camera = None
        
        with self.lock:
            self.frame_buffer.clear()
    
    def get_latest_frame(self):
        """
        Get the latest encoded frame (JPEG bytes).
        Returns None if no frame available.
        """
        with self.lock:
            if self.frame_buffer:
                return self.frame_buffer[-1]  # Get latest frame
            return None
    
    def get_status(self):
        """
        Get camera status and statistics.
        """
        with self.lock:
            return {
                "state": self.state,
                "running": self.running,
                "frame_count": self.frame_count,
                "frames_buffered": len(self.frame_buffer),
                "last_frame_time": self.last_frame_time,
                "error": self.last_error,
                "camera_index": CAMERA_INDEX,
                "resolution": f"{CAMERA_WIDTH}x{CAMERA_HEIGHT}",
                "fps": CAMERA_FPS
            }

# Global camera instance
camera_manager = CameraManager()

# ==========================================
# PUBLIC API
# ==========================================

def initialize_camera():
    """
    Initialize and start camera.
    """
    return camera_manager.start()

def shutdown_camera():
    """
    Stop camera and cleanup.
    """
    return camera_manager.stop()

def get_camera_status():
    """
    Get current camera status.
    """
    return camera_manager.get_status()

def generate_frames():
    """
    Generator for streaming MJPEG frames.
    Yields MJPEG boundary and frame data.
    """
    while True:
        frame = camera_manager.get_latest_frame()
        
        if frame is None:
            time.sleep(0.01)  # Wait for frame
            continue
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + str(len(frame)).encode() + b'\r\n\r\n' +
               frame + b'\r\n')