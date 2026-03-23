#!/bin/bash

# 启动服务器脚本

echo "🚀 启动视频传输服务器..."

# 进入服务器目录
cd "$(dirname "$0")/server"

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

# 初始化数据库（如果不存在）
if [ ! -f "video_system.db" ]; then
    echo "🗄️  初始化数据库..."
    python -c "from models import init_db; import asyncio; asyncio.run(init_db())"
fi

# 启动服务器
echo "✅ 服务器启动中..."
echo "📍 访问地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

