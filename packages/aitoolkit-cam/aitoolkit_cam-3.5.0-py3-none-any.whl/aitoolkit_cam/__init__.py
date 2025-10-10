"""
aitoolkit_cam - ARM摄像头工具包
=============================

简单易用的摄像头库，专为ARM设备和Jupyter环境设计。

基本使用:
    from aitoolkit_cam import Camera
    
    with Camera(source=0, max_frames=100) as cam:
        url = cam.start()
        for frame in cam:
            # OpenCV处理
            processed = your_processing(frame)
            cam.show(processed)

FastAPI集成:
    from aitoolkit_cam import add_camera_routes
    
    add_camera_routes(app, prefix="/camera")

Producer/Hub模式:
    from aitoolkit_cam import Hub, get_video_blueprint
    
    # 启动Hub服务器
    hub = Hub(port=5000)
    hub.run()
"""

# 导入核心功能
from .core import Camera, CameraWorker, FrameBuffer

# 导入配置管理
from .config import get_config, set_config, load_config, save_config, reset_config

# 导入设备管理
from .device_manager import (
    list_available_cameras, get_optimal_camera, validate_camera, 
    get_camera_info, get_camera_capabilities, clear_device_cache
)

# 导入图像处理
from .filters import (
    ImageFilters, FilterChain, TextOverlay,
    create_vintage_filter, create_artistic_filter, create_dramatic_filter
)

# 导入FastAPI集成
try:
    from .fastapi_adapter import add_camera_routes, setup_background_processing, camera_manager
    _fastapi_available = True
except ImportError as e:
    _fastapi_available = False
    import logging
    logging.warning(f"FastAPI features not available: {e}")

# 导入传统Producer/Hub架构组件
try:
    from .hub import Hub
    from .video_blueprint import video_bp as get_video_blueprint
    from . import frame_buffer
    _producer_hub_available = True
except ImportError as e:
    _producer_hub_available = False
    import logging
    logging.warning(f"Producer/Hub features not available: {e}")

# 兼容性辅助函数
def start_camera(source=0, width=640, height=480, fps=20, max_frames=None):
    """辅助函数：创建并启动CameraWorker"""
    worker = CameraWorker(source, width, height, fps, max_frames)
    worker.start()
    return worker

def stop_camera(worker):
    """辅助函数：停止CameraWorker"""
    if worker and worker.is_alive():
        worker.stop()
        worker.join(timeout=2.0)

__version__ = "3.0.0"
__author__ = "Haitao Wang"

# 构建动态导出列表
__all__ = [
    # 核心功能
    'Camera', 'CameraWorker', 'FrameBuffer', 'start_camera', 'stop_camera',
    
    # 配置管理
    'get_config', 'set_config', 'load_config', 'save_config', 'reset_config',
    
    # 设备管理
    'list_available_cameras', 'get_optimal_camera', 'validate_camera', 
    'get_camera_info', 'get_camera_capabilities', 'clear_device_cache',
    
    # 图像处理
    'ImageFilters', 'FilterChain', 'TextOverlay',
    'create_vintage_filter', 'create_artistic_filter', 'create_dramatic_filter'
]

if _fastapi_available:
    __all__.extend(['add_camera_routes', 'setup_background_processing', 'camera_manager'])

if _producer_hub_available:
    __all__.extend(['Hub', 'get_video_blueprint', 'frame_buffer'])

# 设置日志 - 只显示CRITICAL级别，抑制ERROR和WARNING
import logging
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.CRITICAL,  # 只显示致命错误，不显示ERROR和WARNING
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# 强力抑制OpenCV的所有日志输出
import os
import cv2
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'  # 完全静默
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'    # 关闭VideoIO调试信息
cv2.setLogLevel(0)  # 0 = SILENT, 1 = FATAL, 2 = ERROR, 3 = WARNING, 4 = INFO, 5 = DEBUG 