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
            <el-form-item label="账号操作">
              <el-button type="primary" @click="passwordDialogVisible = true">修改密码</el-button>
              <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 关于 -->
        <el-tab-pane label="关于" name="about">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统名称">
              {{ basicSettings.systemName }}
            </el-descriptions-item>
            <el-descriptions-item label="版本">
              v1.0.0
            </el-descriptions-item>
            <el-descriptions-item label="描述">
              本系统是一个基于 WebRTC 和 RTSP 协议的分布式视频监控解决方案。支持多端设备接入、实时监控、录像回放及设备管理。通过 MediaMTX 媒体服务器实现低延迟流传输，后端采用 FastAPI 构建，前端使用 Vue 3 + Element Plus 提供现代化的用户界面。
            </el-descriptions-item>

          </el-descriptions>
        </el-tab-pane>
      </el-tabs>

      <div class="action-buttons">
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
        <el-button @click="resetSettings">重置</el-button>
      </div>
    </el-card>

    <!-- 修改密码弹窗 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
      @closed="resetPasswordForm"
    >
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPasswordChange">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import { useConfigStore } from '@/stores/config'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { changePassword } from '@/api/auth'

const userStore = useUserStore()
const configStore = useConfigStore()
const router = useRouter()

const activeTab = ref('basic')

// 使用 store 中的设置作为初始值
const basicSettings = ref({ ...configStore.settings })

// 修改密码相关
const passwordDialogVisible = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

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

const loadSettings = () => {
  basicSettings.value = { ...configStore.settings }
}

const saveSettings = () => {
  configStore.saveSettings(basicSettings.value)
  ElMessage.success('设置已保存并同步至系统')
}

const resetSettings = () => {
  configStore.resetSettings()
  basicSettings.value = { ...configStore.settings }
  ElMessage.info('设置已重置')
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      type: 'warning'
    })
    await userStore.logout()
    router.push('/login')
  } catch {
    // 用户取消
  }
}

const resetPasswordForm = () => {
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields()
  }
}

const submitPasswordChange = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await changePassword({
          old_password: passwordForm.oldPassword,
          new_password: passwordForm.newPassword
        })
        ElMessage.success('密码修改成功')
        passwordDialogVisible.value = false
      } catch (error: any) {
        // 错误已经在 request.ts 中拦截处理并提示，这里可以做额外逻辑
        console.error('修改密码失败', error)
      }
    }
  })
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-page {
  padding: 20px;
}

.action-buttons {
  margin-top: 30px;
  text-align: right;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
