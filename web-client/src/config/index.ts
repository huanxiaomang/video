/**
 * 应用配置
 * 支持开发环境和生产环境
 */

// 获取当前主机地址（用于局域网访问）
const getHostAddress = (): string => {
  // 在开发环境，使用 localhost
  // 在生产环境或需要局域网访问时，使用实际的IP地址
  if (import.meta.env.DEV) {
    return window.location.hostname
  }
  return window.location.hostname
}

const host = getHostAddress()

export const config = {
  // API服务器地址
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || `http://${host}:8000`,
  
  // MediaMTX WebRTC地址
  webrtcBaseUrl: import.meta.env.VITE_WEBRTC_BASE_URL || `http://${host}:8889`,
  
  // MediaMTX RTSP地址
  rtspBaseUrl: import.meta.env.VITE_RTSP_BASE_URL || `rtsp://${host}:8554`,
}

export default config

