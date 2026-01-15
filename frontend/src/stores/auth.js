import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isLoggedIn = computed(() => !!token.value && !!user.value)

  // 登录
  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/v1/login/', {
        username,
        password
      })

      const { access: newToken, username: usernameData, email: emailData } = response.data
      
      token.value = newToken
      user.value = { username: usernameData, email: emailData }
      
      localStorage.setItem('token', newToken)
      localStorage.setItem('user', JSON.stringify({ username: usernameData, email: emailData }))
      
      axios.defaults.headers.Authorization = `Bearer ${newToken}`
      
      ElMessage({
        message: '登录成功',
        type: 'success'
      })
      
      return true
    } catch (error) {
      ElMessage({
        message: error.response?.data?.error || '登录失败',
        type: 'error'
      })
      return false
    }
  }

  // 注册
  const register = async (username, email, password) => {
    try {
      const response = await axios.post('/api/v1/register/', {
        username,
        email,
        password
      })

      ElMessage({
        message: '注册成功',
        type: 'success'
      })

      return true
    } catch (error) {
      ElMessage({
        message: error.response?.data?.error || '注册失败',
        type: 'error'
      })
      return false
    }
  }

  // 登出
  const logout = () => {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete axios.defaults.headers.Authorization

      ElMessage({
        message: '已退出登录',
        type: 'success'
      })
    }).catch(() => {})
  }

  // 检查登录状态
  const checkAuth = async () => {
    if (!token.value) {
      return false
    }

    try {
      // 这里可以添加检查用户信息的API
      return true
    } catch (error) {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete axios.defaults.headers.Authorization
      return false
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    register,
    logout,
    checkAuth
  }
}, {
  persist: true
})