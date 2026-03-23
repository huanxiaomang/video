#!/bin/bash

# 启动摄像头采集端脚本

echo "📹 启动摄像头采集端..."

# 进入摄像头客户端目录
cd "$(dirname "$0")/camera-client"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "📝 创建配置文件..."
    cp .env.example .env
fi

# 启动摄像头采集
echo "✅ 摄像头采集启动中..."
echo "📡 连接服务器: http://localhost:8000"
echo ""
python main.py

