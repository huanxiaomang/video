"""录像文件扫描服务"""
import os
import asyncio
from datetime import datetime
from pathlib import Path
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Recording, Device, AsyncSessionLocal
from config import settings


class RecordingScanner:
    """录像文件扫描器"""

    def __init__(self, recording_path: str = None):
        self.recording_path = recording_path or settings.RECORDING_PATH
        self.scan_interval = 60  # 扫描间隔（秒）
        self.running = False

    async def scan_recordings(self):
        """扫描录像目录并创建数据库记录"""
        try:
            if not os.path.exists(self.recording_path):
                return


            async with AsyncSessionLocal() as db:
                # 遍历录像目录
                for device_dir in Path(self.recording_path).iterdir():
                    if not device_dir.is_dir():
                        continue

                    device_id = device_dir.name

                    # 检查设备是否存在
                    result = await db.execute(
                        select(Device).where(Device.device_id == device_id)
                    )
                    device = result.scalar_one_or_none()

                    if not device:
                        logger.warning(f"设备不存在: {device_id}")
                        continue

                    # 扫描设备目录下的录像文件
                    for file_path in device_dir.glob('*.mp4'):
                        await self._process_recording_file(db, device, file_path)

                    # 扫描fmp4文件
                    for file_path in device_dir.glob('*.fmp4'):
                        await self._process_recording_file(db, device, file_path)

                await db.commit()

        except Exception as e:
            logger.error(f"扫描录像失败: {e}")

    async def _process_recording_file(
        self,
        db: AsyncSession,
        device: Device,
        file_path: Path
    ):
        """处理单个录像文件"""
        try:
            # 检查文件是否已存在于数据库
            file_path_str = str(file_path.relative_to(Path.cwd()))

            result = await db.execute(
                select(Recording).where(Recording.file_path == file_path_str)
            )
            existing = result.scalar_one_or_none()

            if existing:
                return  # 已存在，跳过

            # 获取文件信息
            stat = file_path.stat()
            file_size = stat.st_size

            # 从文件名解析时间（格式：YYYY-MM-DD_HH-MM-SS.mp4）
            filename = file_path.stem
            try:
                start_time = datetime.strptime(filename, '%Y-%m-%d_%H-%M-%S')
            except ValueError:
                # 如果文件名格式不匹配，使用文件创建时间
                start_time = datetime.fromtimestamp(stat.st_ctime)

            # 创建录像记录
            recording = Recording(
                device_id=device.device_id,
                device_name=device.device_name,
                start_time=start_time,
                end_time=datetime.fromtimestamp(stat.st_mtime),
                duration=None,  # 需要ffprobe获取，暂时为空
                file_path=file_path_str,
                file_size=file_size,
                status='completed'
            )

            db.add(recording)
            logger.info(f"添加录像记录: {file_path_str}")

        except Exception as e:
            logger.error(f"处理录像文件失败 {file_path}: {e}")

    async def start(self):
        """启动扫描服务"""
        self.running = True

        while self.running:
            await self.scan_recordings()
            await asyncio.sleep(self.scan_interval)

    def stop(self):
        """停止扫描服务"""
        self.running = False


# 全局扫描器实例
scanner = RecordingScanner()


async def start_scanner():
    """启动扫描器"""
    await scanner.start()


def stop_scanner():
    """停止扫描器"""
    scanner.stop()

