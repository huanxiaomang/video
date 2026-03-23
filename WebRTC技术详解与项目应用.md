# WebRTC 技术详解与项目应用

> 适合计算机新手小白的 WebRTC 入门指南
>
> 本文档将通俗易懂地讲解 WebRTC 是什么，以及它在本项目中的具体应用

---

## 目录

- [一、WebRTC 是什么？](#一webrtc-是什么)
- [二、WebRTC 的核心特点](#二webrtc-的核心特点)
- [三、WebRTC 在本项目中的应用](#三webrtc-在本项目中的应用)
- [四、WebRTC 的核心组件](#四webrtc-的核心组件)
- [五、WebRTC 工作原理](#五webrtc-工作原理)
- [六、项目中的 WebRTC 实现细节](#六项目中的-webrtc-实现细节)
- [七、WebRTC 相关知识点](#七webrtc-相关知识点)
- [八、学习资源与推荐文章](#八学习资源与推荐文章)

---

## 一、WebRTC 是什么？

### 1. 名词解释

**WebRTC** = **Web** **R**eal-**T**ime **C**ommunication

- **中文翻译**：网页实时通信技术
- **一句话概括**：让浏览器能够直接进行音视频通话和数据传输的技术
- **通俗理解**：就像微信视频通话、腾讯会议、Zoom 这些应用背后使用的核心技术

### 2. 生活中的类比

想象一下打电话的场景：

```
传统视频通话（如 Skype 早期）：
你 → 电话公司中转站 → 对方
     (所有数据都经过中转)
     延迟大、占用服务器资源

WebRTC 视频通话：
你 ←─────直接连接─────→ 对方
     (点对点直连，几乎无延迟)
     延迟小、不占用服务器带宽
```

**核心优势**：WebRTC 尽可能让两端**直接连接**，就像面对面说话一样快！

### 3. WebRTC 的诞生背景

- **2011年**：Google 开源 WebRTC 项目
- **目标**：让浏览器原生支持实时音视频通信，不需要安装任何插件
- **现状**：所有现代浏览器（Chrome、Firefox、Safari、Edge）都已内置支持

---

## 二、WebRTC 的核心特点

### 1. 超低延迟

| 技术方案 | 延迟时间 | 适用场景 |
|---------|---------|---------|
| **WebRTC** | **100-500ms** | 视频通话、实时监控、在线游戏 |
| RTMP | 2-5秒 | 直播推流 |
| HLS | 5-30秒 | 点播、非实时直播 |
| RTSP | 1-3秒 | 传统监控摄像头 |

**本项目需求**：巡检机器人需要实时监控，延迟必须 ≤1秒，所以选择 WebRTC！

### 2. 浏览器原生支持

```javascript
// 不需要安装任何插件，浏览器直接支持：
const pc = new RTCPeerConnection();  // 创建 WebRTC 连接
```

**对比**：
- ❌ RTSP 协议：浏览器不支持，需要安装 VLC 插件
- ✅ WebRTC：浏览器原生支持，打开网页就能看

### 3. 点对点传输（P2P）

```
传统方案（所有数据经过服务器）：
摄像头 → 服务器 → 浏览器
        (服务器压力大)

WebRTC 方案（尽可能直连）：
摄像头 ←─────直连─────→ 浏览器
        (服务器只负责建立连接)
```

**注意**：本项目因为需要录制和多人观看，所以使用 MediaMTX 服务器中转，但延迟依然很低。

### 4. 安全加密

- 所有 WebRTC 连接都是**强制加密**的（DTLS + SRTP）
- 数据传输过程中无法被窃听
- 类似 HTTPS 的安全级别

---

## 三、WebRTC 在本项目中的应用

### 1. 整体架构图

```
┌─────────────────┐                    ┌─────────────────┐                    ┌─────────────────┐
│  机器人摄像头端  │                    │  MediaMTX 服务器 │                    │   监控网页端     │
│                 │                    │                 │                    │                 │
│  ● OpenCV 采集  │   WebRTC 推流      │  ● 接收视频流   │   WebRTC 拉流      │  ● 浏览器播放   │
│  ● H.264 编码   │ ─────────────────► │  ● 录制存储     │ ◄───────────────── │  ● 实时显示     │
│  ● WHIP 协议    │                    │  ● 转发分发     │                    │  ● WHEP 协议    │
│                 │                    │  ● 端口 8889    │                    │                 │
└─────────────────┘                    └─────────────────┘                    └─────────────────┘
     Python 端                              流媒体中转站                           浏览器端
   (aiortc 库)                            (MediaMTX)                        (原生 WebRTC API)
```

### 2. WebRTC 在项目中的三个应用场景

| 应用场景 | 使用的协议 | WebRTC 的作用 | 对应文件 |
|---------|-----------|--------------|---------|
| **推流** | WHIP | 把摄像头画面实时推送到服务器 | `camera-client/whip_streamer.py` |
| **拉流** | WHEP | 从服务器获取视频在浏览器播放 | `web-client/src/utils/whepClient.ts` |
| **传输** | RTP/SRTP | 实际的视频数据传输通道 | WebRTC 底层自动处理 |

### 3. 为什么本项目选择 WebRTC？

**需求分析**：
- ✅ 延迟要求：≤1秒（实时监控）
- ✅ 播放端：浏览器网页（不能装插件）
- ✅ 多设备：支持多个机器人同时推流
- ✅ 录制：需要服务器端录制视频

**方案对比**：

| 方案 | 延迟 | 浏览器支持 | 录制 | 结论 |
|-----|------|-----------|------|------|
| RTSP | 1-3秒 | ❌ 需插件 | ✅ | ❌ 浏览器不支持 |
| HLS | 5-30秒 | ✅ | ✅ | ❌ 延迟太高 |
| **WebRTC** | **≤500ms** | **✅** | **✅** | **✅ 完美匹配** |

---

## 四、WebRTC 的核心组件详解

WebRTC 不是一个单一的技术，而是由多个组件协同工作的"技术套餐"。

### 1. 三大核心 API

```
┌─────────────────────────────────────────────────────────────┐
│                    WebRTC 技术栈                             │
│                                                             │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ RTCPeerConnection│  │ MediaStream  │  │ RTCDataChannel│  │
│  │                 │  │              │  │               │  │
│  │ 核心！负责建立  │  │ 音视频流对象  │  │ 传输任意数据  │  │
│  │ 点对点连接      │  │ 承载画面和声音│  │ 如文字、文件  │  │
│  │                 │  │              │  │               │  │
│  │ 本项目：推流和  │  │ 本项目：摄像头│  │ 本项目：未使用│  │
│  │ 拉流都用它      │  │ 画面的载体    │  │ (可扩展)     │  │
│  └─────────────────┘  └──────────────┘  └───────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    底层协议                              ││
│  │  SDP(参数协商) + ICE(网络穿透) + RTP(数据传输)        ││
│  │  + DTLS(加密) + SRTP(安全传输)                        ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 2. 各组件详细说明

#### （1）RTCPeerConnection —— 连接管理器

这是 WebRTC 最核心的对象，负责管理整个连接的生命周期。

**类比**：就像手机的"通话功能"，负责拨号、接听、挂断。

```javascript
// 浏览器端创建（本项目 whepClient.ts 中）
const pc = new RTCPeerConnection({
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
});
```

```python
# Python端创建（本项目 whip_streamer.py 中）
from aiortc import RTCPeerConnection
pc = RTCPeerConnection()
```

**在本项目中的作用**：
- 推流端（Python）：创建连接 → 添加视频轨道 → 发送画面
- 拉流端（浏览器）：创建连接 → 接收视频轨道 → 播放画面

#### （2）MediaStream —— 媒体流

承载音频和视频数据的"容器"。

**类比**：就像水管里的水流，MediaStream 就是那根"水管"，里面流的是视频画面。

```
一个 MediaStream 可以包含多个轨道（Track）：
┌──────────────────────────┐
│      MediaStream         │
│  ┌────────────────────┐  │
│  │  VideoTrack (视频)  │  │  ← 摄像头画面
│  └────────────────────┘  │
│  ┌────────────────────┐  │
│  │  AudioTrack (音频)  │  │  ← 麦克风声音（本项目未使用）
│  └────────────────────┘  │
└──────────────────────────┘
```

**在本项目中**：
- 推流端：`CameraVideoTrack` 类产生视频帧 → 封装成 MediaStream → 通过 WebRTC 发送
- 拉流端：`ontrack` 事件接收 MediaStream → 设置到 `<video>` 标签播放

#### （3）SDP（Session Description Protocol）—— 参数协商

SDP 是一份"能力清单"，告诉对方"我支持什么"。

**类比**：就像两个人见面先交换名片，SDP 就是 WebRTC 的"名片"。

```
SDP 内容示例（简化版）：

v=0                              ← 协议版本号
o=- 0 0 IN IP4 127.0.0.1        ← 发起者信息
s=-                              ← 会话名称
t=0 0                            ← 时间（0表示永久）
m=video 9 UDP/TLS/RTP/SAVPF 96  ← 我要传视频，用RTP协议
a=rtpmap:96 H264/90000           ← 视频编码用H.264
a=sendonly                       ← 我只发送（推流端）
                                    或 a=recvonly（拉流端只接收）
```

**Offer/Answer 模型**：

```
推流端/拉流端                          服务器
     │                                  │
     │  ① 发送 Offer SDP               │
     │  "我支持H.264, 720P, 30fps"     │
     ├─────────────────────────────────►│
     │                                  │
     │  ② 返回 Answer SDP              │
     │  "好的，我也支持，开始吧"        │
     │◄─────────────────────────────────┤
     │                                  │
     │  ③ 连接建立，开始传输            │
     │◄════════════════════════════════►│
```

#### （4）ICE（Interactive Connectivity Establishment）—— 网络穿透

ICE 负责在复杂网络环境中找到两端之间的最佳通信路径。

**为什么需要 ICE？**

```
现实中的网络很复杂：

摄像头 ──► [防火墙] ──► [路由器NAT] ──► 互联网 ──► [路由器NAT] ──► [防火墙] ──► 服务器

ICE 的工作就是穿过这些障碍，找到一条能通的路！
```

**ICE 的三种连接方式**：

| 方式 | 说明 | 速度 | 成功率 |
|------|------|------|--------|
| **直连** | 两端在同一局域网，直接连 | 最快 | 局域网内100% |
| **STUN穿透** | 通过STUN服务器获取公网IP，然后直连 | 快 | 约70-80% |
| **TURN中转** | 所有数据通过TURN服务器转发 | 较慢 | 接近100% |

**本项目中**：摄像头和服务器通常在同一局域网，走直连模式，速度最快。

```javascript
// 本项目 whepClient.ts 中配置了 STUN 服务器作为备用：
const pc = new RTCPeerConnection({
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
  // Google 提供的免费 STUN 服务器
});
```

#### （5）RTP/SRTP —— 实际数据传输

RTP = Real-time Transport Protocol（实时传输协议）

连接建立后，视频帧就通过 RTP 协议一帧一帧地传输。

```
一个 RTP 数据包的结构：

┌──────────┬──────────┬──────────┬───────────────────────┐
│ 版本(2B) │ 序列号    │ 时间戳    │     视频帧数据         │
│          │ (2字节)  │ (4字节)  │   (H.264编码后)        │
└──────────┴──────────┴──────────┴───────────────────────┘

- 序列号：保证包的顺序（第1个包、第2个包...）
- 时间戳：保证播放同步（这帧应该在什么时间显示）
- SRTP：在RTP基础上加了加密，防止被窃听
```

---

## 五、WebRTC 完整工作原理

### 1. 一次完整的 WebRTC 连接过程

用"打视频电话"来类比整个过程：

```
阶段一：准备阶段
┌──────────────────────────────────────────────────────────┐
│ 1. 创建 RTCPeerConnection（拿起电话）                     │
│ 2. 添加媒体轨道（打开摄像头/准备接收画面）                │
│ 3. 监听事件（准备好接听回调）                             │
└──────────────────────────────────────────────────────────┘
                          ↓
阶段二：信令交换（互相交换"名片"）
┌──────────────────────────────────────────────────────────┐
│ 4. 创建 Offer SDP（写好自己的能力清单）                   │
│ 5. 通过 HTTP POST 发送 Offer（把名片递给对方）            │
│ 6. 收到 Answer SDP（对方回复了他的能力清单）              │
│ 7. setRemoteDescription（记住对方的参数）                 │
└──────────────────────────────────────────────────────────┘
                          ↓
阶段三：网络协商（找到最佳通信路径）
┌──────────────────────────────────────────────────────────┐
│ 8. ICE 候选收集（列出所有可能的网络路径）                  │
│ 9. ICE 候选交换（双方交换网络路径信息）                    │
│ 10. 连通性检查（测试哪条路径最快）                        │
│ 11. 选择最佳路径（确定最终通信通道）                      │
└──────────────────────────────────────────────────────────┘
                          ↓
阶段四：媒体传输（开始传视频！）
┌──────────────────────────────────────────────────────────┐
│ 12. DTLS 握手（建立加密通道）                             │
│ 13. SRTP 传输（加密传输视频帧）                           │
│ 14. 持续传输，直到连接关闭                                │
└──────────────────────────────────────────────────────────┘
```

### 2. 本项目中的两种 WebRTC 使用方式

```
方式一：WHIP 推流（摄像头 → 服务器）

  Python 端                    MediaMTX
  (aiortc)                    (8889端口)
     │                            │
     │ createOffer()              │
     │ POST /device-001/whip     │
     ├───────────────────────────►│
     │                            │
     │ Answer SDP                 │
     │◄───────────────────────────┤
     │                            │
     │ ═══ 视频帧(sendonly) ═══► │
     │                            │


方式二：WHEP 拉流（浏览器 ← 服务器）

  浏览器端                     MediaMTX
  (原生API)                   (8889端口)
     │                            │
     │ createOffer()              │
     │ POST /device-001/whep     │
     ├───────────────────────────►│
     │                            │
     │ Answer SDP                 │
     │◄───────────────────────────┤
     │                            │
     │ ◄═══ 视频帧(recvonly) ═══ │
     │                            │
```

### 3. 连接状态变化

WebRTC 连接有明确的生命周期状态：

```
new → connecting → connected → disconnected → closed
                      ↑
                 正常工作状态
                 视频在这里传输
```

**本项目的断线重连机制**：

```typescript
// whepClient.ts 中的连接状态监听
pc.onconnectionstatechange = () => {
  if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected') {
    // 连接断开了，自动重新连接！
    this.restart()  // 重新走一遍 WHEP 握手流程
  }
}
```

---

## 六、项目中的 WebRTC 实现细节

### 1. 推流端实现（Python + aiortc）

**文件位置**：`camera-client/whip_streamer.py`

```python
# 第1步：采集画面
class CameraVideoTrack(VideoStreamTrack):
    async def recv(self):
        ret, frame = self.cap.read()              # OpenCV 读取一帧
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 颜色转换
        video_frame = VideoFrame.from_ndarray(frame)     # 转为WebRTC帧
        return video_frame

# 第2步：建立 WebRTC 连接并推流
class WHIPStreamer:
    async def start(self):
        self.pc = RTCPeerConnection()             # 创建连接
        self.pc.addTrack(self.video_track)        # 添加视频轨道

        offer = await self.pc.createOffer()       # 创建 Offer
        await self.pc.setLocalDescription(offer)  # 设置本地描述

        # 通过 HTTP POST 发送到 WHIP 端点
        response = await session.post(
            "http://服务器:8889/device-001/whip",
            data=offer.sdp,
            headers={"Content-Type": "application/sdp"}
        )

        answer_sdp = await response.text()        # 收到 Answer
        await self.pc.setRemoteDescription(       # 设置远程描述
            RTCSessionDescription(sdp=answer_sdp, type="answer")
        )
        # 连接建立完成，视频自动推送！
```

**关键参数**（`camera-client/config.py`）：

```python
CAMERA_ID = 0          # 摄像头编号
FRAME_WIDTH = 1280     # 宽度 1280 像素
FRAME_HEIGHT = 720     # 高度 720 像素
FPS = 25               # 每秒 25 帧
VIDEO_BITRATE = 2000   # 码率 2000kbps
```

### 2. 拉流端实现（TypeScript + 浏览器原生 API）

**文件位置**：`web-client/src/utils/whepClient.ts`

```typescript
const pc = new RTCPeerConnection({
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
})

pc.ontrack = (event) => {
  videoElement.srcObject = event.streams[0]  // 视频流接到<video>标签
}

pc.addTransceiver('video', { direction: 'recvonly' })  // 只接收

const offer = await pc.createOffer()
await pc.setLocalDescription(offer)

const response = await fetch('http://服务器:8889/device-001/whep', {
  method: 'POST',
  headers: { 'Content-Type': 'application/sdp' },
  body: offer.sdp
})

const answerSdp = await response.text()
await pc.setRemoteDescription({ type: 'answer', sdp: answerSdp })
// 视频自动开始播放！
```

### 3. 播放组件（Vue3）

**文件位置**：`web-client/src/components/VideoPlayer.vue`

```typescript
import { WebRTCPlayer } from '@eyevinn/webrtc-player'

const whepUrl = `${config.webrtcBaseUrl}/${deviceId}/whep`
// 例如：http://192.168.1.100:8889/device-001/whep

player = new WebRTCPlayer({
  video: videoElement.value,
  type: 'whep',
})
await player.load(new URL(whepUrl))
```

### 4. 服务器配置（MediaMTX）

**文件位置**：`mediamtx.yml`

```yaml
webrtcAddress: :8889      # WHIP/WHEP 共用端口

paths:
  all:                    # 匹配所有设备路径
    record: yes           # 自动录制
    recordPath: ./server/recordings/%path/%Y-%m-%d_%H-%M-%S
    recordFormat: fmp4
```

### 5. WebRTC 在项目各文件中的使用汇总

| 文件 | WebRTC 相关功能 | 使用的 API/库 |
|------|----------------|--------------|
| `whip_streamer.py` | 创建连接、添加轨道、发Offer、收Answer | aiortc: `RTCPeerConnection` |
| `whepClient.ts` | 创建连接、收轨道、发Offer、收Answer | 浏览器原生: `RTCPeerConnection` |
| `VideoPlayer.vue` | 构建WHEP地址、播放视频 | `@eyevinn/webrtc-player` |
| `mediamtx.yml` | WebRTC端口配置、路径管理 | MediaMTX 服务器 |
| `config.py` | 视频参数（分辨率、帧率、码率） | OpenCV 配置 |
| `config/index.ts` | WebRTC服务器地址配置 | 前端配置 |

---

## 七、WebRTC 相关知识点汇总

### 1. 核心协议知识点

| 知识点 | 全称 | 通俗解释 | 在项目中的作用 |
|--------|------|---------|---------------|
| **WebRTC** | Web Real-Time Communication | 网页实时通信技术 | 整个视频传输的底层技术 |
| **SDP** | Session Description Protocol | 会话描述协议（"能力名片"） | 描述视频编码、分辨率等参数 |
| **ICE** | Interactive Connectivity Establishment | 网络路径协商 | 找到摄像头和服务器之间的最佳网络路径 |
| **STUN** | Session Traversal Utilities for NAT | NAT穿透辅助服务器 | 帮助获取公网IP地址 |
| **TURN** | Traversal Using Relays around NAT | NAT中转服务器 | 直连失败时的备用中转方案 |
| **RTP** | Real-time Transport Protocol | 实时传输协议 | 实际传输视频帧数据 |
| **SRTP** | Secure RTP | 加密的RTP | 加密传输，防止窃听 |
| **DTLS** | Datagram Transport Layer Security | 数据报传输层安全 | WebRTC的加密握手协议 |

### 2. 应用层协议知识点

| 知识点 | 全称 | 通俗解释 | 在项目中的作用 |
|--------|------|---------|---------------|
| **WHIP** | WebRTC-HTTP Ingestion Protocol | HTTP推流协议 | 摄像头通过HTTP发起WebRTC推流 |
| **WHEP** | WebRTC-HTTP Egress Protocol | HTTP拉流协议 | 浏览器通过HTTP发起WebRTC拉流 |
| **RTSP** | Real Time Streaming Protocol | 实时流传输协议 | 项目中的备用推流方案 |
| **HLS** | HTTP Live Streaming | HTTP直播流 | 对比方案（延迟太高未采用） |

### 3. 视频编码知识点

| 知识点 | 说明 | 项目中的值 |
|--------|------|-----------|
| **H.264** | 最常用的视频压缩编码标准 | 推流端编码格式 |
| **分辨率** | 画面像素大小 | 1280×720（720P） |
| **帧率(FPS)** | 每秒画面帧数 | 25fps |
| **码率(Bitrate)** | 每秒传输数据量 | 2000kbps |
| **I帧** | 关键帧，完整画面 | 视频流中周期性出现 |
| **P帧** | 预测帧，只记录变化部分 | 减少数据量 |

### 4. 开发工具知识点

| 知识点 | 说明 | 在项目中的作用 |
|--------|------|---------------|
| **aiortc** | Python的WebRTC库 | 推流端创建WebRTC连接 |
| **OpenCV** | 计算机视觉库 | 读取摄像头画面 |
| **MediaMTX** | 开源流媒体服务器 | 视频流中转站 |
| **@eyevinn/webrtc-player** | 前端WebRTC播放器库 | 封装WHEP拉流播放 |
| **RTCPeerConnection** | 浏览器原生WebRTC API | 拉流端建立连接 |
| **Fetch API** | 浏览器HTTP请求接口 | 发送WHEP的HTTP请求 |

### 5. WebRTC 核心概念关系图

```
                        WebRTC 技术体系
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
     信令层(Signaling)   连接层(Connection)  传输层(Transport)
          │                  │                  │
     ┌────┴────┐       ┌────┴────┐       ┌────┴────┐
     │  SDP    │       │  ICE    │       │  RTP    │
     │(参数协商)│       │(路径协商)│       │(数据传输)│
     └────┬────┘       └────┬────┘       └────┬────┘
          │                  │                  │
     Offer/Answer      STUN/TURN           SRTP加密
     (提议/应答)       (穿透/中转)         (安全传输)
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    本项目通过 WHIP/WHEP
                    用 HTTP POST 完成信令交换
```

---

## 八、学习资源与推荐文章

### 1. 官方权威资源

| 资源 | 链接 | 推荐理由 |
|------|------|---------|
| **WebRTC 官网** | https://webrtc.org/ | 官方网站，最权威的入口 |
| **MDN WebRTC 中文教程** | https://developer.mozilla.org/zh-CN/docs/Web/API/WebRTC_API | Mozilla出品，中文友好，适合入门 |
| **WebRTC 规范(W3C)** | https://www.w3.org/TR/webrtc/ | W3C官方标准文档 |
| **WHIP 标准草案** | https://datatracker.ietf.org/doc/draft-ietf-wish-whip/ | IETF官方WHIP协议定义 |
| **WHEP 标准草案** | https://datatracker.ietf.org/doc/draft-murillo-whep/ | IETF官方WHEP协议定义 |

### 2. 中文入门教程（强烈推荐新手）

| 资源 | 链接 | 推荐理由 |
|------|------|---------|
| **知乎: WebRTC是什么** | https://www.zhihu.com/question/22301898 | 高赞回答，通俗易懂 |
| **知乎: WebRTC入门总结** | https://zhuanlan.zhihu.com/p/86751078 | 系统性入门文章 |
| **掘金: WebRTC从入门到实践** | https://juejin.cn/search?query=WebRTC%E5%85%A5%E9%97%A8 | 掘金社区实战文章 |
| **CSDN: WebRTC详解** | https://blog.csdn.net/search?q=WebRTC%E8%AF%A6%E8%A7%A3 | CSDN技术博客 |
| **B站: WebRTC视频教程** | https://search.bilibili.com/all?keyword=WebRTC%E6%95%99%E7%A8%8B | 视频教程，看着学更直观 |

### 3. 英文深入资源

| 资源 | 链接 | 推荐理由 |
|------|------|---------|
| **WebRTC For The Curious** | https://webrtcforthecurious.com/ | 免费电子书，深入浅出讲原理 |
| **WebRTC Samples** | https://webrtc.github.io/samples/ | 官方代码示例，可在线运行 |
| **High Performance Browser Networking - WebRTC** | https://hpbn.co/webrtc/ | 经典书籍的WebRTC章节 |

### 4. 本项目相关技术库文档

| 库 | 链接 | 用途 |
|----|------|------|
| **aiortc** | https://github.com/aiortc/aiortc | Python WebRTC库（推流端） |
| **aiortc 文档** | https://aiortc.readthedocs.io/ | aiortc API文档 |
| **MediaMTX** | https://github.com/bluenviron/mediamtx | 流媒体服务器 |
| **MediaMTX Wiki** | https://github.com/bluenviron/mediamtx/wiki | 服务器配置文档 |
| **@eyevinn/webrtc-player** | https://github.com/Eyevinn/webrtc-player | 前端WHEP播放器 |
| **OpenCV Python** | https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html | 摄像头采集库 |

### 5. 推荐学习路径

```
第1天：了解 WebRTC 是什么（2小时）
├─ 阅读本文档 第一章~第二章
├─ 看B站 "WebRTC是什么" 入门视频
├─ 浏览 WebRTC 官网 webrtc.org
└─ 目标：能用自己的话说出 WebRTC 是什么

第2天：理解核心组件（2小时）
├─ 阅读本文档 第四章
├─ 阅读 MDN WebRTC 中文教程
├─ 重点理解：RTCPeerConnection、SDP、ICE
└─ 目标：能画出 WebRTC 连接建立的流程图

第3天：理解项目应用（2小时）
├─ 阅读本文档 第三章、第五章、第六章
├─ 对照文档看项目源码
├─ 重点看 whip_streamer.py 和 whepClient.ts
└─ 目标：能说清楚项目中 WebRTC 用在哪里

第4天：扩展学习（2小时）
├─ 阅读 WebRTC For The Curious 电子书
├─ 浏览 WebRTC Samples 在线示例
├─ 阅读本文档 第七章 知识点汇总
└─ 目标：能回答关于 WebRTC 的常见问题
```

---

**文档版本**: v1.0
**最后更新**: 2025年
**适用读者**: 计算机新手小白、需要了解 WebRTC 在项目中应用的学生