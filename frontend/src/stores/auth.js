import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import service from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isLoggedIn = computed(() => {
    const result = !!token.value && !!user.value
    console.log('isLoggedIn计算:', { token: !!token.value, user: !!user.value, result })
    return result
  })

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
      console.log('请求路径:', '/api/v1/login/')
      console.log('service baseURL:', service.defaults.baseURL)
      
      const response = await service.post('/api/v1/login/', requestData, {
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
      
      const { access: newToken, username: usernameData, email: emailData } = responseData

      if (!newToken || !usernameData) {
        console.error('登录响应缺少必需字段:', responseData)
        throw new Error('登录响应缺少必需字段')
      }

      token.value = newToken
      user.value = { username: usernameData, email: emailData || '' }

      localStorage.setItem('token', newToken)
      localStorage.setItem('user', JSON.stringify({ username: usernameData, email: emailData || '' }))

      service.defaults.headers.Authorization = `Bearer ${newToken}`

      console.log('登录成功，token已保存:', newToken)
      console.log('用户信息已保存:', { username: usernameData, email: emailData || '' })
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

  const register = async (username, email, password) => {
    try {
      const response = await service.post('/api/v1/register/', {
        username,
        password,
        email
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
      console.error('注册错误响应:', error.response)
      console.error('注册错误数据:', error.response?.data)
      ElMessage({
        message: error.response?.data?.error || error.message || '注册失败',
        type: 'error'
      })
      return false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.Authorization
    
    ElMessage({
      message: '已退出登录',
      type: 'success'
    })
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    register,
    logout
  }
})