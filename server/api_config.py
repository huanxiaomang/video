"""系统配置API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import yaml
from pathlib import Path
from loguru import logger

router = APIRouter(prefix="/api/config", tags=["配置管理"])

MEDIAMTX_CONFIG_PATH = Path("mediamtx.yml")


class RecordingConfig(BaseModel):
    """录像配置"""
    enabled: bool
    record_path: str
    record_format: str
    part_duration: str
    segment_duration: str
    delete_after: str


class SystemConfig(BaseModel):
    """系统配置"""
    recording: RecordingConfig


@router.get("/recording", response_model=RecordingConfig)
async def get_recording_config():
    """获取录像配置"""
    try:
        if not MEDIAMTX_CONFIG_PATH.exists():
            raise HTTPException(status_code=404, detail="配置文件不存在")
        
        with open(MEDIAMTX_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        paths_config = config.get('paths', {}).get('all', {})
        
        return RecordingConfig(
            enabled=paths_config.get('record', False),
            record_path=paths_config.get('recordPath', './server/recordings/%path/%Y-%m-%d_%H-%M-%S'),
            record_format=paths_config.get('recordFormat', 'fmp4'),
            part_duration=paths_config.get('recordPartDuration', '1h'),
            segment_duration=paths_config.get('recordSegmentDuration', '1h'),
            delete_after=paths_config.get('recordDeleteAfter', '168h')
        )
    except Exception as e:
        logger.error(f"获取录像配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/recording")
async def update_recording_config(config: RecordingConfig):
    """更新录像配置"""
    try:
        if not MEDIAMTX_CONFIG_PATH.exists():
            raise HTTPException(status_code=404, detail="配置文件不存在")
        
        # 读取现有配置
        with open(MEDIAMTX_CONFIG_PATH, 'r', encoding='utf-8') as f:
            mediamtx_config = yaml.safe_load(f)
        
        # 更新录像配置
        if 'paths' not in mediamtx_config:
            mediamtx_config['paths'] = {}
        if 'all' not in mediamtx_config['paths']:
            mediamtx_config['paths']['all'] = {}
        
        mediamtx_config['paths']['all']['record'] = config.enabled
        mediamtx_config['paths']['all']['recordPath'] = config.record_path
        mediamtx_config['paths']['all']['recordFormat'] = config.record_format
        mediamtx_config['paths']['all']['recordPartDuration'] = config.part_duration
        mediamtx_config['paths']['all']['recordSegmentDuration'] = config.segment_duration
        mediamtx_config['paths']['all']['recordDeleteAfter'] = config.delete_after
        
        # 写回配置文件
        with open(MEDIAMTX_CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(mediamtx_config, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"录像配置已更新: enabled={config.enabled}")
        
        return {
            "message": "录像配置已更新，需要重启MediaMTX才能生效",
            "config": config
        }
    except Exception as e:
        logger.error(f"更新录像配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recording/toggle")
async def toggle_recording(enabled: bool):
    """快速切换录像开关"""
    try:
        if not MEDIAMTX_CONFIG_PATH.exists():
            raise HTTPException(status_code=404, detail="配置文件不存在")
        
        with open(MEDIAMTX_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if 'paths' not in config:
            config['paths'] = {}
        if 'all' not in config['paths']:
            config['paths']['all'] = {}
        
        config['paths']['all']['record'] = enabled
        
        with open(MEDIAMTX_CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"录像功能已{'启用' if enabled else '禁用'}")
        
        return {
            "message": f"录像功能已{'启用' if enabled else '禁用'}，需要重启MediaMTX才能生效",
            "enabled": enabled
        }
    except Exception as e:
        logger.error(f"切换录像功能失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

