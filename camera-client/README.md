# 摄像头采集端 (Camera Client)

## 功能说明

摄像头采集端负责从本地摄像头采集视频，编码压缩后通过RTSP协议推流到服务器。

## 主要模块

- **camera_capture.py**: 摄像头采集模块，使用OpenCV读取摄像头数据
- **rtsp_streamer.py**: RTSP推流模块，使用FFmpeg进行H.264编码和RTSP推流
- **device_manager.py**: 设备管理模块，负责设备注册和心跳
- **main.py**: 主程序入口
- **config.py**: 配置文件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

编辑 `config.py` 文件，配置以下参数：

- `SERVER_URL`: 服务器地址
- `DEVICE_NAME`: 设备名称
- `DEVICE_TYPE`: 设备类型 (robot/fixed)
- `DEVICE_LOCATION`: 设备位置
- `CAMERA_ID`: 摄像头ID (0为默认摄像头)
- `RESOLUTION_WIDTH/HEIGHT`: 分辨率
- `FPS`: 帧率
- `BITRATE`: 码率

## 运行

```bash
python main.py
```

## 工作流程

1. 启动时向服务器注册设备
2. 开启心跳线程，定期向服务器发送心跳
3. 初始化摄像头采集
4. 初始化RTSP推流器
5. 循环读取摄像头帧并推流
6. 退出时注销设备并清理资源

## 注意事项

- 需要安装FFmpeg并确保在系统PATH中
- 确保摄像头权限已授予
- RTSP服务器需要提前配置好（如MediaMTX）

