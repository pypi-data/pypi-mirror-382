"""
图像滤镜和处理模块
================

提供常用的图像滤镜和处理效果。
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional, Callable
from .config import get_config

logger = logging.getLogger(__name__)
# 设置logger只记录CRITICAL级别,静默ERROR和WARNING
logger.setLevel(logging.CRITICAL)

class ImageFilters:
    """常用图像滤镜集合"""
    
    @staticmethod
    def edge_detection(frame: np.ndarray, low_threshold: int = 50, 
                      high_threshold: int = 150) -> np.ndarray:
        """
        边缘检测滤镜
        
        Args:
            frame: 输入帧
            low_threshold: 低阈值
            high_threshold: 高阈值
        
        Returns:
            处理后的帧
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, low_threshold, high_threshold)
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        except Exception as e:
            logger.error(f"边缘检测处理失败: {e}")
            return frame
    
    @staticmethod
    def blur_effect(frame: np.ndarray, kernel_size: int = 15) -> np.ndarray:
        """
        模糊效果
        
        Args:
            frame: 输入帧
            kernel_size: 核大小（必须为奇数）
        
        Returns:
            处理后的帧
        """
        try:
            # 确保kernel_size为奇数
            if kernel_size % 2 == 0:
                kernel_size += 1
            
            return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        except Exception as e:
            logger.error(f"模糊效果处理失败: {e}")
            return frame
    
    @staticmethod
    def cartoon_effect(frame: np.ndarray) -> np.ndarray:
        """
        卡通效果
        
        Args:
            frame: 输入帧
        
        Returns:
            处理后的帧
        """
        try:
            # 双边滤波平滑图像
            bilateral = cv2.bilateralFilter(frame, 15, 80, 80)
            
            # 边缘检测
            gray = cv2.cvtColor(bilateral, cv2.COLOR_BGR2GRAY)
            gray_blur = cv2.medianBlur(gray, 5)
            edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                        cv2.THRESH_BINARY, 9, 9)
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            # 合并
            cartoon = cv2.bitwise_and(bilateral, edges)
            return cartoon
        except Exception as e:
            logger.error(f"卡通效果处理失败: {e}")
            return frame
    
    @staticmethod
    def sepia_effect(frame: np.ndarray) -> np.ndarray:
        """
        复古棕褐色效果
        
        Args:
            frame: 输入帧
        
        Returns:
            处理后的帧
        """
        try:
            # 棕褐色变换矩阵
            sepia_filter = np.array([
                [0.272, 0.534, 0.131],
                [0.349, 0.686, 0.168],
                [0.393, 0.769, 0.189]
            ])
            
            sepia_img = cv2.transform(frame, sepia_filter)
            # 确保值在0-255范围内
            sepia_img = np.clip(sepia_img, 0, 255)
            return sepia_img.astype(np.uint8)
        except Exception as e:
            logger.error(f"复古效果处理失败: {e}")
            return frame
    
    @staticmethod
    def negative_effect(frame: np.ndarray) -> np.ndarray:
        """
        负片效果
        
        Args:
            frame: 输入帧
        
        Returns:
            处理后的帧
        """
        try:
            return 255 - frame
        except Exception as e:
            logger.error(f"负片效果处理失败: {e}")
            return frame
    
    @staticmethod
    def brightness_contrast(frame: np.ndarray, brightness: int = 0, 
                           contrast: float = 1.0) -> np.ndarray:
        """
        亮度和对比度调整
        
        Args:
            frame: 输入帧
            brightness: 亮度调整值 (-100 到 100)
            contrast: 对比度调整值 (0.5 到 3.0)
        
        Returns:
            处理后的帧
        """
        try:
            # 限制参数范围
            brightness = max(-100, min(100, brightness))
            contrast = max(0.5, min(3.0, contrast))
            
            adjusted = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)
            return adjusted
        except Exception as e:
            logger.error(f"亮度对比度调整失败: {e}")
            return frame
    
    @staticmethod
    def color_filter(frame: np.ndarray, color_mask: Tuple[int, int, int] = (255, 255, 255)) -> np.ndarray:
        """
        颜色滤镜
        
        Args:
            frame: 输入帧
            color_mask: RGB颜色掩码
        
        Returns:
            处理后的帧
        """
        try:
            # 创建颜色掩码
            mask = np.ones_like(frame, dtype=np.float32)
            mask[:, :, 0] *= color_mask[2] / 255.0  # B
            mask[:, :, 1] *= color_mask[1] / 255.0  # G
            mask[:, :, 2] *= color_mask[0] / 255.0  # R
            
            filtered = frame.astype(np.float32) * mask
            return np.clip(filtered, 0, 255).astype(np.uint8)
        except Exception as e:
            logger.error(f"颜色滤镜处理失败: {e}")
            return frame
    
    @staticmethod
    def emboss_effect(frame: np.ndarray) -> np.ndarray:
        """
        浮雕效果
        
        Args:
            frame: 输入帧
        
        Returns:
            处理后的帧
        """
        try:
            # 浮雕核
            kernel = np.array([[-2, -1, 0],
                              [-1,  1, 1],
                              [ 0,  1, 2]])
            
            embossed = cv2.filter2D(frame, -1, kernel)
            # 调整亮度
            embossed = cv2.convertScaleAbs(embossed, alpha=1, beta=128)
            return embossed
        except Exception as e:
            logger.error(f"浮雕效果处理失败: {e}")
            return frame
    
    @staticmethod
    def motion_blur(frame: np.ndarray, size: int = 15, angle: float = 0) -> np.ndarray:
        """
        运动模糊效果
        
        Args:
            frame: 输入帧
            size: 模糊大小
            angle: 模糊角度（度）
        
        Returns:
            处理后的帧
        """
        try:
            # 创建运动模糊核
            kernel = np.zeros((size, size))
            kernel[int((size-1)/2), :] = np.ones(size)
            kernel = kernel / size
            
            # 旋转核
            if angle != 0:
                center = (size // 2, size // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                kernel = cv2.warpAffine(kernel, rotation_matrix, (size, size))
            
            blurred = cv2.filter2D(frame, -1, kernel)
            return blurred
        except Exception as e:
            logger.error(f"运动模糊处理失败: {e}")
            return frame

class FilterChain:
    """滤镜链，支持多个滤镜的组合应用"""
    
    def __init__(self):
        self.filters = []
    
    def add_filter(self, filter_func: Callable, **kwargs):
        """
        添加滤镜到链中
        
        Args:
            filter_func: 滤镜函数
            **kwargs: 滤镜参数
        """
        self.filters.append((filter_func, kwargs))
        return self
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """
        应用滤镜链
        
        Args:
            frame: 输入帧
        
        Returns:
            处理后的帧
        """
        result = frame.copy()
        
        for filter_func, kwargs in self.filters:
            try:
                result = filter_func(result, **kwargs)
            except Exception as e:
                logger.error(f"应用滤镜 {filter_func.__name__} 失败: {e}")
                continue
        
        return result
    
    def clear(self):
        """清空滤镜链"""
        self.filters.clear()
    
    def remove_last(self):
        """移除最后一个滤镜"""
        if self.filters:
            self.filters.pop()

class TextOverlay:
    """文本叠加工具"""
    
    @staticmethod
    def add_text(frame: np.ndarray, text: str, position: Tuple[int, int] = (10, 30),
                font_scale: float = 1.0, color: Tuple[int, int, int] = (255, 255, 255),
                thickness: int = 2, background: bool = True) -> np.ndarray:
        """
        在帧上添加文本
        
        Args:
            frame: 输入帧
            text: 要添加的文本
            position: 文本位置 (x, y)
            font_scale: 字体大小
            color: 文本颜色 (B, G, R)
            thickness: 文本粗细
            background: 是否添加背景
        
        Returns:
            处理后的帧
        """
        try:
            result = frame.copy()
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            # 获取文本大小
            (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            
            # 添加背景
            if background:
                cv2.rectangle(result, 
                            (position[0] - 5, position[1] - text_height - 5),
                            (position[0] + text_width + 5, position[1] + baseline + 5),
                            (0, 0, 0), -1)
            
            # 添加文本
            cv2.putText(result, text, position, font, font_scale, color, thickness)
            
            return result
        except Exception as e:
            logger.error(f"添加文本失败: {e}")
            return frame
    
    @staticmethod
    def add_timestamp(frame: np.ndarray, position: Tuple[int, int] = None,
                     format_str: str = "%Y-%m-%d %H:%M:%S") -> np.ndarray:
        """
        添加时间戳
        
        Args:
            frame: 输入帧
            position: 时间戳位置，None为右下角
            format_str: 时间格式字符串
        
        Returns:
            处理后的帧
        """
        try:
            import datetime
            
            timestamp = datetime.datetime.now().strftime(format_str)
            
            if position is None:
                # 默认位置：右下角
                height, width = frame.shape[:2]
                position = (width - 200, height - 20)
            
            return TextOverlay.add_text(frame, timestamp, position, 
                                      font_scale=0.6, color=(255, 255, 255))
        except Exception as e:
            logger.error(f"添加时间戳失败: {e}")
            return frame
    
    @staticmethod
    def add_frame_info(frame: np.ndarray, frame_count: int, fps: float = 0.0,
                      position: Tuple[int, int] = (10, 30)) -> np.ndarray:
        """
        添加帧信息
        
        Args:
            frame: 输入帧
            frame_count: 帧计数
            fps: 当前FPS
            position: 信息位置
        
        Returns:
            处理后的帧
        """
        try:
            info_text = f"Frame: {frame_count}"
            if fps > 0:
                info_text += f" | FPS: {fps:.1f}"
            
            return TextOverlay.add_text(frame, info_text, position,
                                      font_scale=0.7, color=(0, 255, 0))
        except Exception as e:
            logger.error(f"添加帧信息失败: {e}")
            return frame

# 预定义滤镜组合
def create_vintage_filter() -> FilterChain:
    """创建复古风格滤镜链"""
    chain = FilterChain()
    chain.add_filter(ImageFilters.sepia_effect)
    chain.add_filter(ImageFilters.brightness_contrast, brightness=-10, contrast=1.2)
    return chain

def create_artistic_filter() -> FilterChain:
    """创建艺术风格滤镜链"""
    chain = FilterChain()
    chain.add_filter(ImageFilters.cartoon_effect)
    chain.add_filter(ImageFilters.color_filter, color_mask=(255, 200, 150))
    return chain

def create_dramatic_filter() -> FilterChain:
    """创建戏剧化风格滤镜链"""
    chain = FilterChain()
    chain.add_filter(ImageFilters.brightness_contrast, brightness=10, contrast=1.5)
    chain.add_filter(ImageFilters.edge_detection, low_threshold=100, high_threshold=200)
    return chain