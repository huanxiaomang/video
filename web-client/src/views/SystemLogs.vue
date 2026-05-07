<template>
  <div class="logs-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>系统操作日志</span>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索日志..."
              style="width: 200px; margin-right: 10px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="fetchLogs">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredLogs" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="time" label="时间" width="180" sortable />
        <el-table-column prop="user" label="操作人" width="120" />
        <el-table-column prop="module" label="模块" width="120">
          <template #default="{ row }">
            <el-tag :type="getModuleTag(row.module)">{{ row.module }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作内容" />
        <el-table-column prop="ip" label="IP 地址" width="140" />
        <el-table-column prop="status" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '成功' ? 'success' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          background
          layout="prev, pager, next, total"
          :total="totalLogs"
          :page-size="15"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const searchQuery = ref('')
const loading = ref(false)

const logs = ref([
  { time: '2024-03-20 14:30:05', user: 'admin', module: '用户中心', action: '登录系统', ip: '192.168.1.100', status: '成功' },
  { time: '2024-03-20 14:35:12', user: 'admin', module: '设备管理', action: '修改设备 [办公区摄像头] 名称', ip: '192.168.1.100', status: '成功' },
  { time: '2024-03-20 14:40:00', user: 'system', module: '流媒体', action: '启动录像任务: Device_001', ip: '127.0.0.1', status: '成功' },
  { time: '2024-03-20 15:00:22', user: 'admin', module: '系统设置', action: '更改存储策略为 14 天', ip: '192.168.1.100', status: '成功' },
  { time: '2024-03-20 15:10:05', user: 'guest', module: '用户中心', action: '尝试访问未授权页面', ip: '192.168.1.105', status: '失败' },
  { time: '2024-03-20 15:15:30', user: 'system', module: '设备管理', action: '设备 [门口摄像头] 离线报警', ip: '192.168.1.50', status: '成功' },
  { time: '2024-03-20 15:20:10', user: 'admin', module: '录像回放', action: '查看录像: 2024-03-19_10-00-00', ip: '192.168.1.100', status: '成功' },
  { time: '2024-03-20 15:45:18', user: 'admin', module: '设备管理', action: '重置设备 [仓库摄像头] 连接', ip: '192.168.1.100', status: '成功' },
])

const totalLogs = ref(100)

const filteredLogs = computed(() => {
  if (!searchQuery.value) return logs.value
  return logs.value.filter(log => 
    log.action.includes(searchQuery.value) || 
    log.user.includes(searchQuery.value) ||
    log.module.includes(searchQuery.value)
  )
})

const getModuleTag = (module: string) => {
  const map: Record<string, string> = {
    '用户中心': '',
    '设备管理': 'success',
    '流媒体': 'warning',
    '系统设置': 'info',
    '录像回放': 'danger'
  }
  return map[module] || ''
}

const fetchLogs = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 500)
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.logs-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
