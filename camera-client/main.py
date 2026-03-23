"""摄像头采集端主程序"""
import sys
import time
import signal
import asyncio
from loguru import logger

from whip_streamer import WHIPStreamer
from device_manager import DeviceManager
import config


class CameraClient:
    """摄像头客户端"""

    def __init__(self):
        self.streamer: WHIPStreamer = None
        self.device_manager: DeviceManager = None
        self.running = False
        self.loop = None
        
    async def setup(self) -> bool:
        """初始化设置"""
        try:
            # 配置日志
            logger.remove()
            logger.add(
                sys.stderr,
                level=config.LOG_LEVEL,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
            )
            logger.add(
                "logs/camera_client_{time}.log",
                rotation="100 MB",
                retention="7 days",
                level=config.LOG_LEVEL
            )

            logger.info("=" * 60)
            logger.info("摄像头采集端启动 (WHIP模式)")
            logger.info("=" * 60)

            # 初始化设备管理器
            self.device_manager = DeviceManager(
                server_url=config.SERVER_URL,
                device_name=config.DEVICE_NAME,
                device_type=config.DEVICE_TYPE,
                location=config.DEVICE_LOCATION
            )

            # 注册设备
            if not self.device_manager.register():
                logger.error("设备注册失败")
                return False

            # 启动心跳
            self.device_manager.start_heartbeat(config.HEARTBEAT_INTERVAL)

            # 初始化WHIP推流器
            # MediaMTX WHIP端点: http://localhost:8889/{path}/whip
            whip_url = f"http://{config.RTSP_SERVER}:8889/{self.device_manager.device_id}/whip"

            self.streamer = WHIPStreamer(
                whip_url=whip_url,
                camera_id=config.CAMERA_ID,
                width=config.RESOLUTION_WIDTH,
                height=config.RESOLUTION_HEIGHT,
                fps=config.FPS
            )

            if not await self.streamer.start():
                logger.error("WHIP推流启动失败")
                return False

            logger.info("初始化完成")
            return True

        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return False
    
    async def run(self):
        """运行主循环"""
        self.running = True

        logger.info("WHIP推流运行中...")

        try:
            # WHIP推流是异步的，只需要保持连接
            while self.running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("收到中断信号")
        except Exception as e:
            logger.error(f"运行异常: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """清理资源"""
        logger.info("开始清理资源...")

        self.running = False

        if self.streamer:
            await self.streamer.stop()

        if self.device_manager:
            self.device_manager.stop_heartbeat()
            self.device_manager.unregister()

        logger.info("资源清理完成")
        logger.info("摄像头采集端已停止")


async def main():
    """主函数"""
    client = CameraClient()

    # 信号处理
    def signal_handler(sig, frame):
        logger.info(f"收到信号 {sig}")
        client.running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动
    if await client.setup():
        await client.run()
    else:
        logger.error("启动失败")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

