"""摄像头采集模块"""
import cv2
import numpy as np
from loguru import logger
from typing import Optional


class CameraCapture:
    """摄像头采集类"""
    
    def __init__(self, camera_id: int = 0, width: int = 1280, height: int = 720, fps: int = 25):
        """
        初始化摄像头
        
        Args:
            camera_id: 摄像头ID，0表示默认摄像头
            width: 视频宽度
            height: 视频高度
            fps: 帧率
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        
    def start(self) -> bool:
        """
        启动摄像头
        
        Returns:
            bool: 是否成功启动
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                logger.error(f"无法打开摄像头 {self.camera_id}")
                return False
            
            # 设置分辨率
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # 验证设置
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            logger.info(f"摄像头已启动: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            self.is_running = True
            return True
            
        except Exception as e:
            logger.error(f"启动摄像头失败: {e}")
            return False
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        读取一帧
        
        Returns:
            np.ndarray: 视频帧，如果失败返回None
        """
        if not self.is_running or self.cap is None:
            logger.warning("摄像头未启动")
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            logger.warning("读取帧失败")
            return None
        
        return frame
    
    def stop(self):
        """停止摄像头"""
        if self.cap is not None:
            self.cap.release()
            self.is_running = False
            logger.info("摄像头已停止")
    
    def __del__(self):
        """析构函数"""
        self.stop()


if __name__ == "__main__":
    # 测试代码
    import time
    
    logger.info("开始测试摄像头采集...")
    
    camera = CameraCapture(camera_id=0, width=1280, height=720, fps=25)
    
    if camera.start():
        logger.info("摄像头启动成功，开始采集...")
        
        for i in range(100):  # 采集100帧
            frame = camera.read_frame()
            if frame is not None:
                logger.info(f"采集第 {i+1} 帧，形状: {frame.shape}")
                
                # 显示画面（可选）
                cv2.imshow('Camera Test', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            time.sleep(0.04)  # 25fps
        
        camera.stop()
        cv2.destroyAllWindows()
        logger.info("测试完成")
    else:
        logger.error("摄像头启动失败")

