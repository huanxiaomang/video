# MediaMTX 服务器 —— 新手入门学习资源

> 本文档整理了与本项目高度相关的 MediaMTX 学习资源
>
> 从"零基础"到"能看懂项目配置"，按学习阶段分级推荐

---

## 一、本项目中 MediaMTX 用了哪些功能？

在查找学习资源之前，先明确本项目用到了 MediaMTX 的哪些功能，这样你学习时**有的放矢**：

```yaml
# 本项目 mediamtx.yml 配置摘要：

# ✅ 功能1：WebRTC 推拉流（核心功能！）
webrtcAddress: :8889          # WHIP推流 + WHEP拉流 共用端口

# ✅ 功能2：RTSP 备用协议
rtspAddress: :8554            # 传统RTSP协议备用
rtspTransports: [tcp, udp]    # 支持TCP和UDP

# ✅ 功能3：自动录制
record: yes                   # 开启录制
recordFormat: fmp4            # 录像格式
recordDeleteAfter: 168h       # 7天后自动清理

# ✅ 功能4：动态路径
paths:
  all:                        # 任何设备ID都自动创建路径

# ⬜ 功能5：HLS/RTMP（配置了但项目主要没用）
hlsAddress: :8888
rtmpAddress: :1935
```

**你需要重点学习的 MediaMTX 功能**：

| 优先级 | 功能 | 为什么要学 |
|--------|------|-----------|
| ⭐⭐⭐ | WebRTC (WHIP/WHEP) | 项目核心！推流和拉流都靠它 |
| ⭐⭐⭐ | 路径管理 (paths) | 理解设备如何动态注册和访问 |
| ⭐⭐ | 录制功能 (record) | 项目自动录像用到了 |
| ⭐⭐ | RTSP 协议 | 备用方案，理解多协议支持 |
| ⭐ | HLS/RTMP | 了解即可，项目未主要使用 |

---

## 二、官方核心资源（必看！）

### 1. GitHub 仓库（最重要的资源）

| 资源 | 链接 | 说明 |
|------|------|------|
| **MediaMTX 官方仓库** | https://github.com/bluenviron/mediamtx | ⭐ 项目主页，README 就是最佳入门文档 |
| **官方 README（中文可翻译）** | https://github.com/bluenviron/mediamtx#readme | 包含安装、配置、所有协议说明 |
| **Releases 下载页** | https://github.com/bluenviron/mediamtx/releases | 下载对应系统的可执行文件 |
| **Issues 问题讨论** | https://github.com/bluenviron/mediamtx/issues | 遇到问题先搜这里 |
| **默认配置文件模板** | https://github.com/bluenviron/mediamtx/blob/main/mediamtx.yml | 完整配置项参考，每项都有注释 |

### 2. 官方 Wiki 文档

| 页面 | 链接 | 与本项目的关系 |
|------|------|---------------|
| **Wiki 首页** | https://github.com/bluenviron/mediamtx/wiki | 所有文档的入口 |

> **学习建议**：先看 GitHub README，再看 Wiki，最后对照本项目的 `mediamtx.yml` 配置文件理解每个参数。

---

## 三、与本项目高度相关的学习主题

### 主题1：WebRTC + WHIP/WHEP（最重要！）

| 资源 | 链接 | 说明 |
|------|------|------|
| **MediaMTX WebRTC 配置说明** | https://github.com/bluenviron/mediamtx#webrtc | 官方WebRTC配置文档 |
| **WHIP 推流说明** | https://github.com/bluenviron/mediamtx#publish-to-the-server | 如何用WHIP推流到MediaMTX |
| **WHEP 拉流说明** | https://github.com/bluenviron/mediamtx#read-from-the-server | 如何用WHEP从MediaMTX拉流 |
| **WHIP 协议标准** | https://datatracker.ietf.org/doc/draft-ietf-wish-whip/ | IETF官方WHIP协议草案 |
| **WHEP 协议标准** | https://datatracker.ietf.org/doc/draft-murillo-whep/ | IETF官方WHEP协议草案 |
| **掘金: MediaMTX+WebRTC实践** | https://juejin.cn/search?query=mediamtx%20webrtc | 中文实战文章 |
| **CSDN: MediaMTX WebRTC** | https://blog.csdn.net/search?q=mediamtx+webrtc | 中文技术博客 |

**本项目对应代码**：
```
推流端: camera-client/whip_streamer.py → POST http://IP:8889/{设备ID}/whip
拉流端: web-client/src/utils/whepClient.ts → POST http://IP:8889/{设备ID}/whep
```

### 主题2：录制功能（Record）

| 资源 | 链接 | 说明 |
|------|------|------|
| **官方录制配置** | https://github.com/bluenviron/mediamtx#recording | 录制功能的所有参数说明 |
| **CSDN: MediaMTX录制** | https://blog.csdn.net/search?q=mediamtx+%E5%BD%95%E5%88%B6 | 中文录制配置教程 |

**本项目配置**：
```yaml
record: yes
recordPath: ./server/recordings/%path/%Y-%m-%d_%H-%M-%S
recordFormat: fmp4            # fragmented MP4格式
recordPartDuration: 1h        # 每段1小时
recordSegmentDuration: 1h
recordDeleteAfter: 168h       # 7天自动清理
```

### 主题3：RTSP 协议支持

| 资源 | 链接 | 说明 |
|------|------|------|
| **官方 RTSP 说明** | https://github.com/bluenviron/mediamtx#rtsp | RTSP协议配置 |
| **知乎: RTSP协议入门** | https://www.zhihu.com/search?q=RTSP%E5%8D%8F%E8%AE%AE%E5%85%A5%E9%97%A8 | 理解RTSP基础概念 |

### 主题4：路径管理（Paths）

| 资源 | 链接 | 说明 |
|------|------|------|
| **官方路径配置** | https://github.com/bluenviron/mediamtx#path-configuration | 路径通配和权限配置 |

**本项目配置解释**：
```yaml
paths:
  all:        # "all" 是特殊关键字，匹配所有路径
              # 意味着任何设备ID（device-001, device-002...）
              # 都会自动创建路径，不需要提前配置
```

---

## 四、中文入门教程推荐

| 资源 | 链接 | 推荐理由 |
|------|------|---------|
| **CSDN: MediaMTX入门教程** | https://blog.csdn.net/search?q=mediamtx%E5%85%A5%E9%97%A8 | 中文入门，有步骤截图 |
| **掘金: MediaMTX使用指南** | https://juejin.cn/search?query=mediamtx%E6%95%99%E7%A8%8B | 掘金实战文章 |
| **知乎: 流媒体服务器对比** | https://www.zhihu.com/search?q=mediamtx%20%E6%B5%81%E5%AA%92%E4%BD%93 | 了解MediaMTX在流媒体中的定位 |
| **B站: MediaMTX教程** | https://search.bilibili.com/all?keyword=mediamtx | 视频教程，直观易懂 |
| **B站: 流媒体服务器搭建** | https://search.bilibili.com/all?keyword=%E6%B5%81%E5%AA%92%E4%BD%93%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%90%AD%E5%BB%BA | 包含MediaMTX相关内容 |
| **CSDN: MediaMTX配置详解** | https://blog.csdn.net/search?q=mediamtx+%E9%85%8D%E7%BD%AE | 配置文件逐项讲解 |

---

## 五、进阶学习资源

### 1. 流媒体基础知识（理解 MediaMTX 的前提）

| 资源 | 链接 | 说明 |
|------|------|------|
| **知乎: 什么是流媒体** | https://www.zhihu.com/search?q=%E4%BB%80%E4%B9%88%E6%98%AF%E6%B5%81%E5%AA%92%E4%BD%93 | 先理解"流媒体"的概念 |
| **知乎: RTSP vs RTMP vs HLS** | https://www.zhihu.com/search?q=RTSP+RTMP+HLS+%E5%8C%BA%E5%88%AB | 理解各种流媒体协议的区别 |
| **MDN: WebRTC API** | https://developer.mozilla.org/zh-CN/docs/Web/API/WebRTC_API | WebRTC 基础（MediaMTX 的核心协议） |
| **WebRTC For The Curious** | https://webrtcforthecurious.com/ | 免费电子书，深入理解 WebRTC |

### 2. MediaMTX 竞品对比（了解 MediaMTX 的定位）

| 流媒体服务器 | 链接 | 与 MediaMTX 对比 |
|-------------|------|-----------------|
| **SRS (Simple Realtime Server)** | https://github.com/ossrs/srs | 功能更丰富，但配置复杂 |
| **Janus Gateway** | https://github.com/meetecho/janus-gateway | 专注 WebRTC，插件化架构 |
| **Nginx-RTMP** | https://github.com/arut/nginx-rtmp-module | 传统方案，不支持 WebRTC |
| **GStreamer** | https://gstreamer.freedesktop.org/ | 底层框架，非开箱即用 |

> **为什么本项目选 MediaMTX？** 因为它：
> - ✅ 单个可执行文件，零依赖，开箱即用
> - ✅ 原生支持 WHIP/WHEP（WebRTC推拉流）
> - ✅ 同时支持 RTSP、RTMP、HLS 多协议
> - ✅ 自带录制功能
> - ✅ 配置超级简单（一个 YAML 文件搞定）

### 3. Docker 部署相关

| 资源 | 链接 | 说明 |
|------|------|------|
| **MediaMTX Docker镜像** | https://hub.docker.com/r/bluenviron/mediamtx | 官方Docker镜像 |
| **GitHub: Docker使用说明** | https://github.com/bluenviron/mediamtx#docker-image | 官方Docker部署文档 |

---

## 六、本项目 mediamtx.yml 逐行解读

下面对本项目的配置文件 `mediamtx.yml` 逐行讲解，帮你理解每个参数的含义：

```yaml
# === 基础设置 ===
logLevel: info                    # 日志级别：info（正常）、debug（调试）、warn（警告）
                                  # 新手建议用 info，排错时改 debug

# === RTSP 协议配置（传统监控协议，本项目备用） ===
rtspAddress: :8554                # RTSP 监听端口 8554（行业标准端口）
rtspTransports: [tcp, udp]        # 支持 TCP 和 UDP 两种传输方式
rtspEncryption: "no"              # 不加密（局域网内无需加密）
rtpAddress: :9000                 # RTP 数据端口
rtcpAddress: :9001                # RTCP 控制端口

# === WebRTC 配置（本项目核心！） ===
webrtcAddress: :8889              # ⭐ WebRTC 监听端口 8889
                                  # WHIP推流和WHEP拉流都用这个端口
                                  # 摄像头推流: POST http://IP:8889/{设备ID}/whip
                                  # 浏览器拉流: POST http://IP:8889/{设备ID}/whep
webrtcICEServers2: []             # ICE 服务器列表（空=不用外部STUN/TURN）
                                  # 局域网部署不需要，跨网络时需要配置

# === HLS 配置（备用，浏览器兼容方案） ===
hlsAddress: :8888                 # HLS 监听端口
hlsAlwaysRemux: no                # 不总是重新封装

# === RTMP 配置（备用，兼容 OBS 等工具） ===
rtmpAddress: :1935                # RTMP 标准端口

# === 路径配置（最关键！） ===
paths:
  all:                            # ⭐ "all" = 匹配所有路径
                                  # 意味着任何设备ID都能自动创建流
                                  # 例如推流到 /device-001/whip，device-001 路径自动创建

    # 录制设置
    record: yes                   # ⭐ 开启自动录制
    recordPath: ./server/recordings/%path/%Y-%m-%d_%H-%M-%S
                                  # 录像保存路径：
                                  # %path = 设备ID（如 device-001）
                                  # %Y-%m-%d_%H-%M-%S = 年-月-日_时-分-秒
                                  # 例如: ./server/recordings/device-001/2025-01-15_14-30-00
    recordFormat: fmp4            # 录像格式：fragmented MP4（边录边写，断电不丢数据）
    recordPartDuration: 1h        # 每个录像片段时长：1小时
    recordSegmentDuration: 1h     # 每个录像段时长：1小时
    recordDeleteAfter: 168h       # ⭐ 168小时 = 7天后自动删除旧录像
```

**核心要点总结**：

| 配置项 | 值 | 含义 |
|--------|-----|------|
| `webrtcAddress` | `:8889` | 推流拉流的统一入口 |
| `paths: all` | 通配所有路径 | 设备自动注册，无需提前配置 |
| `record: yes` | 开启录制 | 所有推流的视频自动保存 |
| `recordDeleteAfter` | `168h` | 7天自动清理，防止存储爆满 |

---

## 七、推荐学习路径

```
第1步：快速了解（30分钟）
├── 阅读本文档 第一章~第二章
├── 访问 MediaMTX GitHub 仓库，看 README 的前半部分
└── 目标：知道 MediaMTX 是什么、能做什么

第2步：理解项目配置（1小时）
├── 阅读本文档 第六章（逐行解读）
├── 打开项目中的 mediamtx.yml 对照学习
├── 重点理解：webrtcAddress、paths、record 三个配置
└── 目标：能解释项目为什么这样配置

第3步：理解协议关系（1小时）
├── 阅读本文档 第三章（与项目高度相关的学习主题）
├── 理解 WHIP 推流 和 WHEP 拉流 如何通过 MediaMTX 中转
├── 对照看 whip_streamer.py 和 whepClient.ts 代码
└── 目标：能画出完整的视频流转路径

第4步：扩展了解（选学，1小时）
├── 阅读本文档 第五章（进阶资源）
├── 了解 MediaMTX 与其他流媒体服务器的区别
├── 浏览 MediaMTX 的 GitHub Issues 看常见问题
└── 目标：能回答"为什么选 MediaMTX 而不是其他方案"
```

---

**文档版本**: v1.0
**最后更新**: 2025年
**适用读者**: 计算机新手小白、需要理解项目中 MediaMTX 作用的学生