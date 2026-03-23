#!/bin/bash

# 启动Web客户端脚本

echo "🌐 启动Web监控客户端..."

# 进入Web客户端目录
cd "$(dirname "$0")/web-client"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

# 启动开发服务器
echo "✅ Web客户端启动中..."
echo "📍 访问地址: http://localhost:5173"
echo "👤 默认账号: admin / admin123"
echo ""
npm run dev

