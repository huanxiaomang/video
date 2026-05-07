<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useConfigStore } from '@/stores/config'

const userStore = useUserStore()
const configStore = useConfigStore()
const route = useRoute()

// 更新网页标题
const updateTitle = () => {
  const systemName = configStore.settings.systemName || '视频监控系统'
  const pageTitle = route.meta.title as string
  if (pageTitle) {
    document.title = `${pageTitle} - ${systemName}`
  } else {
    document.title = systemName
  }
}

// 监听路由变化更新标题
watch(() => route.path, updateTitle)

// 监听系统名称变化更新标题
watch(() => configStore.settings.systemName, updateTitle)

onMounted(() => {
  // 初始化用户状态
  userStore.init()
  updateTitle()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
}
</style>

