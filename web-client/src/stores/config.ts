import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export interface SystemSettings {
  systemName: string
  defaultLayout: 1 | 4 | 9 | 16
  autoRefresh: boolean
  refreshInterval: number
}

const DEFAULT_SETTINGS: SystemSettings = {
  systemName: '视频监控管理系统',
  defaultLayout: 4,
  autoRefresh: true,
  refreshInterval: 10
}

export const useConfigStore = defineStore('config', () => {
  const settings = ref<SystemSettings>({ ...DEFAULT_SETTINGS })

  // 从 localStorage 加载设置
  const loadSettings = () => {
    const saved = localStorage.getItem('system_settings')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        settings.value = { ...DEFAULT_SETTINGS, ...parsed }
      } catch (e) {
        console.error('解析系统设置失败:', e)
      }
    }
  }

  // 保存设置到 localStorage
  const saveSettings = (newSettings: SystemSettings) => {
    settings.value = { ...newSettings }
    localStorage.setItem('system_settings', JSON.stringify(settings.value))
  }

  // 重置设置
  const resetSettings = () => {
    settings.value = { ...DEFAULT_SETTINGS }
    localStorage.setItem('system_settings', JSON.stringify(settings.value))
  }

  // 初始化加载
  loadSettings()

  return {
    settings,
    saveSettings,
    resetSettings,
    loadSettings
  }
})
