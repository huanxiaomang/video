"""配置文件"""
import os
from dotenv import load_dotenv

load_dotenv()

# 服务器配置
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:8000')

# 设备配置
DEVICE_NAME = os.getenv('DEVICE_NAME', 'Camera-001')
DEVICE_TYPE = os.getenv('DEVICE_TYPE', 'robot')  # robot 或 fixed
DEVICE_LOCATION = os.getenv('DEVICE_LOCATION', '1号机组')

# 摄像头配置
CAMERA_ID = int(os.getenv('CAMERA_ID', '0'))  # 0表示默认摄像头
RESOLUTION_WIDTH = int(os.getenv('RESOLUTION_WIDTH', '1280'))
RESOLUTION_HEIGHT = int(os.getenv('RESOLUTION_HEIGHT', '720'))
FPS = int(os.getenv('FPS', '25'))

# 编码配置
VIDEO_CODEC = 'libx264'
BITRATE = int(os.getenv('BITRATE', '2000'))  # kbps
PRESET = 'ultrafast'
TUNE = 'zerolatency'

# RTSP配置
RTSP_SERVER = os.getenv('RTSP_SERVER', 'localhost')
RTSP_PORT = int(os.getenv('RTSP_PORT', '8554'))

# 心跳配置
HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', '10'))  # 秒

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

