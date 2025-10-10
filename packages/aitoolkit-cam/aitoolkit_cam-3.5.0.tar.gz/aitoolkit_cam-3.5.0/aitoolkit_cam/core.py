"""
aitoolkit_cam 核心模块
===================

提供简洁的Camera类，自动处理简单模式和后端集成。
"""

import cv2
import time
import logging
import threading
import queue
import requests
import socket
import atexit
import weakref
from typing import Optional, Callable
from flask import Flask, Response
from .config import get_config
from .device_manager import CameraDeviceManager, validate_camera

logger = logging.getLogger(__name__)
# 设置logger只记录CRITICAL级别,静默ERROR和WARNING
logger.setLevel(logging.CRITICAL)

# 全局注册表，用于追踪所有摄像头实例，确保程序退出时释放
_active_cameras = weakref.WeakSet()

class CameraWorker(threading.Thread):
    """摄像头工作线程，负责视频捕获"""

    def __init__(self, source=0, width=640, height=480, fps=20, max_frames=None):
        super().__init__(daemon=False)  # 改为非daemon模式，确保资源清理
        self.source = source
        self.width = width
        self.height = height
        self.fps = fps
        self.max_frames = max_frames
        self.frame_queue = queue.Queue(maxsize=1)
        self._stop_event = threading.Event()
        self.is_running = False
        self.frame_count = 0
        self._cap = None  # 摄像头对象引用
        self._cap_lock = threading.Lock()  # 添加锁保护摄像头对象

    def __del__(self):
        """析构函数确保资源清理"""
        self._force_release_camera()

    def _force_release_camera(self):
        """强制释放摄像头资源"""
        with self._cap_lock:
            if self._cap is not None:
                try:
                    self._cap.release()
                    self._cap = None
                except Exception:
                    pass  # 静默处理，避免在析构时产生异常

    def run(self):
        """工作线程主循环"""
        self.is_running = True
        self.frame_count = 0
        retry_count = 0
        max_retries = 3
        
        try:
            self._cap = cv2.VideoCapture(self.source)
            if not self._cap.isOpened():
                logger.error(f"无法打开摄像头: {self.source}")
                self.is_running = False
                return
            
            # 设置摄像头参数
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self._cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # 验证设置是否生效
            actual_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self._cap.get(cv2.CAP_PROP_FPS))
            logger.info(f"摄像头参数: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            while not self._stop_event.is_set():
                try:
                    # 检查最大帧数限制
                    if self.max_frames and self.frame_count >= self.max_frames:
                        logger.info(f"达到最大帧数 ({self.max_frames})，停止捕获")
                        break
                    
                    ret, frame = self._cap.read()
                    if not ret:
                        retry_count += 1
                        if retry_count >= max_retries:
                            logger.error(f"连续 {max_retries} 次读取帧失败，停止捕获")
                            break
                        logger.warning(f"读取帧失败，重试中... ({retry_count}/{max_retries})")
                        time.sleep(0.5)
                        continue
                    
                    retry_count = 0  # 重置重试计数
                    self.frame_count += 1
                    
                    # 更新帧队列（保持最新帧）
                    if not self.frame_queue.empty():
                        try:
                            self.frame_queue.get_nowait()
                        except queue.Empty:
                            pass
                    
                    self.frame_queue.put(frame)
                    time.sleep(1 / self.fps)
                    
                except Exception as e:
                    logger.error(f"帧处理过程中发生错误: {e}")
                    time.sleep(0.1)
                    continue
                    
        except Exception as e:
            logger.error(f"摄像头工作线程发生严重错误: {e}")
        finally:
            # 使用锁安全释放摄像头资源
            with self._cap_lock:
                if self._cap is not None:
                    try:
                        self._cap.release()
                        self._cap = None
                    except Exception:
                        pass  # 静默处理
            self.is_running = False
            logger.info("摄像头工作线程停止")

    def stop(self):
        """停止工作线程"""
        self._stop_event.set()
        # 等待线程安全结束
        if self.is_alive() and threading.current_thread() != self:
            self.join(timeout=3.0)  # 增加超时时间，确保线程有足够时间清理
        # 强制释放摄像头（确保即使join超时也能释放）
        self._force_release_camera()

    def read(self, timeout=1.0):
        """读取一帧"""
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None

class FrameBuffer:
    """线程安全的帧缓冲区"""
    
    def __init__(self):
        self._frame = None
        self._lock = threading.Lock()
    
    def update(self, frame):
        """更新帧"""
        with self._lock:
            self._frame = frame
    
    def get(self):
        """获取最新帧"""
        with self._lock:
            return self._frame

class Camera:
    """
    摄像头主类
    
    自动检测后端服务，支持简单模式和后端集成模式。
    用户代码保持不变，无需关心后端服务的存在。
    """
    
    def __init__(self, source=0, width=None, height=None, fps=None, max_frames=None, port=None):
        # 使用配置文件的默认值
        self.source = source
        self.width = width or get_config("camera.default_width", 640)
        self.height = height or get_config("camera.default_height", 480)
        self.fps = fps or get_config("camera.default_fps", 20)
        self.max_frames = max_frames
        self.port = port or get_config("server.default_port", 9000)

        # 验证最大帧数限制
        max_limit = get_config("camera.max_frames_limit", 10000)
        if self.max_frames and self.max_frames > max_limit:
            logger.warning(f"最大帧数 {self.max_frames} 超过限制 {max_limit}，已调整")
            self.max_frames = max_limit

        # 初始化组件
        self._worker = None
        self._frame_buffer = FrameBuffer()
        self.is_running = False

        # 注册到全局清理列表
        _active_cameras.add(self)

        # 检测后端服务
        self._backend_url = self._detect_backend()
        self._simple_mode = (self._backend_url is None)
        
        # 简单模式需要内置服务器
        if self._simple_mode:
            self._flask_app = None
            self._server_thread = None
            self._setup_flask_server()
        
        logger.info(f"Camera初始化完成，模式: {'简单模式' if self._simple_mode else '后端模式'}")

    def _detect_backend(self) -> Optional[str]:
        """检测后端服务"""
        candidates = get_config("network.backend_candidates", [
            "http://127.0.0.1:8000/camera",
            "http://localhost:8000/camera", 
            "http://127.0.0.1:5000/camera",
            "http://localhost:5000/camera"
        ])
        timeout = get_config("network.backend_detection_timeout", 1.0)
        
        for url in candidates:
            try:
                response = requests.get(f"{url}/status", timeout=timeout)
                if response.status_code == 200:
                    logger.info(f"检测到后端服务: {url}")
                    return url
            except (requests.RequestException, ConnectionError, TimeoutError) as e:
                logger.debug(f"检测 {url} 失败: {e}")
                continue
            except Exception as e:
                logger.warning(f"检测 {url} 时发生未知错误: {e}")
                continue
        
        logger.info("未检测到后端服务，将使用简单模式")
        return None

    def _setup_flask_server(self):
        """设置内置Flask服务器"""
        self._flask_app = Flask(__name__)
        
        # 抑制Flask日志
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        
        @self._flask_app.route('/')
        def index():
            return '''
            <html>
            <head><title>Camera Stream</title></head>
            <body style="text-align: center; padding: 50px;">
                <h1>摄像头视频流</h1>
                <img src="/video" style="max-width: 90%; border: 2px solid #333;">
            </body>
            </html>
            '''
        
        @self._flask_app.route('/video')
        def video_feed():
            def generate():
                while True:
                    frame = self._frame_buffer.get()
                    if frame is not None:
                        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                        if ret:
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
                    time.sleep(0.033)  # ~30 FPS
            
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def _get_local_ip(self):
        """获取本地IP地址"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"

    def start(self) -> str:
        """启动摄像头，返回视频流URL"""
        if self.is_running:
            logger.warning("摄像头已在运行")
            return self._get_stream_url()
        
        # 启动摄像头工作线程
        self._worker = CameraWorker(self.source, self.width, self.height, self.fps, self.max_frames)
        self._worker.start()
        self.is_running = True
        
        # 等待摄像头初始化
        time.sleep(0.3)
        
        if self._simple_mode:
            # 简单模式：启动内置服务器
            self._start_flask_server()
            url = f"http://{self._get_local_ip()}:{self.port}"
            logger.info(f"摄像头启动成功，访问: {url}")
            return url
        else:
            # 后端模式：通知后端启动
            try:
                params = {
                    'source': self.source,
                    'width': self.width,
                    'height': self.height,
                    'fps': self.fps,
                    'max_frames': self.max_frames
                }
                response = requests.get(f"{self._backend_url}/start", params=params, timeout=2)
                if response.status_code == 200:
                    url = self._backend_url.replace('/camera', '') + '/camera/stream'
                    logger.info(f"连接到后端成功，访问: {url}")
                    return url
            except Exception as e:
                logger.warning(f"连接后端失败: {e}，切换到简单模式")
                return self._fallback_to_simple_mode()

    def _start_flask_server(self):
        """启动Flask服务器"""
        if self._server_thread is None:
            def run_server():
                self._flask_app.run(host='0.0.0.0', port=self.port, threaded=True, use_reloader=False)
            
            self._server_thread = threading.Thread(target=run_server, daemon=True)
            self._server_thread.start()
            time.sleep(0.3)  # 等待服务器启动

    def _fallback_to_simple_mode(self):
        """回退到简单模式"""
        self._simple_mode = True
        self._backend_url = None
        self._start_flask_server()
        url = f"http://{self._get_local_ip()}:{self.port}"
        logger.info(f"回退到简单模式，访问: {url}")
        return url

    def _get_stream_url(self):
        """获取当前流URL"""
        if self._simple_mode:
            return f"http://{self._get_local_ip()}:{self.port}"
        else:
            return self._backend_url.replace('/camera', '') + '/camera/stream'

    def stop(self):
        """停止摄像头"""
        if not self.is_running:
            return
        
        # 通知后端停止（如果是后端模式）
        if not self._simple_mode and self._backend_url:
            try:
                requests.get(f"{self._backend_url}/stop", timeout=1)
            except:
                pass
        
        # 停止工作线程
        if self._worker:
            self._worker.stop()
            self._worker.join(timeout=2.0)
        
        self.is_running = False
        logger.info("摄像头已停止")

    def read(self, timeout=1.0):
        """读取原始帧"""
        if not self.is_running or not self._worker:
            return None
        
        # 更新运行状态
        if not self._worker.is_running:
            self.is_running = False
            return None
        
        return self._worker.read(timeout)

    def show(self, frame):
        """显示处理后的帧"""
        if self._simple_mode:
            # 简单模式：更新本地缓冲区
            self._frame_buffer.update(frame)
        else:
            # 后端模式：发送到后端
            try:
                ret, jpeg_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                if ret:
                    requests.post(f"{self._backend_url}/upload", 
                                data=jpeg_data.tobytes(),
                                headers={'Content-Type': 'image/jpeg'},
                                timeout=0.5)
            except Exception as e:
                logger.warning(f"发送帧到后端失败: {e}")

    @property
    def frame_count(self):
        """获取当前帧计数"""
        return self._worker.frame_count if self._worker else 0

    def __iter__(self):
        """支持迭代器模式"""
        return self

    def __next__(self):
        """迭代器实现"""
        if not self.is_running:
            raise StopIteration
        
        frame = self.read(timeout=1.0)
        if frame is None:
            if not self._worker.is_running:
                raise StopIteration
            return None
        return frame

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()

# 全局清理函数，程序退出时调用
def _cleanup_all_cameras():
    """程序退出时强制清理所有摄像头资源"""
    try:
        # 复制weakset避免在迭代时修改
        cameras_to_clean = list(_active_cameras)
        for camera in cameras_to_clean:
            try:
                if camera.is_running:
                    camera.stop()
            except Exception:
                pass  # 静默处理,避免在退出时产生异常
    except Exception:
        pass

# 注册atexit清理函数
atexit.register(_cleanup_all_cameras)