"""
配置管理模块
===========

提供统一的配置管理功能，支持默认配置和用户自定义配置。
"""

import os
import json
import logging
from typing import Dict, Any, Union
from functools import lru_cache

logger = logging.getLogger(__name__)
# 设置logger只记录CRITICAL级别,静默ERROR和WARNING
logger.setLevel(logging.CRITICAL)

# 默认配置
DEFAULT_CONFIG = {
    "camera": {
        "default_width": 640,
        "default_height": 480,
        "default_fps": 20,
        "max_frames_limit": 10000,
        "retry_attempts": 3,
        "retry_delay": 0.5
    },
    "network": {
        "backend_detection_timeout": 1.0,
        "backend_candidates": [
            "http://127.0.0.1:18001/camera",
            "http://localhost:18001/camera",
            "http://127.0.0.1:5000/camera",
            "http://localhost:5000/camera",
            "http://127.0.0.1:6000/camera",
            "http://localhost:6000/camera",
            "http://127.0.0.1:7000/camera",
            "http://localhost:7000/camera",
            "http://127.0.0.1:8000/camera",
            "http://localhost:8000/camera",
            "http://127.0.0.1:9000/camera",
            "http://localhost:9000/camera"
        ],
        "upload_timeout": 0.5,
        "stream_quality": 90
    },
    "flask": {
        "default_port": 9000,
        "host": "0.0.0.0",
        "threaded": True,
        "use_reloader": False
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "suppress_flask": True
    },
    "performance": {
        "frame_buffer_size": 3,
        "stream_fps": 30,
        "processing_timeout": 1.0
    }
}

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self._config_loaded = False
        self._config_path = None
    
    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径，如果为None则尝试默认位置
        
        Returns:
            加载后的完整配置字典
        """
        if config_path is None:
            # 尝试默认配置文件位置
            possible_paths = [
                "aitoolkit_cam_config.json",
                os.path.expanduser("~/.aitoolkit_cam/config.json"),
                "/etc/aitoolkit_cam/config.json"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
                    self._config_path = config_path
                    logger.info(f"已加载配置文件: {config_path}")
            except json.JSONDecodeError as e:
                logger.error(f"配置文件JSON格式错误: {e}")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
        
        self._config_loaded = True
        return self._config
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """
        合并用户配置到默认配置
        
        Args:
            user_config: 用户配置字典
        """
        def deep_merge(default: Dict, user: Dict):
            """深度合并字典"""
            for key, value in user.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    deep_merge(default[key], value)
                else:
                    default[key] = value
        
        deep_merge(self._config, user_config)
    
    def get(self, key: str, default=None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        
        Args:
            key: 配置键，支持 "section.subsection.key" 格式
            default: 默认值
        
        Returns:
            配置值
        """
        if not self._config_loaded:
            self.load_config()
        
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键，支持 "section.subsection.key" 格式
            value: 配置值
        """
        if not self._config_loaded:
            self.load_config()
        
        keys = key.split('.')
        config = self._config
        
        # 导航到目标位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def save_config(self, config_path: str = None):
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径，如果为None则使用加载时的路径
        """
        if config_path is None:
            config_path = self._config_path
        
        if config_path is None:
            config_path = "aitoolkit_cam_config.json"
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存到: {config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def reset_to_default(self):
        """重置为默认配置"""
        self._config = DEFAULT_CONFIG.copy()
        logger.info("配置已重置为默认值")
    
    def get_all(self) -> Dict[str, Any]:
        """获取完整配置"""
        if not self._config_loaded:
            self.load_config()
        return self._config.copy()

# 全局配置管理器实例
_config_manager = ConfigManager()

def get_config(key: str, default=None) -> Any:
    """
    获取配置值的便捷函数
    
    Args:
        key: 配置键
        default: 默认值
    
    Returns:
        配置值
    """
    return _config_manager.get(key, default)

def set_config(key: str, value: Any):
    """
    设置配置值的便捷函数
    
    Args:
        key: 配置键
        value: 配置值
    """
    _config_manager.set(key, value)

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    加载配置文件的便捷函数
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        完整配置字典
    """
    return _config_manager.load_config(config_path)

def save_config(config_path: str = None):
    """
    保存配置文件的便捷函数
    
    Args:
        config_path: 配置文件路径
    """
    _config_manager.save_config(config_path)

def reset_config():
    """重置配置为默认值的便捷函数"""
    _config_manager.reset_to_default()

# 配置验证函数
def validate_config():
    """验证配置的有效性"""
    config = _config_manager.get_all()
    
    # 验证摄像头配置
    camera_config = config.get("camera", {})
    if camera_config.get("default_width", 0) <= 0:
        logger.warning("摄像头宽度配置无效，使用默认值")
        set_config("camera.default_width", 640)
    
    if camera_config.get("default_height", 0) <= 0:
        logger.warning("摄像头高度配置无效，使用默认值")
        set_config("camera.default_height", 480)
    
    if camera_config.get("default_fps", 0) <= 0:
        logger.warning("摄像头FPS配置无效，使用默认值")
        set_config("camera.default_fps", 20)
    
    # 验证网络配置
    network_config = config.get("network", {})
    if network_config.get("backend_detection_timeout", 0) <= 0:
        logger.warning("后端检测超时配置无效，使用默认值")
        set_config("network.backend_detection_timeout", 1.0)
    
    logger.debug("配置验证完成")

# 初始化时验证配置
validate_config()