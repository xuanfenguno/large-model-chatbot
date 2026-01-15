import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// 创建axios实例（优化超时和配置）
const service = axios.create({
  baseURL: '/api/v1',
  timeout: 60000, // 增加超时时间到60秒，考虑到AI响应可能需要更长时间
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: false
})

// 请求重试配置
const MAX_RETRIES = 2
const RETRY_DELAY = 1000

// 请求拦截器（优化配置和取消请求支持）
service.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }

    // 为每个请求创建取消令牌
    const source = axios.CancelToken.source()
    config.cancelToken = source.token
    config._cancelTokenSource = source

    // 添加请求时间戳用于性能监控
    config._startTime = Date.now()

    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器（优化错误处理和重试机制）
service.interceptors.response.use(
  response => {
    const { data } = response

    // 计算请求耗时
    const duration = Date.now() - response.config._startTime
    console.log(`请求 ${response.config.url} 耗时: ${duration}ms`)

    // 如果响应包含状态码，检查是否成功
    if (data.code && data.code !== 200) {
      ElMessage({
        message: data.message || '请求失败',
        type: 'error'
      })
      return Promise.reject(new Error(data.message || '请求失败'))
    }

    return data
  },
  error => {
    console.error('响应错误:', error)

    // 检查是否是取消请求
    if (axios.isCancel(error)) {
      console.log('请求被取消:', error.message)
      return Promise.reject(error)
    }

    // 请求重试逻辑
    if (error.config && error.config._retryCount < MAX_RETRIES) {
      error.config._retryCount = (error.config._retryCount || 0) + 1
      const delay = Math.min(error.config._retryCount * RETRY_DELAY, 5000)
      
      return new Promise((resolve) => {
        setTimeout(() => {
          console.log(`请求重试 (${error.config._retryCount}/${MAX_RETRIES})`)
          resolve(service(error.config))
        }, delay)
      })
    }

    // 网络超时处理
    if (error.code === 'ECONNABORTED') {
      ElMessage({
        message: '请求超时，请检查网络或重试',
        type: 'error',
        duration: 5000
      })
      return Promise.reject(error)
    }

    if (error.response) {
      const { status, data } = error.response

      // 401未授权，清除token并跳转登录
      if (status === 401) {
        const authStore = useAuthStore()
        authStore.logout()
        
        ElMessage({
          message: '登录已过期，请重新登录',
          type: 'error'
        })
        
        return Promise.reject(error)
      }

      // 403禁止访问
      if (status === 403) {
        ElMessage({
          message: '您没有权限执行此操作',
          type: 'error'
        })
        return Promise.reject(error)
      }

      // 404未找到
      if (status === 404) {
        ElMessage({
          message: '请求的资源不存在',
          type: 'error'
        })
        return Promise.reject(error)
      }

      // 服务器错误
      if (status >= 500) {
        ElMessage({
          message: '服务器内部错误',
          type: 'error',
          duration: 5000
        })
        return Promise.reject(error)
      }

      // 其他状态码
      ElMessage({
        message: data?.detail || data?.message || '请求失败',
        type: 'error'
      })
    } else if (error.request) {
      // 网络错误
      ElMessage({
        message: '网络连接失败，请检查网络设置',
        type: 'error',
        duration: 5000
      })
    } else {
      // 请求配置错误
      ElMessage({
        message: error.message,
        type: 'error'
      })
    }

    return Promise.reject(error)
  }
)

// 导出取消请求方法
export const cancelRequest = (config, message = '请求被取消') => {
  if (config && config._cancelTokenSource) {
    config._cancelTokenSource.cancel(message)
  }
}

export default service