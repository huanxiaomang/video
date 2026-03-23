"""WHIP WebRTC推流模块 - 超低延迟"""
import asyncio
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaPlayer
from aiohttp import ClientSession
from av import VideoFrame
from loguru import logger
import time
from fractions import Fraction


class CameraVideoTrack(VideoStreamTrack):
    """摄像头视频轨道"""
    
    def __init__(self, camera_id: int = 0, width: int = 1280, height: int = 720, fps: int = 30):
        super().__init__()
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        self.frame_count = 0
        self.start_time = time.time()
        
    async def start(self):
        """启动摄像头"""
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"摄像头已启动: {actual_width}x{actual_height} @ {self.fps}fps")
        
    async def recv(self):
        """接收视频帧"""
        pts, time_base = await self.next_timestamp()
        
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("读取帧失败")
            # 返回黑帧
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # 转换为 VideoFrame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        
        self.frame_count += 1
        if self.frame_count % 100 == 0:
            elapsed = time.time() - self.start_time
            actual_fps = self.frame_count / elapsed
            logger.info(f"已推流 {self.frame_count} 帧，实际帧率: {actual_fps:.2f} fps")
        
        return video_frame
    
    def stop(self):
        """停止摄像头"""
        if self.cap:
            self.cap.release()


class WHIPStreamer:
    """WHIP推流器 - 直接WebRTC推流"""
    
    def __init__(
        self,
        whip_url: str,
        camera_id: int = 0,
        width: int = 1280,
        height: int = 720,
        fps: int = 30
    ):
        self.whip_url = whip_url
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        
        self.pc = None
        self.video_track = None
        self.session = None
        
    async def start(self):
        """启动WHIP推流"""
        try:
            logger.info(f"启动WHIP推流: {self.whip_url}")
            
            # 创建 PeerConnection
            self.pc = RTCPeerConnection()
            
            # 创建视频轨道
            self.video_track = CameraVideoTrack(
                camera_id=self.camera_id,
                width=self.width,
                height=self.height,
                fps=self.fps
            )
            await self.video_track.start()
            
            # 添加视频轨道
            self.pc.addTrack(self.video_track)
            
            # 创建 Offer
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
            
            # 发送 Offer 到 WHIP 端点
            self.session = ClientSession()
            async with self.session.post(
                self.whip_url,
                data=self.pc.localDescription.sdp,
                headers={"Content-Type": "application/sdp"}
            ) as response:
                if response.status != 201:
                    raise Exception(f"WHIP请求失败: {response.status}")
                
                answer_sdp = await response.text()
                
                # 设置远程描述
                answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
                await self.pc.setRemoteDescription(answer)
            
            logger.info("WHIP推流已启动")
            return True
            
        except Exception as e:
            logger.error(f"启动WHIP推流失败: {e}")
            return False
    
    async def stop(self):
        """停止推流"""
        logger.info("停止WHIP推流...")
        
        if self.video_track:
            self.video_track.stop()
        
        if self.pc:
            await self.pc.close()
        
        if self.session:
            await self.session.close()
        
        logger.info("WHIP推流已停止")

