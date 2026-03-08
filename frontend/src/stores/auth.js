import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import service from '@/utils/request'

// 导出refreshToken函数供其他模块使用
export let refreshToken = null

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const storedUser = localStorage.getItem('user')
const user = ref(storedUser ? JSON.parse(storedUser) : null)
  const isLoggedIn = computed(() => {
    const result = !!token.value && !!user.value
    console.log('isLoggedIn计算:', { token: !!token.value, user: !!user.value, result })
    return result
  })
  
  const accessToken = computed(() => token.value)
  
  // 获取用户信息（包含头像）
  const fetchUserInfo = async () => {
    if (!token.value) {
      console.error('没有有效的token，无法获取用户信息')
      return
    }
    
    try {
      const response = await service.get('/user-info/', {
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })
      
      if (response.data) {
        // 更新用户信息，包括头像
        user.value = {
          ...user.value,
          ...response.data
        }
        
        // 保存到localStorage
        localStorage.setItem('user', JSON.stringify(user.value))
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 即使获取失败也不抛出错误，因为这不是关键操作
    }
  }

  const login = async (username, password) => {
    try {
      // 彻底清理所有可能的token存储
      delete service.defaults.headers.Authorization
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      token.value = null
      user.value = null
      
      console.log('开始登录请求，用户名:', username, '密码长度:', password.length)
      
      const requestData = {
        username,
        password
      }
      
      console.log('请求数据:', requestData)
      console.log('请求路径:', '/login/')
      console.log('service baseURL:', service.defaults.baseURL)
      
      const response = await service.post('/login/', requestData, {
          timeout: 30000,
          _isLoginRequest: true
        })
      console.log('收到响应:', response)

      console.log('登录完整响应:', response)
      console.log('登录响应状态:', response.status)
      console.log('登录响应数据:', response.data)
      
      const responseData = response.data
      
      if (!responseData) {
        console.error('响应数据为空，可能是API路径或CORS问题')
        throw new Error('API响应数据为空')
      }
      
      // 更健壮的数据解析，支持多种响应格式
      const newToken = responseData.access;

      if (!newToken || !responseData.user) {
        console.error('登录响应缺少必需字段，完整响应:', responseData)
        throw new Error('登录响应缺少必需字段')
      }

      token.value = newToken
      user.value = responseData.user // 直接使用登录响应中的完整用户信息

      localStorage.setItem('token', newToken)
      localStorage.setItem('user', JSON.stringify(responseData.user))
      // 检查并存储refresh token
      if (responseData.refresh) {
        localStorage.setItem('refreshToken', responseData.refresh)
      }

      service.defaults.headers.Authorization = `Bearer ${newToken}`

      console.log('登录成功，token已保存:', newToken)
      console.log('用户信息已保存:', responseData.user)
      console.log('当前认证状态:', isLoggedIn.value)

      return true
    } catch (error) {
      console.error('登录错误详情:', error)
      console.error('错误响应状态:', error.response?.status)
      console.error('错误响应数据:', error.response?.data)
      console.error('错误响应头:', error.response?.headers)
      ElMessage({
        message: error.response?.data?.error || error.message || '登录失败',
        type: 'error'
      })
      return false
    }
  }

  const register = async (username, email, password, confirmPassword) => {
    try {
      const response = await service.post('/register/', {
        username,
        email,
        password,
        confirm_password: confirmPassword
      }, {
        timeout: 30000
      })
      
      console.log('注册响应:', response)
      console.log('注册响应数据:', response.data)
      
      const responseData = response.data
      
      if (response && responseData) {
        ElMessage({
          message: '注册成功',
          type: 'success'
        })
        return true
      }
      
      return false
    } catch (error) {
      console.error('注册错误:', error)
      console.error('注册错误响应状态:', error.response?.status)
      console.error('注册错误数据:', error.response?.data)
      
      // 根据后端返回的具体错误信息显示不同的提示
      const errorMessage = error.response?.data?.error || error.message || '注册失败'
      
      // 处理重复注册的错误信息
      if (error.response?.status === 400) {
        if (errorMessage.includes('Username already exists')) {
          ElMessage.warning('该用户名已被注册，请使用其他用户名')
        } else if (errorMessage.includes('Email already exists')) {
          ElMessage.warning('该邮箱已被注册，请使用其他邮箱')
        } else {
          ElMessage.error(errorMessage)
        }
      } else {
        ElMessage.error(errorMessage)
      }
      
      return false
    }
  }

  const logout = () => {
    token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user') // 新增：移除用户信息 // 确保也清除refresh token
    localStorage.removeItem('user')
    delete service.defaults.headers.Authorization
    
    ElMessage({
      message: '已退出登录',
      type: 'success'
    })
  }

  // 刷新token
  const refreshTokenFn = async () => {
    const refreshToken = localStorage.getItem('refreshToken')
    if (!refreshToken) {
      console.error('没有可用的refresh token，无法刷新')
      // 在这里可以选择登出用户
      logout()
      throw new Error('No refresh token available.')
    }

    try {
      console.log('开始使用refresh token刷新access token...')
      
      // 调用后端刷新接口 - 使用正确的API路径
      const response = await service.post('/token/refresh/', {
        refresh: refreshToken
      }, {
        timeout: 10000,
        _isRefreshRequest: true
      })
      
      const responseData = response.data
      let newToken
      
      // 解析新的token
      if (responseData.access) {
        newToken = responseData.access
      } else if (responseData.token) {
        newToken = responseData.token
      } else if (responseData.data) {
        newToken = responseData.data.access || responseData.data.token
      }
      
      if (!newToken) {
        throw new Error('刷新token失败：响应中缺少token')
      }
      
      // 更新token
      token.value = newToken
      localStorage.setItem('token', newToken)
      service.defaults.headers.Authorization = `Bearer ${newToken}`
      
      console.log('token刷新成功')
      return newToken
      
    } catch (error) {
      console.error('刷新token失败:', error)
      throw error
    }
  }

  // 将refreshToken函数赋值给导出的变量
  refreshToken = refreshTokenFn

  return {
    token,
    user,
    isLoggedIn,
    login,
    register,
    logout,
    fetchUserInfo,
    refreshToken: refreshTokenFn
  }
})