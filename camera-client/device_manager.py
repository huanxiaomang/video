"""设备管理模块"""
import requests
import time
import threading
import socket
from loguru import logger
from typing import Optional, Dict


class DeviceManager:
    """设备管理类"""
    
    def __init__(
        self,
        server_url: str,
        device_name: str,
        device_type: str,
        location: str
    ):
        """
        初始化设备管理器
        
        Args:
            server_url: 服务器地址
            device_name: 设备名称
            device_type: 设备类型
            location: 设备位置
        """
        self.server_url = server_url.rstrip('/')
        self.device_name = device_name
        self.device_type = device_type
        self.location = location
        
        self.device_id: Optional[str] = None
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.running = False
        
    def get_local_ip(self) -> str:
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def register(self) -> bool:
        """
        注册设备
        
        Returns:
            bool: 是否注册成功
        """
        try:
            device_info = {
                "device_name": self.device_name,
                "device_type": self.device_type,
                "location": self.location,
                "ip_address": self.get_local_ip()
            }
            
            logger.info(f"注册设备: {device_info}")
            
            response = requests.post(
                f'{self.server_url}/api/devices/register',
                json=device_info,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.device_id = data.get('device_id')
                logger.info(f"设备注册成功，ID: {self.device_id}")
                return True
            else:
                logger.error(f"设备注册失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"设备注册异常: {e}")
            return False
    
    def start_heartbeat(self, interval: int = 10):
        """
        启动心跳
        
        Args:
            interval: 心跳间隔(秒)
        """
        if self.device_id is None:
            logger.error("设备未注册，无法启动心跳")
            return
        
        self.running = True
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            args=(interval,),
            daemon=True
        )
        self.heartbeat_thread.start()
        logger.info(f"心跳已启动，间隔: {interval}秒")
    
    def _heartbeat_loop(self, interval: int):
        """心跳循环"""
        while self.running:
            try:
                response = requests.post(
                    f'{self.server_url}/api/devices/{self.device_id}/heartbeat',
                    json={'timestamp': time.time()},
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.debug(f"心跳成功: {self.device_id}")
                else:
                    logger.warning(f"心跳失败: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"心跳异常: {e}")
            
            time.sleep(interval)
    
    def stop_heartbeat(self):
        """停止心跳"""
        self.running = False
        if self.heartbeat_thread is not None:
            self.heartbeat_thread.join(timeout=5)
            logger.info("心跳已停止")
    
    def unregister(self) -> bool:
        """
        注销设备（标记为离线）
        
        Returns:
            bool: 是否注销成功
        """
        if self.device_id is None:
            return True
        
        try:
            response = requests.post(
                f'{self.server_url}/api/devices/{self.device_id}/offline',
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"设备注销成功: {self.device_id}")
                return True
            else:
                logger.error(f"设备注销失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"设备注销异常: {e}")
            return False

