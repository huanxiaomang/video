<template>
  <div class="live-monitor">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="left">
        <el-button-group>
          <el-button :type="layout === 1 ? 'primary' : ''" @click="setLayout(1)">1分屏</el-button>
          <el-button :type="layout === 4 ? 'primary' : ''" @click="setLayout(4)">4分屏</el-button>
          <el-button :type="layout === 9 ? 'primary' : ''" @click="setLayout(9)">9分屏</el-button>
          <el-button :type="layout === 16 ? 'primary' : ''" @click="setLayout(16)">16分屏</el-button>
        </el-button-group>
      </div>
      <div class="right">
        <el-button @click="refreshDevices" :loading="deviceStore.loading">
          <el-icon><Refresh /></el-icon>
          刷新设备
        </el-button>
      </div>
    </div>

    <!-- 视频网格 -->
    <div class="video-grid" :class="`grid-${layout}`">
      <div
        v-for="index in layout"
        :key="index"
        class="video-cell"
        @click="handleCellClick(index - 1)"
      >
        <VideoPlayer
          v-if="selectedDevices[index - 1]"
          :device="selectedDevices[index - 1]!"
          @close="handleCloseVideo(index - 1)"
        />
        <div v-else class="empty-cell">
          <el-icon :size="40"><VideoCameraFilled /></el-icon>
          <p>点击选择设备</p>
        </div>
      </div>
    </div>

    <!-- 设备选择对话框 -->
    <el-dialog v-model="showDeviceDialog" title="选择设备" width="600px">
      <el-table :data="onlineDevices" @row-click="handleSelectDevice" highlight-current-row>
        <el-table-column prop="device_name" label="设备名称" />
        <el-table-column prop="device_type" label="设备类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.device_type === 'robot' ? 'success' : 'info'">
              {{ row.device_type === 'robot' ? '机器人' : '固定' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="位置" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Refresh, VideoCameraFilled } from '@element-plus/icons-vue'
import { useDeviceStore } from '@/stores/device'
import type { Device, LayoutType } from '@/types'
import VideoPlayer from '@/components/VideoPlayer.vue'

const deviceStore = useDeviceStore()

const STORAGE_KEY_LAYOUT = 'live_monitor_layout'
const STORAGE_KEY_DEVICES = 'live_monitor_devices'

const layout = ref<LayoutType>(4)
const selectedDevices = ref<(Device | null)[]>([])
const showDeviceDialog = ref(false)
const currentCellIndex = ref(0)

const onlineDevices = computed(() => {
  return deviceStore.devices.filter((d) => d.status === 'online')
})

// 保存布局到localStorage
const saveLayoutToStorage = () => {
  try {
    localStorage.setItem(STORAGE_KEY_LAYOUT, String(layout.value))

    // 保存设备ID列表（只保存ID，不保存完整对象）
    const deviceIds = selectedDevices.value.map(d => d?.device_id || null)
    localStorage.setItem(STORAGE_KEY_DEVICES, JSON.stringify(deviceIds))
  } catch (error) {
    // 静默失败，不影响用户体验
    console.warn('保存布局失败:', error)
  }
}

// 从localStorage恢复布局
const loadLayoutFromStorage = () => {
  try {
    const savedLayout = localStorage.getItem(STORAGE_KEY_LAYOUT)
    const savedDeviceIds = localStorage.getItem(STORAGE_KEY_DEVICES)

    if (savedLayout) {
      const layoutValue = parseInt(savedLayout) as LayoutType
      if ([1, 4, 9, 16].includes(layoutValue)) {
        layout.value = layoutValue
      }
    }

    if (savedDeviceIds) {
      const deviceIds: (string | null)[] = JSON.parse(savedDeviceIds)

      // 等待设备列表加载后再恢复
      const restoreDevices = () => {
        const devices = deviceIds.map(id => {
          if (!id) return null
          // 从设备列表中查找对应的设备
          return deviceStore.devices.find(d => d.device_id === id) || null
        })

        selectedDevices.value = devices
      }

      // 如果设备列表已加载，立即恢复；否则等待
      if (deviceStore.devices.length > 0) {
        restoreDevices()
      } else {
        // 延迟恢复，等待设备列表加载
        setTimeout(restoreDevices, 1000)
      }
    }
  } catch (error) {
    // 静默失败，使用默认布局
    console.warn('恢复布局失败:', error)
  }
}

const setLayout = (newLayout: LayoutType) => {
  layout.value = newLayout
  // 调整选中设备数组大小
  if (selectedDevices.value.length > newLayout) {
    selectedDevices.value = selectedDevices.value.slice(0, newLayout)
  } else {
    while (selectedDevices.value.length < newLayout) {
      selectedDevices.value.push(null)
    }
  }
  saveLayoutToStorage()
}

const handleCellClick = (index: number) => {
  currentCellIndex.value = index
  showDeviceDialog.value = true
}

const handleSelectDevice = (device: Device) => {
  selectedDevices.value[currentCellIndex.value] = device
  showDeviceDialog.value = false
  saveLayoutToStorage()
}

const handleCloseVideo = (index: number) => {
  selectedDevices.value[index] = null
  saveLayoutToStorage()
}

const refreshDevices = async () => {
  await deviceStore.fetchDevices({ status: 'online' })
}

// 监听selectedDevices变化，自动保存
watch(selectedDevices, () => {
  saveLayoutToStorage()
}, { deep: true })

onMounted(async () => {
  // 先加载设备列表
  await refreshDevices()

  // 然后恢复布局
  loadLayoutFromStorage()

  // 如果没有恢复到布局，使用默认4分屏
  if (selectedDevices.value.length === 0) {
    setLayout(4)
  }
})
</script>

<style scoped>
.live-monitor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 4px;
}

.video-grid {
  flex: 1;
  display: grid;
  gap: 10px;
  overflow: auto;
}

.grid-1 {
  grid-template-columns: 1fr;
  grid-template-rows: 1fr;
}

.grid-4 {
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
}

.grid-9 {
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
}

.grid-16 {
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(4, 1fr);
}

.video-cell {
  background: #000;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  min-height: 200px;
}

.empty-cell {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.empty-cell:hover {
  background: #1a1a1a;
  color: #409eff;
}

.empty-cell p {
  margin-top: 10px;
  font-size: 14px;
}
</style>

