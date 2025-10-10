# aitoolkit-cam

[![PyPI version](https://img.shields.io/pypi/v/aitoolkit-cam.svg)](https://pypi.org/project/aitoolkit-cam/)
[![Python versions](https://img.shields.io/pypi/pyversions/aitoolkit-cam.svg)](https://pypi.org/project/aitoolkit-cam/)
[![License](https://img.shields.io/pypi/l/aitoolkit-cam.svg)](https://github.com/dianx12/aitoolkit-cam/blob/main/LICENSE)

极简Python摄像头库 - 专为ARM设备和Jupyter环境设计的高性能摄像头工具包。

## 🚀 特性

- **🎯 简单易用**: 三行代码即可启动摄像头流
- **🔧 MJPEG流修复**: v3.0版本完全解决视频流断流问题
- **🏢 多客户端支持**: 支持多用户同时访问摄像头流
- **📱 Jupyter优化**: 专为Jupyter notebook环境优化
- **🔄 ARM64优化**: 针对树莓派等ARM设备优化性能
- **⚡ FastAPI集成**: 内置Web服务器，一键启动视频流
- **🎨 实时图像处理**: 内置多种滤镜和图像处理功能

## 🛠️ 安装

```bash
pip install aitoolkit-cam
```

## 📖 快速开始

### 基本使用

```python
from aitoolkit_cam import Camera

# 启动摄像头
with Camera(source=0, max_frames=100) as cam:
    url = cam.start()
    print(f"视频流地址: {url}")

    # 处理每一帧
    for frame in cam:
        # 在这里添加你的图像处理代码
        processed_frame = your_processing_function(frame)
        cam.show(processed_frame)
```

### FastAPI Web服务

```python
from fastapi import FastAPI
from aitoolkit_cam import add_camera_routes

app = FastAPI()
add_camera_routes(app, prefix="/camera")

# 访问 http://localhost:8000/camera/stream 查看视频流
```

### Jupyter Notebook中使用

```python
import aitoolkit_cam

# 快速启动摄像头管理器
manager = aitoolkit_cam.camera_manager
print(f"摄像头状态: {manager.is_running}")

# 获取单帧图像
frame = manager.read_frame()
if frame is not None:
    print(f"成功获取帧: {frame.shape}")
```

## 🔧 高级功能

### 图像滤镜

```python
from aitoolkit_cam import Camera, ImageFilters

with Camera() as cam:
    filters = ImageFilters()
    url = cam.start()

    for frame in cam:
        # 应用复古滤镜
        vintage_frame = filters.vintage(frame)
        cam.show(vintage_frame)
```

### 设备管理

```python
from aitoolkit_cam import list_available_cameras, get_optimal_camera

# 列出所有可用摄像头
cameras = list_available_cameras()
print(f"发现 {len(cameras)} 个摄像头设备")

# 自动选择最佳摄像头
best_camera = get_optimal_camera()
print(f"推荐使用摄像头: {best_camera}")
```

## 📋 版本历史

### v3.0.0 (2025-10-06)
- ✅ **重大修复**: 完全解决MJPEG视频流断流问题
- ✅ **多客户端支持**: 添加JPEG缓存机制，支持多用户同时访问
- ✅ **连接稳定性**: 改进错误处理和恢复机制
- ✅ **浏览器兼容性**: 添加Content-Length头，提高兼容性
- ✅ **性能优化**: 优化ARM设备上的性能表现

### v2.0.0
- 修复MJPEG流显示问题
- 改进多客户端支持

### v1.1.0
- 基础摄像头功能
- Jupyter环境集成

## 🔧 API文档

### Camera类

```python
Camera(source=0, width=640, height=480, fps=20, max_frames=None)
```

**参数:**
- `source`: 摄像头设备索引或路径
- `width`: 视频宽度 (默认: 640)
- `height`: 视频高度 (默认: 480)
- `fps`: 帧率 (默认: 20)
- `max_frames`: 最大帧数限制 (默认: None)

### FastAPI集成

```python
add_camera_routes(app, prefix="/camera")
```

**端点:**
- `GET /camera/stream` - MJPEG视频流
- `GET /camera/frame` - 单帧JPEG图像
- `GET /camera/info` - 摄像头信息

## 🎯 使用场景

1. **教育项目**: 简单易懂的API，适合编程教学
2. **IoT应用**: ARM设备上的视频监控
3. **Jupyter研究**: 数据科学和机器学习中的图像处理
4. **Web应用**: 快速集成视频流功能
5. **原型开发**: 快速搭建包含摄像头的应用原型

## 📞 技术支持

- **问题反馈**: [GitHub Issues](https://github.com/dianx12/aitoolkit-cam/issues)
- **源代码**: [GitHub Repository](https://github.com/dianx12/aitoolkit-cam)
- **作者**: Haitao Wang
- **邮箱**: dianx12@163.com

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 🏷️ 标签

`camera` `opencv` `video` `streaming` `web` `cv2` `jupyter` `notebook` `education` `arm64` `raspberry-pi` `real-time` `smart-stop` `mjpeg` `fastapi`