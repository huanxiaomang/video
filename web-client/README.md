# Web监控客户端 (Web Client)

## 功能说明

基于Vue3 + TypeScript的Web监控客户端，提供实时视频监控、设备管理、录像回放等功能。

## 技术栈

- **Vue 3**: 渐进式JavaScript框架
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **Pinia**: 状态管理
- **Vue Router**: 路由管理
- **Element Plus**: UI组件库
- **Axios**: HTTP客户端

## 安装依赖

```bash
npm install
# 或
yarn install
# 或
pnpm install
```

## 开发运行

```bash
npm run dev
```

访问: http://localhost:5173

## 构建生产版本

```bash
npm run build
```

## 主要功能模块

### 1. 用户认证
- 登录/登出
- JWT Token管理
- 路由守卫

### 2. 实时监控
- 多分屏显示（1/4/9/16分屏）
- 设备选择
- 实时视频播放
- 全屏播放

### 3. 设备管理
- 设备列表查看
- 设备状态监控
- 设备筛选
- 设备删除

### 4. 录像回放
- 录像搜索
- 录像播放
- 时间范围筛选

### 5. 系统设置
- 基本设置
- 视频参数配置
- 用户信息查看

## 目录结构

```
src/
├── api/              # API接口
│   ├── request.ts    # Axios封装
│   ├── auth.ts       # 认证API
│   └── device.ts     # 设备API
├── components/       # 组件
│   └── VideoPlayer.vue
├── stores/           # Pinia状态管理
│   ├── user.ts       # 用户状态
│   └── device.ts     # 设备状态
├── router/           # 路由配置
│   └── index.ts
├── types/            # TypeScript类型定义
│   └── index.ts
├── views/            # 页面组件
│   ├── Login.vue
│   ├── Layout.vue
│   ├── LiveMonitor.vue
│   ├── DeviceManagement.vue
│   ├── PlaybackPage.vue
│   └── Settings.vue
├── App.vue           # 根组件
└── main.ts           # 入口文件
```

## 默认登录账号

- 用户名: admin
- 密码: admin123

## 配置说明

### API代理配置

在 `vite.config.ts` 中配置了API代理：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

## 注意事项

1. 确保后端服务器已启动
2. 视频播放需要浏览器支持相应的视频格式
3. WebRTC播放需要HTTPS或localhost环境

