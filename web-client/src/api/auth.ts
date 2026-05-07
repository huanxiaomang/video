/**
 * 认证API
 */
import request from './request'
import type { LoginResponse, User } from '@/types'

/**
 * 用户登录
 */
export function login(username: string, password: string): Promise<LoginResponse> {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)

  return request({
    url: '/api/auth/login',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser(): Promise<User> {
  return request({
    url: '/api/auth/me',
    method: 'get',
  })
}

/**
 * 用户登出
 */
export function logout(): Promise<any> {
  return request({
    url: '/api/auth/logout',
    method: 'post',
  })
}

/**
 * 修改密码
 */
export function changePassword(data: any): Promise<any> {
  return request({
    url: '/api/auth/change-password',
    method: 'post',
    data,
  })
}

