<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 基本设置 -->
        <el-tab-pane label="基本设置" name="basic">
          <el-form :model="basicSettings" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="basicSettings.systemName" />
            </el-form-item>
            <el-form-item label="默认分屏">
              <el-select v-model="basicSettings.defaultLayout">
                <el-option label="1分屏" :value="1" />
                <el-option label="4分屏" :value="4" />
                <el-option label="9分屏" :value="9" />
                <el-option label="16分屏" :value="16" />
              </el-select>
            </el-form-item>
            <el-form-item label="自动刷新">
              <el-switch v-model="basicSettings.autoRefresh" />
              <span style="margin-left: 10px">每 {{ basicSettings.refreshInterval }} 秒</span>
            </el-form-item>
            <el-form-item label="刷新间隔">
              <el-slider
                v-model="basicSettings.refreshInterval"
                :min="5"
                :max="60"
                :disabled="!basicSettings.autoRefresh"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 视频设置 -->
        <el-tab-pane label="视频设置" name="video">
          <el-form :model="videoSettings" label-width="120px">
            <el-form-item label="默认分辨率">
              <el-select v-model="videoSettings.defaultResolution">
                <el-option label="720P" value="720p" />
                <el-option label="1080P" value="1080p" />
                <el-option label="4K" value="4k" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认帧率">
              <el-select v-model="videoSettings.defaultFps">
                <el-option label="15 fps" :value="15" />
                <el-option label="25 fps" :value="25" />
                <el-option label="30 fps" :value="30" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认码率">
              <el-input v-model="videoSettings.defaultBitrate" type="number">
                <template #append>kbps</template>
              </el-input>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 录像设置 -->
        <el-tab-pane label="录像设置" name="recording">
          <el-alert
            title="提示"
            type="warning"
            :closable="false"
            style="margin-bottom: 20px"
          >
            修改录像配置后需要重启MediaMTX才能生效
          </el-alert>

          <el-form :model="recordingSettings" label-width="140px" v-loading="recordingLoading">
            <el-form-item label="启用自动录像">
              <el-switch
                v-model="recordingSettings.enabled"
                @change="handleRecordingToggle"
                :loading="toggleLoading"
              />
              <span style="margin-left: 10px; color: #909399">
                {{ recordingSettings.enabled ? '已启用' : '已禁用' }}
              </span>
            </el-form-item>

            <el-divider />

            <el-form-item label="录像格式">
              <el-select v-model="recordingSettings.record_format" disabled>
                <el-option label="fmp4 (推荐)" value="fmp4" />
                <el-option label="mpegts" value="mpegts" />
              </el-select>
              <div style="color: #909399; font-size: 12px; margin-top: 5px">
                fmp4格式浏览器原生支持，适合Web播放
              </div>
            </el-form-item>

            <el-form-item label="录像路径">
              <el-input v-model="recordingSettings.record_path" disabled>
                <template #prepend>./</template>
              </el-input>
              <div style="color: #909399; font-size: 12px; margin-top: 5px">
                %path = 设备ID, %Y-%m-%d_%H-%M-%S = 时间戳
              </div>
            </el-form-item>

            <el-form-item label="分段时长">
              <el-input v-model="recordingSettings.part_duration">
                <template #append>小时</template>
              </el-input>
              <div style="color: #909399; font-size: 12px; margin-top: 5px">
                每个录像文件的时长（如：1h = 1小时）
              </div>
            </el-form-item>

            <el-form-item label="段落时长">
              <el-input v-model="recordingSettings.segment_duration">
                <template #append>小时</template>
              </el-input>
            </el-form-item>

            <el-form-item label="自动删除">
              <el-input v-model="recordingSettings.delete_after">
                <template #append>小时</template>
              </el-input>
              <div style="color: #909399; font-size: 12px; margin-top: 5px">
                录像保存时长，超过后自动删除（168h = 7天）
              </div>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveRecordingConfig" :loading="saveLoading">
                保存录像配置
              </el-button>
              <el-button @click="loadRecordingConfig">
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 用户信息 -->
        <el-tab-pane label="用户信息" name="user">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">
              {{ userStore.userInfo?.username }}
            </el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag>{{ getRoleText(userStore.userInfo?.role) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ userStore.userInfo?.created_at ? formatTime(userStore.userInfo.created_at) : '-' }}
            </el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <el-form label-width="120px">
            <el-form-item label="修改密码">
              <el-button type="primary">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 关于 -->
        <el-tab-pane label="关于" name="about">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统名称">
              电厂巡检视频监控系统
            </el-descriptions-item>
            <el-descriptions-item label="版本">
              v1.0.0
            </el-descriptions-item>
            <el-descriptions-item label="描述">
              端到端无线视频传输系统，用于电厂机器人巡检
            </el-descriptions-item>
            <el-descriptions-item label="技术栈">
              Vue 3 + TypeScript + Element Plus
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>

      <div class="action-buttons">
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
        <el-button @click="resetSettings">重置</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { getRecordingConfig, updateRecordingConfig, toggleRecording, type RecordingConfig } from '@/api/config'

const userStore = useUserStore()

const activeTab = ref('basic')

const basicSettings = ref({
  systemName: '电厂巡检视频监控系统',
  defaultLayout: 4,
  autoRefresh: true,
  refreshInterval: 10,
})

const videoSettings = ref({
  defaultResolution: '720p',
  defaultFps: 25,
  defaultBitrate: 2000,
})

const recordingSettings = ref<RecordingConfig>({
  enabled: false,
  record_path: 'server/recordings/%path/%Y-%m-%d_%H-%M-%S',
  record_format: 'fmp4',
  part_duration: '1h',
  segment_duration: '1h',
  delete_after: '168h'
})

const recordingLoading = ref(false)
const toggleLoading = ref(false)
const saveLoading = ref(false)

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

const getRoleText = (role?: string) => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    operator: '操作员',
    viewer: '观察员',
  }
  return role ? roleMap[role] || role : '-'
}

// 加载录像配置
const loadRecordingConfig = async () => {
  try {
    recordingLoading.value = true
    const response = await getRecordingConfig()
    recordingSettings.value = response.data || response as any
  } catch (error) {
    console.error('加载录像配置失败:', error)
    ElMessage.error('加载录像配置失败')
  } finally {
    recordingLoading.value = false
  }
}

// 保存录像配置
const saveRecordingConfig = async () => {
  try {
    saveLoading.value = true
    await updateRecordingConfig(recordingSettings.value)
    ElMessage.success('录像配置已保存，请重启MediaMTX使配置生效')
  } catch (error) {
    console.error('保存录像配置失败:', error)
    ElMessage.error('保存录像配置失败')
  } finally {
    saveLoading.value = false
  }
}

// 切换录像开关
const handleRecordingToggle = async (enabled: boolean) => {
  try {
    toggleLoading.value = true
    await toggleRecording(enabled)
    ElMessage.success(`录像功能已${enabled ? '启用' : '禁用'}，请重启MediaMTX使配置生效`)
  } catch (error) {
    console.error('切换录像功能失败:', error)
    ElMessage.error('切换录像功能失败')
    // 恢复开关状态
    recordingSettings.value.enabled = !enabled
  } finally {
    toggleLoading.value = false
  }
}

const saveSettings = () => {
  // TODO: 保存设置到后端
  ElMessage.success('设置已保存')
}

const resetSettings = () => {
  basicSettings.value = {
    systemName: '电厂巡检视频监控系统',
    defaultLayout: 4,
    autoRefresh: true,
    refreshInterval: 10,
  }
  videoSettings.value = {
    defaultResolution: '720p',
    defaultFps: 25,
    defaultBitrate: 2000,
  }
  ElMessage.info('设置已重置')
}

onMounted(() => {
  loadRecordingConfig()
})
</script>

<style scoped>
.settings-page {
  height: 100%;
}

.action-buttons {
  margin-top: 30px;
  text-align: right;
}
</style>

