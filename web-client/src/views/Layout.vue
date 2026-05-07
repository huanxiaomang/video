<template>
  <div class="layout-container">
    <el-container>
      <!-- 侧边栏 (桌面端) -->
      <el-aside v-if="!isMobile" width="200px">
        <div class="logo">
          <h2>{{ configStore.settings.systemName }}</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
        >
          <el-menu-item index="/monitor">
            <el-icon><VideoCamera /></el-icon>
            <span>实时监控</span>
          </el-menu-item>
          <el-menu-item index="/devices">
            <el-icon><Monitor /></el-icon>
            <span>设备管理</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header>
          <div class="header-content">
            <!-- 移动端侧边栏开关 -->
            <el-button v-if="isMobile" :icon="Expand" @click="toggleDrawer" class="menu-toggle-button"></el-button>
            <div class="breadcrumb">
              <span>{{ currentPageTitle }}</span>
            </div>
            <div class="user-info">
              <el-dropdown @command="handleCommand">
                <span class="user-name">
                  <el-icon><User /></el-icon>
                  {{ userStore.userInfo?.username }}
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>

        <!-- 内容区 -->
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <!-- 移动端侧边栏 (抽屉) -->
    <el-drawer
      v-model="isDrawerOpen"
      direction="ltr"
      :with-header="false"
      size="200px"
      v-if="isMobile"
    >
      <div class="logo">
        <h2>{{ configStore.settings.systemName }}</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        @select="isDrawerOpen = false"
      >
        <el-menu-item index="/monitor">
          <el-icon><VideoCamera /></el-icon>
          <span>实时监控</span>
        </el-menu-item>
        <el-menu-item index="/devices">
          <el-icon><Monitor /></el-icon>
          <span>设备管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useConfigStore } from '@/stores/config'
import { ElMessageBox } from 'element-plus'
import { Expand } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const configStore = useConfigStore()

const isDrawerOpen = ref(false)
const isMobile = ref(window.innerWidth < 768) // 假设 768px 是移动端断点

const toggleDrawer = () => {
  isDrawerOpen.value = !isDrawerOpen.value
}

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const activeMenu = computed(() => route.path)
const currentPageTitle = computed(() => route.meta.title as string || '')

const handleCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
      await userStore.logout()
      router.push('/login')
    } catch {
      // 用户取消
    }
  }
}
</script>

<style scoped>
.layout-container {
  width: 100%;
  height: 100%;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4a;
}

.logo h2 {
  font-size: 16px;
  color: #fff;
  margin: 0;
}

.el-menu {
  border-right: none;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}

.header-content {
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.breadcrumb {
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-name {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  color: #606266;
}

.user-name:hover {
  color: #409eff;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}

/* 移动端适配 */
@media (max-width: 767px) {
  .el-aside {
    display: none; /* 移动端隐藏侧边栏 */
  }

  .header-content {
    justify-content: flex-start; /* 移动端头部内容左对齐 */
    gap: 10px; /* 增加元素间距 */
  }

  .breadcrumb {
    font-size: 16px; /* 移动端面包屑字体缩小 */
  }

  .user-info {
    margin-left: auto; /* 用户信息靠右 */
  }

  .el-main {
    padding: 10px; /* 移动端内容区内边距缩小 */
  }

  .menu-toggle-button {
    display: block; /* 移动端显示菜单切换按钮 */
  }
}

/* 桌面端隐藏菜单切换按钮 */
@media (min-width: 768px) {
  .menu-toggle-button {
    display: none;
  }
}
</style>

