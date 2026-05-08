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


from picamera2 import Picamera2



class CameraVideoTrack(VideoStreamTrack):

    def __init__(self, width=1280, height=720, fps=30):
        super().__init__()

        self.width = width
        self.height = height
        self.fps = fps

        self.picam2 = Picamera2()

        config = self.picam2.create_video_configuration(
            main={"size": (width, height), "format": "RGB888"}
        )

        self.picam2.configure(config)

        self.picam2.start()

        self.frame_count = 0
        self.start_time = time.time()

    async def recv(self):

        pts, time_base = await self.next_timestamp()

        frame = self.picam2.capture_array()



        video_frame = VideoFrame.from_ndarray(
            frame,
            format="bgr24"
        )

        video_frame.pts = pts
        video_frame.time_base = time_base

        self.frame_count += 1

        return video_frame

    def stop(self):
        self.picam2.stop()


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
                width=self.width,
                height=self.height,
                fps=self.fps
            )
            
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

