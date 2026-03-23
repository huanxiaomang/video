# 传输服务器 (Server)

## 功能说明

传输服务器负责管理设备、用户认证、视频流转发和录像管理。

## 主要模块

- **main.py**: FastAPI应用主入口
- **config.py**: 配置管理
- **models.py**: 数据库模型定义
- **database.py**: 数据库连接和初始化
- **api_auth.py**: 用户认证API
- **api_devices.py**: 设备管理API

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

主要配置项：
- `HOST`: 服务器监听地址
- `PORT`: 服务器端口
- `DATABASE_URL`: 数据库连接URL
- `SECRET_KEY`: JWT密钥（生产环境必须修改）
- `RTSP_SERVER_HOST/PORT`: RTSP服务器地址
- `CORS_ORIGINS`: 允许的跨域源

## 运行

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 默认账号

- 用户名: admin
- 密码: admin123

## 数据库

使用SQLite数据库，首次运行会自动创建表和默认管理员账户。

## 主要API端点

### 认证
- POST `/api/auth/login` - 用户登录
- GET `/api/auth/me` - 获取当前用户信息
- POST `/api/auth/logout` - 用户登出

### 设备管理
- POST `/api/devices/register` - 设备注册
- POST `/api/devices/{device_id}/heartbeat` - 设备心跳
- GET `/api/devices` - 获取设备列表
- GET `/api/devices/{device_id}` - 获取设备详情
- DELETE `/api/devices/{device_id}` - 删除设备

