/**
 * 设备API
 */
import request from './request'
import type { Device } from '@/types'

/**
 * 获取设备列表
 */
export function getDevices(params?: {
  status?: string
  device_type?: string
}): Promise<Device[]> {
  return request({
    url: '/api/devices',
    method: 'get',
    params,
  })
}

/**
 * 获取设备详情
 */
export function getDevice(deviceId: string): Promise<Device> {
  return request({
    url: `/api/devices/${deviceId}`,
    method: 'get',
  })
}

/**
 * 删除设备
 */
export function deleteDevice(deviceId: string): Promise<any> {
  return request({
    url: `/api/devices/${deviceId}`,
    method: 'delete',
  })
}

