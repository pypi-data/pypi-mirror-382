import threading

# A simple, thread-safe buffer for the Hub to store the latest frame.
_latest_frame = None
_frame_lock = threading.Lock()

def update_frame(frame):
    """Updates the global frame buffer."""
    global _latest_frame
    with _frame_lock:
        _latest_frame = frame

def get_frame():
    """Retrieves the latest frame from the global buffer."""
    with _frame_lock:
        return _latest_frame 