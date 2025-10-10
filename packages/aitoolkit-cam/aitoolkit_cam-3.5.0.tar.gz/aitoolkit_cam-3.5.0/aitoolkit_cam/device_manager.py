"""
摄像头设备管理模块
================

提供摄像头设备检测、验证和管理功能。
"""

import cv2
import logging
import threading
import time
from typing import List, Dict, Optional, Tuple
from .config import get_config

logger = logging.getLogger(__name__)
# 设置logger只记录CRITICAL级别,静默ERROR和WARNING
logger.setLevel(logging.CRITICAL)

class CameraDeviceInfo:
    """摄像头设备信息"""
    
    def __init__(self, device_id: int, width: int = 0, height: int = 0, 
                 fps: float = 0.0, available: bool = False):
        self.device_id = device_id
        self.width = width
        self.height = height
        self.fps = fps
        self.available = available
        self.backend_name = ""
        self.last_check = time.time()
    
    def __str__(self):
        return (f"Camera({self.device_id}): {self.width}x{self.height}@{self.fps}fps "
                f"[{'可用' if self.available else '不可用'}]")
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "device_id": self.device_id,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "available": self.available,
            "backend_name": self.backend_name,
            "last_check": self.last_check
        }

class CameraDeviceManager:
    """摄像头设备管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._devices = {}  # device_id -> CameraDeviceInfo
        self._cache_timeout = get_config("performance.device_cache_timeout", 30.0)
        self._last_scan = 0
        self._scan_lock = threading.Lock()
        self._initialized = True
    
    def scan_devices(self, max_devices: int = 10, force_rescan: bool = False) -> List[CameraDeviceInfo]:
        """
        扫描可用的摄像头设备
        
        Args:
            max_devices: 最大扫描设备数量
            force_rescan: 强制重新扫描
        
        Returns:
            可用设备列表
        """
        current_time = time.time()
        
        # 检查缓存是否有效
        if not force_rescan and (current_time - self._last_scan) < self._cache_timeout:
            return list(self._devices.values())
        
        with self._scan_lock:
            # 双重检查
            if not force_rescan and (current_time - self._last_scan) < self._cache_timeout:
                return list(self._devices.values())
            
            logger.info(f"开始扫描摄像头设备 (最大 {max_devices} 个)")
            new_devices = {}
            
            for device_id in range(max_devices):
                try:
                    device_info = self._probe_device(device_id)
                    if device_info.available:
                        new_devices[device_id] = device_info
                        logger.debug(f"发现设备: {device_info}")
                except Exception as e:
                    logger.debug(f"检测设备 {device_id} 时出错: {e}")
                    continue
            
            self._devices = new_devices
            self._last_scan = current_time
            
            logger.info(f"扫描完成，发现 {len(self._devices)} 个可用设备")
            return list(self._devices.values())
    
    def _probe_device(self, device_id: int) -> CameraDeviceInfo:
        """
        探测单个设备
        
        Args:
            device_id: 设备ID
        
        Returns:
            设备信息
        """
        device_info = CameraDeviceInfo(device_id)
        
        try:
            cap = cv2.VideoCapture(device_id)
            
            if not cap.isOpened():
                return device_info
            
            # 获取设备属性
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # 尝试读取一帧来验证设备真正可用
            ret, frame = cap.read()
            if ret and frame is not None:
                device_info.width = width
                device_info.height = height
                device_info.fps = fps if fps > 0 else 30.0  # 默认FPS
                device_info.available = True
                
                # 获取后端信息
                backend = cap.getBackendName() if hasattr(cap, 'getBackendName') else "Unknown"
                device_info.backend_name = backend
            
            cap.release()
            
        except Exception as e:
            logger.debug(f"探测设备 {device_id} 失败: {e}")
        
        return device_info
    
    def get_device_info(self, device_id: int) -> Optional[CameraDeviceInfo]:
        """
        获取指定设备信息
        
        Args:
            device_id: 设备ID
        
        Returns:
            设备信息，如果不存在返回None
        """
        if device_id not in self._devices:
            # 尝试探测该设备
            device_info = self._probe_device(device_id)
            if device_info.available:
                self._devices[device_id] = device_info
            else:
                return None
        
        return self._devices.get(device_id)
    
    def get_optimal_device(self, prefer_resolution: bool = True) -> Optional[int]:
        """
        获取最佳摄像头设备ID
        
        Args:
            prefer_resolution: 是否优先选择高分辨率设备
        
        Returns:
            最佳设备ID，如果没有可用设备返回None
        """
        devices = self.scan_devices()
        
        if not devices:
            logger.warning("未找到可用的摄像头设备")
            return None
        
        if prefer_resolution:
            # 按分辨率排序（宽度 * 高度）
            best_device = max(devices, key=lambda d: d.width * d.height)
        else:
            # 选择第一个可用设备
            best_device = devices[0]
        
        logger.info(f"选择最佳设备: {best_device}")
        return best_device.device_id
    
    def is_device_available(self, device_id: int) -> bool:
        """
        检查设备是否可用
        
        Args:
            device_id: 设备ID
        
        Returns:
            设备是否可用
        """
        device_info = self.get_device_info(device_id)
        return device_info is not None and device_info.available
    
    def get_device_capabilities(self, device_id: int) -> Dict:
        """
        获取设备能力信息
        
        Args:
            device_id: 设备ID
        
        Returns:
            设备能力字典
        """
        capabilities = {
            "supported_resolutions": [],
            "supported_fps": [],
            "formats": [],
            "controls": {}
        }
        
        try:
            cap = cv2.VideoCapture(device_id)
            if not cap.isOpened():
                return capabilities
            
            # 测试常见分辨率
            common_resolutions = [
                (320, 240), (640, 480), (800, 600), (1024, 768),
                (1280, 720), (1280, 960), (1600, 1200), (1920, 1080)
            ]
            
            for width, height in common_resolutions:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                
                actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                if actual_width == width and actual_height == height:
                    capabilities["supported_resolutions"].append((width, height))
            
            # 测试FPS
            for fps in [15, 20, 25, 30, 60]:
                cap.set(cv2.CAP_PROP_FPS, fps)
                actual_fps = cap.get(cv2.CAP_PROP_FPS)
                if abs(actual_fps - fps) < 1:
                    capabilities["supported_fps"].append(fps)
            
            cap.release()
            
        except Exception as e:
            logger.debug(f"获取设备 {device_id} 能力时出错: {e}")
        
        return capabilities
    
    def clear_cache(self):
        """清除设备缓存"""
        with self._scan_lock:
            self._devices.clear()
            self._last_scan = 0
            logger.debug("设备缓存已清除")

# 全局设备管理器实例
_device_manager = CameraDeviceManager()

def list_available_cameras() -> List[CameraDeviceInfo]:
    """
    列出可用的摄像头设备
    
    Returns:
        可用设备列表
    """
    return _device_manager.scan_devices()

def get_optimal_camera() -> Optional[int]:
    """
    获取最佳摄像头设备ID
    
    Returns:
        最佳设备ID
    """
    return _device_manager.get_optimal_device()

def validate_camera(device_id: int) -> bool:
    """
    验证摄像头设备是否可用
    
    Args:
        device_id: 设备ID
    
    Returns:
        设备是否可用
    """
    return _device_manager.is_device_available(device_id)

def get_camera_info(device_id: int) -> Optional[CameraDeviceInfo]:
    """
    获取摄像头设备信息
    
    Args:
        device_id: 设备ID
    
    Returns:
        设备信息
    """
    return _device_manager.get_device_info(device_id)

def get_camera_capabilities(device_id: int) -> Dict:
    """
    获取摄像头设备能力
    
    Args:
        device_id: 设备ID
    
    Returns:
        设备能力字典
    """
    return _device_manager.get_device_capabilities(device_id)

def clear_device_cache():
    """清除设备缓存"""
    _device_manager.clear_cache()

# 性能监控装饰器
def performance_monitor(func):
    """性能监控装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.debug(f"{func.__name__} 执行时间: {end_time - start_time:.3f}s")
        return result
    return wrapper