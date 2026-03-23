/**
 * 系统配置API
 */
import request from './request'

export interface RecordingConfig {
  enabled: boolean
  record_path: string
  record_format: string
  part_duration: string
  segment_duration: string
  delete_after: string
}

/**
 * 获取录像配置
 */
export const getRecordingConfig = () => {
  return request.get<RecordingConfig>('/api/config/recording')
}

/**
 * 更新录像配置
 */
export const updateRecordingConfig = (config: RecordingConfig) => {
  return request.put('/api/config/recording', config)
}

/**
 * 切换录像开关
 */
export const toggleRecording = (enabled: boolean) => {
  return request.post('/api/config/recording/toggle', null, {
    params: { enabled }
  })
}

