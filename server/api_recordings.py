"""录像管理API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger
import os

from database import get_db
from models import Recording, Device
from config import settings

router = APIRouter()


# Pydantic模型
class RecordingResponse(BaseModel):
    recording_id: str
    device_id: str
    device_name: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[int]
    file_path: Optional[str]
    file_size: Optional[int]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecordingCreate(BaseModel):
    device_id: str
    device_name: Optional[str] = None


class RecordingUpdate(BaseModel):
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    status: Optional[str] = None


@router.get("", response_model=List[RecordingResponse])
async def get_recordings(
    device_id: Optional[str] = None,
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    status: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """获取录像列表"""
    try:
        query = select(Recording)
        
        # 过滤条件
        conditions = []
        
        if device_id:
            conditions.append(Recording.device_id == device_id)
        
        if status:
            conditions.append(Recording.status == status)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            conditions.append(Recording.start_time >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date) + timedelta(days=1)
            conditions.append(Recording.start_time < end_dt)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序和分页
        query = query.order_by(Recording.start_time.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        recordings = result.scalars().all()
        
        return recordings
        
    except Exception as e:
        logger.error(f"获取录像列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取录像详情"""
    try:
        result = await db.execute(
            select(Recording).where(Recording.recording_id == recording_id)
        )
        recording = result.scalar_one_or_none()
        
        if recording is None:
            raise HTTPException(status_code=404, detail="录像不存在")
        
        return recording
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取录像详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=RecordingResponse)
async def create_recording(
    recording_data: RecordingCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建录像记录"""
    try:
        # 验证设备是否存在
        device_result = await db.execute(
            select(Device).where(Device.device_id == recording_data.device_id)
        )
        device = device_result.scalar_one_or_none()
        
        if device is None:
            raise HTTPException(status_code=404, detail="设备不存在")
        
        # 创建录像记录
        recording = Recording(
            device_id=recording_data.device_id,
            device_name=recording_data.device_name or device.device_name,
            start_time=datetime.utcnow(),
            status="recording"
        )
        
        db.add(recording)
        await db.commit()
        await db.refresh(recording)
        
        logger.info(f"创建录像记录: {recording.recording_id}")

        return recording

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建录像记录失败: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{recording_id}", response_model=RecordingResponse)
async def update_recording(
    recording_id: str,
    recording_data: RecordingUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新录像记录"""
    try:
        result = await db.execute(
            select(Recording).where(Recording.recording_id == recording_id)
        )
        recording = result.scalar_one_or_none()

        if recording is None:
            raise HTTPException(status_code=404, detail="录像不存在")

        # 更新字段
        if recording_data.end_time is not None:
            recording.end_time = recording_data.end_time
        if recording_data.duration is not None:
            recording.duration = recording_data.duration
        if recording_data.file_path is not None:
            recording.file_path = recording_data.file_path
        if recording_data.file_size is not None:
            recording.file_size = recording_data.file_size
        if recording_data.status is not None:
            recording.status = recording_data.status

        await db.commit()
        await db.refresh(recording)

        logger.info(f"更新录像记录: {recording_id}")

        return recording

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新录像记录失败: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{recording_id}")
async def delete_recording(
    recording_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除录像记录"""
    try:
        result = await db.execute(
            select(Recording).where(Recording.recording_id == recording_id)
        )
        recording = result.scalar_one_or_none()

        if recording is None:
            raise HTTPException(status_code=404, detail="录像不存在")

        # 删除文件
        if recording.file_path and os.path.exists(recording.file_path):
            os.remove(recording.file_path)
            logger.info(f"删除录像文件: {recording.file_path}")

        # 删除数据库记录
        await db.delete(recording)
        await db.commit()

        logger.info(f"删除录像记录: {recording_id}")

        return {"message": "录像删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除录像记录失败: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

