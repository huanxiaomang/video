/**
 * 设备状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Device } from '@/types'
import { getDevices } from '@/api/device'

export const useDeviceStore = defineStore('device', () => {
  const devices = ref<Device[]>([])
  const selectedDeviceIds = ref<string[]>([])
  const loading = ref<boolean>(false)

  /**
   * 获取设备列表
   */
  async function fetchDevices(params?: { status?: string; device_type?: string }) {
    loading.value = true
    try {
      const data = await getDevices(params)
      devices.value = data
    } catch (error) {
      console.error('获取设备列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据ID获取设备
   */
  function getDeviceById(deviceId: string): Device | undefined {
    return devices.value.find((d) => d.device_id === deviceId)
  }

  /**
   * 选择设备
   */
  function selectDevice(deviceId: string) {
    if (!selectedDeviceIds.value.includes(deviceId)) {
      selectedDeviceIds.value.push(deviceId)
    }
  }

  /**
   * 取消选择设备
   */
  function unselectDevice(deviceId: string) {
    const index = selectedDeviceIds.value.indexOf(deviceId)
    if (index > -1) {
      selectedDeviceIds.value.splice(index, 1)
    }
  }

  /**
   * 清空选择
   */
  function clearSelection() {
    selectedDeviceIds.value = []
  }

  return {
    devices,
    selectedDeviceIds,
    loading,
    fetchDevices,
    getDeviceById,
    selectDevice,
    unselectDevice,
    clearSelection,
  }
})

