"""
FastAPI 适配器
=============

为现有FastAPI应用提供摄像头功能集成。
"""

import cv2
import time
import logging
import threading
import numpy as np
from typing import Optional, Callable
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from .core import CameraWorker, FrameBuffer

logger = logging.getLogger(__name__)
# 临时启用INFO级别用于调试视频流问题
logger.setLevel(logging.INFO)

class FastAPICameraManager:
    """FastAPI摄像头管理器"""

    def __init__(self):
        self._worker = None
        self._frame_buffer = FrameBuffer()
        self._lock = threading.Lock()
        self.is_running = False
        # 添加共享帧缓存用于多客户端
        self._latest_jpeg = None
        self._jpeg_lock = threading.Lock()
        self._jpeg_timestamp = 0

    def start_camera(self, source=0, width=640, height=480, fps=20, max_frames=None) -> bool:
        """启动摄像头"""
        with self._lock:
            if self._worker and self._worker.is_alive():
                logger.warning("摄像头已在运行")
                return False
            
            self._worker = CameraWorker(source, width, height, fps, max_frames)
            self._worker.start()
            self.is_running = True
            
            # 等待初始化
            time.sleep(0.3)
            logger.info(f"摄像头启动: {width}x{height} @ {fps}fps")
            return True

    def stop_camera(self) -> bool:
        """停止摄像头"""
        with self._lock:
            if not self._worker or not self._worker.is_alive():
                return False
            
            self._worker.stop()
            self._worker.join(timeout=2.0)
            self.is_running = False
            logger.info("摄像头已停止")
            return True

    def read_frame(self, timeout=0.1):
        """读取帧"""
        if not self.is_running or not self._worker:
            return None
        return self._worker.read(timeout)

    def update_frame(self, frame):
        """更新帧缓冲区"""
        self._frame_buffer.update(frame)

    def get_frame(self):
        """获取最新帧"""
        return self._frame_buffer.get()

    def get_latest_jpeg(self):
        """获取最新的JPEG缓存"""
        with self._jpeg_lock:
            return self._latest_jpeg, self._jpeg_timestamp

    def update_jpeg_cache(self, jpeg_data):
        """更新JPEG缓存"""
        with self._jpeg_lock:
            self._latest_jpeg = jpeg_data
            self._jpeg_timestamp = time.time()

    def read_and_cache_frame(self, timeout=0.1):
        """读取帧并更新JPEG缓存"""
        if not self.is_running:
            return None

        frame = self.read_frame(timeout)
        if frame is not None:
            try:
                # 编码为JPEG并缓存
                ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                if ret:
                    self.update_jpeg_cache(jpeg.tobytes())
                    return jpeg.tobytes()
            except Exception as e:
                logger.error(f"JPEG编码失败: {e}")
        return None

    def process_and_update_frame(self, frame_processor=None):
        """
        读取帧，应用处理，并更新帧缓冲区
        frame_processor: 接受帧并返回处理后帧的函数
        """
        if not self.is_running:
            return False
            
        frame = self.read_frame()
        if frame is None:
            return False
        
        # 应用处理函数
        if frame_processor:
            try:
                processed_frame = frame_processor(frame)
            except Exception as e:
                logger.error(f"帧处理错误: {e}")
                processed_frame = frame
        else:
            processed_frame = frame
        
        # 更新帧缓冲区
        self.update_frame(processed_frame)
        return True

    @property
    def frame_count(self):
        """获取帧计数"""
        return self._worker.frame_count if self._worker else 0

# 全局摄像头管理器
camera_manager = FastAPICameraManager()

def add_camera_routes(app: FastAPI, prefix: str = "/camera"):
    """
    向FastAPI应用添加摄像头路由
    
    Args:
        app: FastAPI应用实例
        prefix: 路由前缀
    """
    
    @app.get(f"{prefix}/status")
    async def get_camera_status():
        """获取摄像头状态"""
        return {
            "running": camera_manager.is_running,
            "frame_count": camera_manager.frame_count
        }

    @app.get(f"{prefix}/start")
    async def start_camera(source: int = 0, width: int = 640, height: int = 480, 
                          fps: int = 20, max_frames: Optional[int] = None):
        """启动摄像头"""
        success = camera_manager.start_camera(source, width, height, fps, max_frames)
        return {
            "success": success,
            "message": "摄像头启动成功" if success else "摄像头已在运行或启动失败"
        }

    @app.get(f"{prefix}/stop")
    async def stop_camera():
        """停止摄像头"""
        success = camera_manager.stop_camera()
        return {
            "success": success,
            "message": "摄像头停止成功" if success else "摄像头未运行"
        }

    # 跟踪是否已经记录过成功消息
    _upload_success_logged = {"logged": False}

    @app.post(f"{prefix}/upload")
    async def upload_frame(request: Request):
        """接收客户端上传的帧"""
        jpeg_data = await request.body()
        if not jpeg_data:
            return {"success": False, "message": "无数据"}

        try:
            np_arr = np.frombuffer(jpeg_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is not None:
                camera_manager.update_frame(frame)
                # 只在第一次成功时记录
                if not _upload_success_logged["logged"]:
                    logger.info("✅ 帧上传管道已启动")
                    _upload_success_logged["logged"] = True
                return {"success": True, "message": "帧接收成功"}
            logger.error("帧解码失败")
            return {"success": False, "message": "解码失败"}
        except Exception as e:
            logger.error(f"处理上传帧时出错: {e}")
            return {"success": False, "message": "服务器错误"}

    # 跟踪流成功状态
    _stream_success_logged = {"logged": False}

    @app.get(f"{prefix}/stream")
    async def video_stream():
        """MJPEG视频流 - 支持Producer-Consumer模式

        改进说明：
        - 优先从frame_buffer获取上传的帧（Producer-Consumer模式）
        - 兼容直接从CameraWorker读取（传统模式）
        - 支持多客户端同时访问
        - 添加帧率控制和错误处理
        """
        def generate():
            error_count = 0
            max_errors = 10

            while True:
                try:
                    # 优先从frame_buffer获取帧（上传模式）
                    frame = camera_manager.get_frame()

                    # 如果frame_buffer为空，尝试从CameraWorker读取（传统模式）
                    if frame is None and camera_manager.is_running:
                        frame = camera_manager.read_frame(timeout=0.05)

                    if frame is not None:
                        # 编码为JPEG
                        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        if ret:
                            jpeg_data = jpeg.tobytes()

                            # 只在第一次成功时记录
                            if not _stream_success_logged["logged"]:
                                logger.info("✅ 视频流管道已启动")
                                _stream_success_logged["logged"] = True

                            # 发送MJPEG帧
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n'
                                   b'Content-Length: ' + str(len(jpeg_data)).encode() + b'\r\n\r\n' +
                                   jpeg_data + b'\r\n')

                            error_count = 0
                        else:
                            logger.error("Stream JPEG编码失败")

                    time.sleep(0.033)  # ~30 FPS

                except Exception as e:
                    error_count += 1
                    logger.error(f"MJPEG流生成错误 ({error_count}/{max_errors}): {e}")

                    if error_count >= max_errors:
                        logger.error("错误次数过多，断开连接")
                        break

                    time.sleep(0.5)

        return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

    @app.get(f"{prefix}/")
    async def camera_control():
        """摄像头控制页面"""
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>摄像头控制</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin: 50px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                img {{ max-width: 100%; border: 2px solid #333; }}
                button {{ margin: 5px; padding: 10px 20px; font-size: 16px; cursor: pointer; }}
                .status {{ margin: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>摄像头控制面板</h1>
                
                <div class="status" id="status">状态：加载中...</div>
                
                <div>
                    <button onclick="startCamera()">启动摄像头</button>
                    <button onclick="stopCamera()">停止摄像头</button>
                    <button onclick="updateStatus()">刷新状态</button>
                </div>
                
                <br>
                <img id="videoStream" src="{prefix}/stream" alt="视频流" />
                
                <script>
                    async function startCamera() {{
                        try {{
                            const response = await fetch('{prefix}/start');
                            const data = await response.json();
                            document.getElementById('status').innerHTML = data.message;
                        }} catch (e) {{
                            document.getElementById('status').innerHTML = '启动失败: ' + e.message;
                        }}
                    }}
                    
                    async function stopCamera() {{
                        try {{
                            const response = await fetch('{prefix}/stop');
                            const data = await response.json();
                            document.getElementById('status').innerHTML = data.message;
                        }} catch (e) {{
                            document.getElementById('status').innerHTML = '停止失败: ' + e.message;
                        }}
                    }}
                    
                    async function updateStatus() {{
                        try {{
                            const response = await fetch('{prefix}/status');
                            const data = await response.json();
                            document.getElementById('status').innerHTML = 
                                `状态：${{data.running ? '运行中' : '已停止'}}，帧数：${{data.frame_count}}`;
                        }} catch (e) {{
                            document.getElementById('status').innerHTML = '获取状态失败: ' + e.message;
                        }}
                    }}
                    
                    // 自动更新状态
                    setInterval(updateStatus, 2000);
                    updateStatus();
                </script>
            </div>
        </body>
        </html>
        '''
        return Response(content=html, media_type="text/html")

def setup_background_processing(app: FastAPI, frame_processor: Optional[Callable] = None, fps: int = 20):
    """
    设置后台帧处理任务
    
    Args:
        app: FastAPI应用实例
        frame_processor: 帧处理函数
        fps: 处理帧率
    """
    
    @app.on_event("startup")
    async def startup_background_task():
        """启动时的背景任务"""
        import asyncio
        asyncio.create_task(background_frame_processing(frame_processor, fps))
    
    @app.on_event("shutdown")
    async def shutdown_background_task():
        """关闭时停止摄像头"""
        camera_manager.stop_camera()

async def background_frame_processing(frame_processor: Optional[Callable] = None, fps: int = 20):
    """后台帧处理循环"""
    import asyncio
    
    delay = 1.0 / fps
    
    while True:
        try:
            if camera_manager.is_running:
                frame = camera_manager.read_frame()
                if frame is not None:
                    # 应用处理函数
                    if frame_processor:
                        try:
                            processed_frame = frame_processor(frame)
                            camera_manager.update_frame(processed_frame)
                        except Exception as e:
                            logger.error(f"帧处理错误: {e}")
                            camera_manager.update_frame(frame)
                    else:
                        camera_manager.update_frame(frame)
            
            await asyncio.sleep(delay)
        except Exception as e:
            logger.error(f"后台处理错误: {e}")
            await asyncio.sleep(1)  # 错误时等待更长时间 