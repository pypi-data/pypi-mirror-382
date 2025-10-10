from flask import Flask
from .video_blueprint import video_bp
import logging
import socket

class Hub:
    """
    The Hub server. This class starts a Flask web server to receive
    frames from Producers and stream them to web clients.
    """
    def __init__(self, host='0.0.0.0', port=5000):
        self.app = Flask(__name__)
        self.app.register_blueprint(video_bp)
        self.host = host
        self.port = port
        self.url = f"http://{self._get_local_ip()}:{self.port}"
        
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        @self.app.route('/')
        def index():
            return f'<h1>Camera Hub</h1><p>Streaming from remote producers.</p><img src="/video">'

    def run(self):
        """Starts the Flask server."""
        logging.info(f"Starting Hub server. View the stream at {self.url}")
        self.app.run(host=self.host, port=self.port, threaded=True)

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1" 