# Linux 新手部署完整教程

本教程将手把手教你如何在一台全新安装的 Linux 系统上从零开始部署本视频传输系统。

## 目录

- [系统要求](#系统要求)
- [第一步：Linux 基础配置](#第一步linux-基础配置)
- [第二步：安装 Python 环境](#第二步安装-python-环境)
- [第三步：安装 Node.js 环境](#第三步安装-nodejs-环境)
- [第四步：安装 FFmpeg](#第四步安装-ffmpeg)
- [第五步：安装 Git 并克隆代码](#第五步安装-git-并克隆代码)
- [第六步：配置并启动后端服务](#第六步配置并启动后端服务)
- [第七步：配置并启动前端服务](#第七步配置并启动前端服务)
- [第八步：配置并启动摄像头客户端](#第八步配置并启动摄像头客户端)
- [第九步：启动 MediaMTX 流媒体服务器](#第九步启动-mediamtx-流媒体服务器)
- [第十步：访问系统验证](#第十步访问系统验证)
- [一键启动脚本](#一键启动脚本)
- [开机自启配置](#开机自启配置)
- [常见问题解决](#常见问题解决)

---

## 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Ubuntu 20.04+ / Debian 11+ / CentOS 8+ |
| CPU | 2 核及以上 |
| 内存 | 至少 4GB RAM |
| 硬盘 | 至少 20GB 可用空间 |
| 网络 | 可正常访问互联网 |
| Python | 3.9+ |
| Node.js | 18+ |
| FFmpeg | 4.4+ |

> 本教程以 **Ubuntu 22.04 LTS** 为例，CentOS/Debian 用户命令略有差异，差异处会单独说明。

---

## 第一步：Linux 基础配置

### 1.1 更新系统软件包

打开终端（Terminal），执行以下命令：

```bash
# 更新软件包索引
sudo apt update

# 升级所有已安装的软件包
sudo apt upgrade -y
```

> CentOS 用户使用：`sudo dnf update -y`

### 1.2 安装基础依赖工具

```bash
sudo apt install -y curl wget vim git build-essential software-properties-common
```

各工具用途说明：
- `curl` / `wget`：网络下载工具
- `vim`：命令行文本编辑器
- `git`：版本控制与代码克隆
- `build-essential`：C/C++ 编译工具链（安装某些 Python 包时需要）
- `software-properties-common`：管理第三方软件源

### 1.3 配置服务器时区（建议）

```bash
# 查看当前时区
timedatectl

# 设置为上海时区
sudo timedatectl set-timezone Asia/Shanghai

# 验证
date
```

### 1.4 开放防火墙端口（如启用了 ufw）

```bash
# 查看防火墙状态
sudo ufw status

# 开放各服务端口
sudo ufw allow 8000/tcp    # 后端 FastAPI
sudo ufw allow 5173/tcp    # 前端 Vite 开发服务器
sudo ufw allow 8554/tcp    # MediaMTX RTSP
sudo ufw allow 8889/tcp    # MediaMTX WebRTC HTTP

# 重载防火墙规则
sudo ufw reload
```

---

## 第二步：安装 Python 环境

### 2.1 检查系统自带 Python 版本

```bash
python3 --version
```

Ubuntu 22.04 默认自带 Python 3.10，满足 3.9 的要求，可跳过升级步骤。

### 2.2 安装 Python 3、pip 和 venv

```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev

# 验证
python3 --version   # 应显示 3.9+
pip3 --version
```

### 2.3 升级 pip 到最新版

```bash
python3 -m pip install --upgrade pip
```

### 2.4 （可选）配置 pip 国内镜像加速

```bash
# 永久设置为清华镜像源
pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 第三步：安装 Node.js 环境

> 不要直接 `apt install nodejs`，系统源中的版本通常过旧（v12），请按以下方式安装 v18。

### 3.1 通过 NodeSource 安装 Node.js 18

```bash
# 下载并执行官方安装脚本
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# 安装 Node.js
sudo apt install -y nodejs

# 验证
node --version    # 应显示 v18.x.x
npm --version     # 应显示 9.x.x 或 10.x.x
```

### 3.2 （可选）配置 npm 国内镜像加速

```bash
npm config set registry https://registry.npmmirror.com

# 验证配置
npm config get registry
```

---

## 第四步：安装 FFmpeg

FFmpeg 负责视频的编解码处理，是本项目的核心依赖之一。

```bash
# Ubuntu/Debian
sudo apt install -y ffmpeg

# CentOS 8+（需要先启用 epel 和 rpmfusion）
# sudo dnf install -y epel-release
# sudo dnf install -y ffmpeg

# 验证安装
ffmpeg -version
```

预期输出示例：
```
ffmpeg version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2000-2021 the FFmpeg developers
```



---

## 第五步：安装 Git 并克隆代码

### 5.1 安装并配置 Git

```bash
# 安装 Git
sudo apt install -y git

# 配置你的用户信息（首次使用必须）
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"

# 验证
git --version
```

### 5.2 克隆项目代码

```bash
# 进入你希望存放项目的目录（以 home 目录为例）
cd ~

# 从 GitHub 克隆项目
git clone https://github.com/huanxiaomang/video.git

# 进入项目根目录
cd video

# 查看项目结构
ls -la
```

克隆成功后应看到以下目录结构：

```
video/
├── server/          # 后端服务（FastAPI）
├── web-client/      # 前端服务（Vue3 + TypeScript）
├── camera-client/   # 摄像头采集端（Python）
├── mediamtx.yml     # 流媒体服务器配置
├── start-server.sh  # 后端快速启动脚本
├── start-web.sh     # 前端快速启动脚本
├── start-camera.sh  # 摄像头快速启动脚本
└── README.md
```

> 如果网络访问 GitHub 较慢，可以尝试：
> ```bash
> git clone https://gitclone.com/github.com/huanxiaomang/video.git
> ```

---

## 第六步：配置并启动后端服务

### 6.1 进入后端目录

```bash
cd ~/video/server
```

### 6.2 创建 Python 虚拟环境

```bash
# 创建虚拟环境（隔离项目依赖）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

激活成功后，命令行前缀会出现 `(venv)` 标识。

### 6.3 安装后端依赖包

```bash
pip install -r requirements.txt
```

### 6.4 启动后端服务

```bash
# 确保已激活虚拟环境
python main.py
```

看到以下输出说明启动成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

> 保持此终端窗口开启，按 Ctrl+C 会停止服务。

---

## 第七步：配置并启动前端服务

**打开一个新的终端窗口**，执行：

### 7.1 进入前端目录

```bash
cd ~/video/web-client
```

### 7.2 安装前端依赖

```bash
npm install
```

### 7.3 启动前端开发服务器

```bash
npm run dev
```

看到以下输出说明启动成功：

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

> 保持此终端窗口开启。


---

## 第八步：为什么前端启动了但没有摄像头画面

这是正常现象。**只完成第七步，通常只能看到前端页面，未必能看到视频画面**。

要正常看到摄像头视频，至少需要下面这条链路全部打通：

```text
摄像头客户端 / 推流源 → MediaMTX → 后端服务 → 前端页面
```

也就是说，以下服务通常都要正常运行：

1. **后端服务已启动**：`server/main.py`
2. **前端服务已启动**：`web-client` 的 `npm run dev`
3. **MediaMTX 已启动**：负责 RTSP / WebRTC 流转发
4. **摄像头客户端已启动，且正在推流**：`camera-client/main.py`
5. **前端里选择了正确的设备/视频源**

如果其中任意一环没启动，前端通常就只有页面，没有实际画面。

---

## 第九步：启动 MediaMTX 流媒体服务器

MediaMTX 是这个项目的视频流中转服务，**没有它，前端通常看不到视频**。

### 9.1 进入项目根目录

```bash
cd ~/video
```

### 9.2 下载 MediaMTX

```bash
wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_linux_amd64.tar.gz
```

如果你是 ARM 机器，要下载 ARM 版本，而不是 amd64 版本。

### 9.3 解压 MediaMTX

```bash
tar -xzf mediamtx_v1.5.0_linux_amd64.tar.gz
```

### 9.4 启动 MediaMTX

```bash
./mediamtx mediamtx.yml
```

看到类似下面的输出，说明启动成功：

```text
INF MediaMTX v1.5.0
INF configuration loaded from mediamtx.yml
INF [RTSP] listener opened on :8554
INF [WebRTC] listener opened on :8889
```

> 保持此终端窗口开启。

---

## 第十步：启动摄像头客户端并推流

如果你要看到真实摄像头画面，还需要启动采集端。

### 10.1 打开新终端，进入摄像头目录

```bash
cd ~/video/camera-client
```

### 10.2 创建虚拟环境并安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 10.3 检查并修改配置

先查看配置文件：

```bash
cat config.py
```
重点确认这些配置：

- `SERVER_URL` 是否指向你的后端地址，例如：`http://localhost:8000`
- `CAMERA_ID` 是否正确，通常第一个摄像头是 `0`
- `RTSP_SERVER` 是否指向运行 MediaMTX 的主机，若与本机同一台机器可使用 `localhost`
- 如果有 `.env` 文件，优先检查 `.env` 中的值是否覆盖了 `config.py` 默认值
- 设备 ID 通常不是手动填写的固定配置，而是设备注册后由后端返回，因此应重点确认“设备是否注册成功”

### 10.3.1 新手建议：用 4 个终端分别运行 4 个服务

为了避免互相影响，建议打开 4 个终端窗口或 4 个标签页，分别运行以下内容：

- 终端 1：`cd ~/video && ./mediamtx mediamtx.yml`
- 终端 2：`cd ~/video/server && source venv/bin/activate && python3 main.py`
- 终端 3：`cd ~/video/web-client && npm run dev`
- 终端 4：`cd ~/video/camera-client && source venv/bin/activate && python3 main.py`


Ubuntu 中可以按 `Ctrl + Alt + T` 多次打开多个终端；如果当前终端支持标签页，也可以按 `Ctrl + Shift + T` 新建标签页。

这样排查问题时，可以清楚看到每个模块各自的日志。请不要在同一个终端里连续启动所有服务，否则前一个进程会占住终端，后面的命令无法正常执行。

### 10.3.2 先单独测试摄像头是否能打开

如果担心摄像头本身不可用，建议先执行：

```bash
source venv/bin/activate
python3 camera_capture.py
```

如果这里都无法打开摄像头，那么即使 `python main.py` 启动了，前端也通常不会有画面。此时应优先检查摄像头设备、权限、编号以及是否被其它程序占用。

如果 `CAMERA_ID=0` 无法打开，可以尝试：

```bash
CAMERA_ID=1 python3 camera_capture.py
CAMERA_ID=2 python3 camera_capture.py
```

找到能正常打开画面的编号后，再将对应编号写入配置。请注意，项目实际使用的是 `CAMERA_ID`，不是 `CAMERA_INDEX`。

---

## 第十步补充：如何查看 Linux 终端输出

“终端输出”就是你在 Linux 终端中执行命令后，屏幕上显示出来的文字。

例如执行：

```bash
python3 main.py
```

屏幕上出现的日志、报错、提示信息，都是终端输出。排查问题时，优先把下面几个终端里的输出保存或复制出来：

- MediaMTX 终端输出
- 后端终端输出
- 前端终端输出
- 摄像头客户端终端输出

如果不会复制终端文字，可以：

- 用鼠标选中后右键复制
- 或使用 `Ctrl + Shift + C` 复制、`Ctrl + Shift + V` 粘贴
- 或直接截图发送

如果想把输出保存到文件，可以使用：

```bash
python3 main.py > log.txt 2>&1
cat log.txt
```



### 10.4 启动摄像头客户端

```bash
python main.py
```

如果启动成功，通常会看到摄像头打开、设备注册、开始推流等日志。

---

## 第十一步：如何确认每一环都正常

如果前端没有画面，请按下面顺序检查。

### 11.1 检查后端是否正常

浏览器访问：

```text
http://localhost:8000/docs
```

如果能打开 FastAPI 文档页，说明后端正常。

### 11.2 检查前端是否正常

浏览器访问：

```text
http://localhost:5173
```

如果页面能打开，说明前端正常。

### 11.3 检查 MediaMTX 是否正常

在另一个终端执行：

```bash
ss -tlnp | grep 8554
ss -tlnp | grep 8889
```

如果能看到 8554、8889 端口处于监听状态，说明 MediaMTX 已启动。

### 11.4 检查摄像头是否被 Linux 识别

```bash
ls /dev/video*
```

如果没有看到 `/dev/video0`、`/dev/video1` 之类的设备，而是提示 `No such file or directory`，说明系统当前根本没有识别到任何视频设备。

这时应优先检查：

- 摄像头是否正确接入
- 是否处于虚拟机环境，且 USB 摄像头没有直通到虚拟机
- 是否为远程服务器环境，本机其实没有物理摄像头
- 是否需要重新插拔 USB 摄像头

可以继续执行：

```bash
sudo apt install -y v4l-utils
v4l2-ctl --list-devices
```

如果当前用户没有摄像头访问权限，还需要检查用户组：

```bash
groups
```

如果输出中没有 `video`，可执行：

```bash
sudo usermod -aG video $USER
```

执行后请注销重新登录，再重新测试。

### 11.5 检查摄像头客户端是否真的在推流

看摄像头客户端终端日志，是否出现类似：

- 摄像头打开成功
- 设备注册成功
- 开始推流
- 推流地址已连接

如果看到报错，如 `Cannot open camera`、`Connection refused`、`register failed`，就说明问题在采集端。

---

## 第十二步：最常见的“有页面没画面”原因

### 情况 1：MediaMTX 没启动

这是最常见原因之一。

现象：
- 前端页面打开正常
- 后端接口正常
- 但没有视频画面

解决：

```bash
cd ~/video
./mediamtx mediamtx.yml
```

### 情况 2：摄像头客户端没启动

现象：
- 页面正常
- MediaMTX 正常
- 但没有任何视频流进入系统

解决：

```bash
cd ~/video/camera-client
source venv/bin/activate
python3 main.py
```

### 情况 3：摄像头索引不对

比如你的摄像头实际不是 `0`，而是 `1`。

解决：

```bash
ls /dev/video*
v4l2-ctl --list-devices
```

然后修改 `camera-client/config.py` 里的 `CAMERA_ID`，或在命令行中临时使用：`CAMERA_ID=1 python3 camera_capture.py` 进行测试。

### 情况 4：后端地址配置错了

如果 `camera-client` 里 `SERVER_URL` 写错，设备无法注册到后端。

需要检查：

- `camera-client/config.py`
- 前端接口地址配置

### 情况 5：你打开了前端，但没有在页面中选择设备

有些页面即使系统已经推流成功，也需要你在前端：

- 进入实时监控页
- 选择在线设备
- 点击播放/预览

如果页面里没有自动播放逻辑，就需要手动操作。

---

## 建议的正确启动顺序

每次启动系统，建议按下面顺序：

### 方式一：手动逐个启动

**终端 1：启动 MediaMTX**
```bash
cd ~/video
./mediamtx mediamtx.yml
```

**终端 2：启动后端**
```bash
cd ~/video/server
source venv/bin/activate
python main.py
```

**终端 3：启动前端**
```bash
cd ~/video/web-client
npm run dev
```

**终端 4：启动摄像头客户端**
```bash
cd ~/video/camera-client
source venv/bin/activate
python main.py
```

然后再打开浏览器访问：

```text
http://localhost:5173
```

### 方式二：后续我可以再帮你补一个一键启动脚本

如果你愿意，我可以继续把教程补成完整版，再加上：

- 一键启动脚本
- 一键停止脚本
- 开机自启 systemd 配置
- 无画面排查清单

---

## 你当前最应该做什么

你现在既然已经完成到 **7.3 前端启动**，下一步请直接做下面三件事：

### 第一步：启动 MediaMTX

```bash
cd ~/video
./mediamtx mediamtx.yml
```

### 第二步：启动摄像头客户端

```bash
cd ~/video/camera-client
source venv/bin/activate
python main.py
```

### 第三步：刷新前端页面并检查设备是否在线

如果还是没有画面，你把下面几项结果发给我，我可以继续帮你定位：

1. 后端终端输出
2. MediaMTX 终端输出
3. 摄像头客户端终端输出
4. 浏览器页面截图
5. `camera-client/config.py` 里的关键配置

这样我能直接帮你判断到底是：
- MediaMTX 没启动
- 摄像头没识别
- 推流失败
- 后端没注册成功
- 前端没选中设备

如果你愿意，我下一步可以**直接继续帮你把这份 md 教程补全成完整可执行版**。