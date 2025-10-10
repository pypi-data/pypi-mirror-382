from flask import Blueprint, Response, stream_with_context, request
import cv2
import numpy as np
import logging
import time
from . import frame_buffer

logger = logging.getLogger(__name__)
# 设置logger只记录CRITICAL级别,静默ERROR和WARNING
logger.setLevel(logging.CRITICAL)

video_bp = Blueprint('video_bp', __name__)

@video_bp.route('/upload', methods=['POST'])
def upload_frame():
    """Receives a JPEG frame from a Producer and updates the buffer."""
    jpeg_data = request.data
    if jpeg_data:
        try:
            np_arr = np.frombuffer(jpeg_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is not None:
                frame_buffer.update_frame(frame)
                return "Frame received", 200
            return "Decode error", 400
        except Exception as e:
            logger.error(f"Error processing uploaded frame: {e}", exc_info=True)
            return "Server error", 500
    return "No data", 400

def _stream_generator():
    """Streams frames from the buffer to web clients."""
    while True:
        frame = frame_buffer.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@video_bp.route('/video')
def video_feed():
    """The video streaming route."""
    return Response(stream_with_context(_stream_generator()),
                    mimetype='multipart/x-mixed-replace; boundary=frame') 