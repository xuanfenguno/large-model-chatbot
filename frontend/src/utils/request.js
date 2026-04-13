import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { refreshToken } from '@/stores/auth'

// 创建axios实例（优化超时和配置）
const service = axios.create({
  baseURL: '/api/v1',  // 修改baseURL，指向代理路径
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
      config.headers.Authorization = `Bearer ${token}`
    }

    // 移除可能导致请求取消的AbortController配置
    // 这会导致请求被意外中止
    // if (typeof AbortController !== 'undefined') {
    //   const abortController = new AbortController()
    //   config.signal = abortController.signal
    // }

    // 添加请求时间戳用于性能监控
    config._startTime = Date.now()

    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

export { service }

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// 响应拦截器（优化错误处理和重试机制）
service.interceptors.response.use(
  response => {
    const { data } = response

    // 计算请求耗时
    const duration = Date.now() - response.config._startTime
    console.log(`请求 ${response.config.url} 耗时: ${duration}ms`)

    // 检查响应是否包含错误信息
    if (data.error) {
      ElMessage({
        message: data.error || '请求失败',
        type: 'error'
      })
      return Promise.reject(new Error(data.error || '请求失败'))
    }

    return response
  },
  async error => {
    const originalRequest = error.config

    // 如果请求已经重试过（如 token 刷新后重试），不要显示错误提示
    if (originalRequest?._retry && originalRequest._retryCount === undefined) {
      // 这是刷新 token 后的重试请求，让它自然失败或成功，不显示错误
      return Promise.reject(error)
    }

    // 检查是否是 401 错误且需要刷新 token
    if (error.response?.status === 401 && !originalRequest._retry) {
      // 如果是刷新 token 的请求本身失败，不要再次刷新
      if (originalRequest._isRefreshRequest) {
        console.error('Token 刷新失败，需要重新登录')
        const authStore = useAuthStore()
        authStore.logout()
        ElMessage({
          message: '会话已过期，请重新登录',
          type: 'error',
          duration: 3000
        })
        return Promise.reject(error)
      }

      if (isRefreshing) {
        // 如果正在刷新 token，将请求加入队列等待
        console.log('Token 正在刷新中，将请求加入队列')
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers['Authorization'] = 'Bearer ' + token
            return service(originalRequest)
          })
          .catch(err => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        console.log('开始自动刷新 token...')
        const newAccessToken = await refreshToken()
        processQueue(null, newAccessToken)
        originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken
        
        // 重试原请求
        console.log('Token 刷新成功，重试原请求')
        return service(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        const authStore = useAuthStore()
        authStore.logout()
        ElMessage({
          message: '会话已过期，请重新登录',
          type: 'error',
          duration: 3000
        })
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // 详细的错误信息输出（仅用于非 401 错误，或刷新失败的情况）
    const errorInfo = {
      message: error.message || '未知错误',
      code: error.code,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url,
      method: error.config?.method
    }
    console.error('响应错误详情:', errorInfo)

    // 检查是否是取消请求
    if (axios.isCancel(error)) {
      console.log('请求被取消:', error.message)
      ElMessage({
        message: '请求已取消',
        type: 'warning'
      })
      return Promise.reject(error)
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

    // 请求重试逻辑 (非401错误)
    if (originalRequest && !originalRequest._retry && originalRequest._retryCount < MAX_RETRIES) {
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1
      const delay = Math.min(originalRequest._retryCount * RETRY_DELAY, 5000)
      
      return new Promise((resolve) => {
        setTimeout(() => {
          console.log(`请求重试 (${originalRequest._retryCount}/${MAX_RETRIES})`)
          resolve(service(originalRequest))
        }, delay)
      })
    }

    if (error.response) {
      const { status, data } = error.response

      // 403禁止访问
      if (status === 403) {
        ElMessage({
          message: '您没有权限执行此操作',
          type: 'error'
        })
      }
      // 404未找到
      else if (status === 404) {
        ElMessage({
          message: '请求的资源不存在',
          type: 'error'
        })
      }
      // 服务器错误
      else if (status >= 500) {
        const serverMessage = data?.detail || data?.message || `服务器错误 (${status})`
        ElMessage({
          message: serverMessage,
          type: 'error',
          duration: 5000
        })
      }
      // 其他状态码
      else {
        const errorMsg = data?.detail || data?.message || data?.error || `请求失败 (${status})`
        ElMessage({
          message: errorMsg,
          type: 'error',
          duration: 3000
        })
      }
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
        message: error.message || '请求配置错误',
        type: 'error',
        duration: 3000
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