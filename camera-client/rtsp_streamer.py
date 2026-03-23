"""RTSP推流模块 - 使用FFmpeg"""
import subprocess
import numpy as np
from loguru import logger
from typing import Optional
import threading
import queue


class RTSPStreamer:
    """RTSP推流类"""
    
    def __init__(
        self,
        width: int,
        height: int,
        fps: int,
        bitrate: int,
        rtsp_url: str,
        codec: str = 'libx264',
        preset: str = 'ultrafast',
        tune: str = 'zerolatency'
    ):
        """
        初始化RTSP推流器
        
        Args:
            width: 视频宽度
            height: 视频高度
            fps: 帧率
            bitrate: 码率(kbps)
            rtsp_url: RTSP推流地址
            codec: 编码器
            preset: 编码预设
            tune: 编码调优
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.bitrate = bitrate
        self.rtsp_url = rtsp_url
        self.codec = codec
        self.preset = preset
        self.tune = tune
        
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        
    def start(self) -> bool:
        """
        启动推流

        Returns:
            bool: 是否成功启动
        """
        try:
            # FFmpeg命令 - 推流到RTSP服务器
            # 优化参数以减少延迟
            cmd = [
                'ffmpeg',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-pix_fmt', 'bgr24',
                '-s', f'{self.width}x{self.height}',
                '-r', str(self.fps),
                '-i', '-',  # 从stdin读取
                '-c:v', self.codec,
                '-preset', self.preset,
                '-tune', self.tune,
                '-b:v', f'{self.bitrate}k',
                '-maxrate', f'{self.bitrate}k',
                '-bufsize', f'{self.bitrate}k',  # 减小缓冲区
                '-g', str(self.fps),  # GOP大小为1秒，减少延迟
                '-keyint_min', str(self.fps),  # 最小关键帧间隔
                '-sc_threshold', '0',  # 禁用场景切换检测
                '-pix_fmt', 'yuv420p',
                '-an',  # 无音频
                '-probesize', '32',  # 减小探测大小
                '-analyzeduration', '0',  # 不分析
                '-fflags', 'nobuffer',  # 无缓冲
                '-flags', 'low_delay',  # 低延迟标志
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                self.rtsp_url
            ]

            logger.info(f"启动FFmpeg推流: {self.rtsp_url}")
            logger.debug(f"FFmpeg命令: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,  # 忽略stdout
                stderr=subprocess.PIPE,
                bufsize=10**8
            )

            # 等待一小段时间，检查进程是否立即退出
            import time
            time.sleep(0.5)

            if self.process.poll() is not None:
                # 进程已退出，读取错误信息
                stderr = self.process.stderr.read().decode('utf-8', errors='ignore')
                logger.error(f"FFmpeg进程启动后立即退出，错误信息:\n{stderr}")
                return False

            self.is_running = True
            logger.info("RTSP推流已启动")
            return True

        except Exception as e:
            logger.error(f"启动推流失败: {e}")
            return False
    
    def write_frame(self, frame: np.ndarray) -> bool:
        """
        写入一帧
        
        Args:
            frame: 视频帧
            
        Returns:
            bool: 是否成功写入
        """
        if not self.is_running or self.process is None or self.process.stdin is None:
            logger.warning("推流未启动")
            return False
        
        try:
            self.process.stdin.write(frame.tobytes())
            return True
        except Exception as e:
            logger.error(f"写入帧失败: {e}")
            return False
    
    def stop(self):
        """停止推流"""
        if self.process is not None:
            try:
                if self.process.stdin:
                    self.process.stdin.close()
                self.process.wait(timeout=5)
                logger.info("RTSP推流已停止")
            except subprocess.TimeoutExpired:
                self.process.kill()
                logger.warning("强制终止FFmpeg进程")
            except Exception as e:
                logger.error(f"停止推流失败: {e}")
            finally:
                self.is_running = False
    
    def __del__(self):
        """析构函数"""
        self.stop()

