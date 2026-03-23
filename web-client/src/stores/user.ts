/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'
import { login as loginApi, getCurrentUser, logout as logoutApi } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<User | null>(null)
  const token = ref<string>('')
  const isLoggedIn = ref<boolean>(false)

  /**
   * 登录
   */
  async function login(username: string, password: string) {
    try {
      const response = await loginApi(username, password)
      token.value = response.access_token
      localStorage.setItem('access_token', response.access_token)
      
      // 获取用户信息
      await fetchUserInfo()
      
      isLoggedIn.value = true
      ElMessage.success('登录成功')
      
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  /**
   * 获取用户信息
   */
  async function fetchUserInfo() {
    try {
      const user = await getCurrentUser()
      userInfo.value = user
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  /**
   * 登出
   */
  async function logout() {
    try {
      await logoutApi()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      userInfo.value = null
      token.value = ''
      isLoggedIn.value = false
      localStorage.removeItem('access_token')
      ElMessage.success('已登出')
    }
  }

  /**
   * 初始化（从localStorage恢复登录状态）
   */
  async function init() {
    const savedToken = localStorage.getItem('access_token')
    if (savedToken) {
      token.value = savedToken
      await fetchUserInfo()
      if (userInfo.value) {
        isLoggedIn.value = true
      }
    }
  }

  return {
    userInfo,
    token,
    isLoggedIn,
    login,
    logout,
    fetchUserInfo,
    init,
  }
})

