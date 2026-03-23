/**
 * 录像管理API
 */
import request from './request'

export interface Recording {
  recording_id: string
  device_id: string
  device_name: string
  start_time: string
  end_time: string | null
  duration: number | null
  file_path: string | null
  file_size: number | null
  status: 'recording' | 'completed' | 'error'
  created_at: string
}

export interface RecordingQuery {
  device_id?: string
  start_date?: string
  end_date?: string
  status?: string
  limit?: number
  offset?: number
}

/**
 * 获取录像列表
 */
export function getRecordings(params?: RecordingQuery) {
  return request<Recording[]>({
    url: '/api/recordings',
    method: 'get',
    params
  })
}

/**
 * 获取录像详情
 */
export function getRecording(recordingId: string) {
  return request<Recording>({
    url: `/api/recordings/${recordingId}`,
    method: 'get'
  })
}

/**
 * 创建录像记录
 */
export function createRecording(data: { device_id: string; device_name?: string }) {
  return request<Recording>({
    url: '/api/recordings',
    method: 'post',
    data
  })
}

/**
 * 更新录像记录
 */
export function updateRecording(
  recordingId: string,
  data: {
    end_time?: string
    duration?: number
    file_path?: string
    file_size?: number
    status?: string
  }
) {
  return request<Recording>({
    url: `/api/recordings/${recordingId}`,
    method: 'put',
    data
  })
}

/**
 * 删除录像记录
 */
export function deleteRecording(recordingId: string) {
  return request({
    url: `/api/recordings/${recordingId}`,
    method: 'delete'
  })
}

/**
 * 获取录像文件URL
 */
export function getRecordingUrl(filePath: string): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}${filePath}`
}

