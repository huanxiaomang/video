/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/monitor',
    children: [
      {
        path: '/monitor',
        name: 'LiveMonitor',
        component: () => import('@/views/LiveMonitor.vue'),
        meta: { title: '实时监控' },
      },
      {
        path: '/devices',
        name: 'DeviceManagement',
        component: () => import('@/views/DeviceManagement.vue'),
        meta: { title: '设备管理' },
      },
      {
        path: '/playback',
        name: 'PlaybackPage',
        component: () => import('@/views/PlaybackPage.vue'),
        meta: { title: '录像回放' },
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  
  if (to.meta.requiresAuth && !token) {
    // 需要认证但未登录，跳转到登录页
    next('/login')
  } else if (to.path === '/login' && token) {
    // 已登录访问登录页，跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router

