<template>
  <div class="playback-page">
    <el-card>
      <template #header>
        <span>录像回放</span>
      </template>

      <div class="playback-container">
        <!-- 左侧：录像列表 -->
        <div class="recording-list">
          <div class="filter-section">
            <el-select v-model="selectedDevice" placeholder="选择设备" clearable>
              <el-option
                v-for="device in deviceStore.devices"
                :key="device.device_id"
                :label="device.device_name"
                :value="device.device_id"
              />
            </el-select>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
            />
            <el-button type="primary" @click="searchRecordings">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </div>

          <el-table
            :data="recordings"
            height="calc(100% - 80px)"
            @row-click="handlePlayRecording"
            v-loading="loading"
            highlight-current-row
          >
            <el-table-column prop="device_name" label="设备名称" width="120" />
            <el-table-column prop="start_time" label="开始时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.start_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="时长" width="80">
              <template #default="{ row }">
                {{ formatDuration(row.duration) }}
              </template>
            </el-table-column>
            <el-table-column prop="file_size" label="大小" width="100">
              <template #default="{ row }">
                {{ formatFileSize(row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
                  {{ row.status === 'completed' ? '完成' : '录制中' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 右侧：播放器 -->
        <div class="player-section">
          <div v-if="currentRecording" class="video-player">
            <video ref="videoPlayer" controls autoplay style="width: 100%; height: 100%">
              <source :src="currentRecording.file_path" type="video/mp4" />
              您的浏览器不支持视频播放
            </video>
          </div>
          <div v-else class="empty-player">
            <el-icon :size="60"><VideoPlay /></el-icon>
            <p>请选择录像进行回放</p>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, VideoPlay } from '@element-plus/icons-vue'
import { useDeviceStore } from '@/stores/device'
import { getRecordings, getRecordingUrl, type Recording } from '@/api/recording'

const deviceStore = useDeviceStore()

const selectedDevice = ref('')
const dateRange = ref<[Date, Date]>()
const recordings = ref<Recording[]>([])
const currentRecording = ref<Recording | null>(null)
const videoPlayer = ref<HTMLVideoElement>()
const loading = ref(false)

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

const formatDuration = (seconds?: number) => {
  if (!seconds) return '-'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const formatFileSize = (bytes?: number) => {
  if (!bytes) return '-'
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(2)} MB`
}

const searchRecordings = async () => {
  try {
    loading.value = true

    const params: any = {}

    if (selectedDevice.value) {
      params.device_id = selectedDevice.value
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      params.end_date = dateRange.value[1].toISOString().split('T')[0]
    }

    const response = await getRecordings(params)
    recordings.value = response.data || response as any

    if (recordings.value.length === 0) {
      ElMessage.info('未找到录像记录')
    }
  } catch (error) {
    console.error('获取录像列表失败:', error)
    ElMessage.error('获取录像列表失败')
  } finally {
    loading.value = false
  }
}

const handlePlayRecording = (recording: Recording) => {
  if (recording.status !== 'completed' || !recording.file_path) {
    ElMessage.warning('该录像尚未完成或文件不存在')
    return
  }

  currentRecording.value = {
    ...recording,
    file_path: getRecordingUrl(recording.file_path)
  }

  // 等待DOM更新后播放
  setTimeout(() => {
    if (videoPlayer.value) {
      videoPlayer.value.load()
      videoPlayer.value.play()
    }
  }, 100)
}

onMounted(async () => {
  await deviceStore.fetchDevices()
  // 默认加载最近的录像
  await searchRecordings()
})
</script>

<style scoped>
.playback-page {
  height: 100%;
}

.playback-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.recording-list {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.player-section {
  flex: 2;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  height: 100%;
}

.empty-player {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #666;
}

.empty-player p {
  margin-top: 20px;
  font-size: 16px;
}
</style>

