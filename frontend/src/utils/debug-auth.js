/**
 * 认证调试工具
 * 用于诊断登录跳转问题
 */

import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

class AuthDebugger {
  constructor() {
    this.authStore = useAuthStore()
    this.router = useRouter()
  }

  // 检查认证状态
  checkAuthStatus() {
    const status = {
      localStorage: {
        token: localStorage.getItem('token'),
        user: localStorage.getItem('user')
      },
      authStore: {
        token: this.authStore.token,
        user: this.authStore.user,
        isLoggedIn: this.authStore.isLoggedIn
      },
      computed: {
        isLoggedIn: !!this.authStore.token && !!this.authStore.user
      }
    }
    
    console.log('🔍 认证状态检查:', status)
    return status
  }

  // 测试路由跳转
  async testRouteNavigation(toPath = '/chat') {
    console.log('🚀 测试路由跳转到:', toPath)
    
    try {
      // 检查当前路由
      console.log('📍 当前路由:', this.router.currentRoute.value)
      
      // 尝试跳转
      console.log('🔄 开始跳转...')
      await this.router.push(toPath)
      console.log('✅ 跳转完成')
      
      // 检查跳转后的路由
      console.log('📍 跳转后路由:', this.router.currentRoute.value)
      
      return { success: true }
    } catch (error) {
      console.error('❌ 跳转失败:', error)
      return { success: false, error }
    }
  }

  // 手动设置认证状态
  setAuthManually(token, userData) {
    console.log('🔧 手动设置认证状态...')
    
    if (token) {
      localStorage.setItem('token', token)
      this.authStore.token = token
    }
    
    if (userData) {
      const userStr = JSON.stringify(userData)
      localStorage.setItem('user', userStr)
      this.authStore.user = userData
    }
    
    console.log('✅ 手动设置完成')
    this.checkAuthStatus()
  }

  // 清除认证状态
  clearAuth() {
    console.log('🧹 清除认证状态...')
    
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    this.authStore.token = null
    this.authStore.user = null
    
    console.log('✅ 清除完成')
    this.checkAuthStatus()
  }

  // 运行完整诊断
  async runDiagnosis() {
    console.log('🔬 开始认证诊断...\n')
    
    // 检查当前状态
    const status = this.checkAuthStatus()
    
    // 测试路由跳转
    const navResult = await this.testRouteNavigation('/chat')
    
    // 诊断结果
    const diagnosis = {
      status,
      navigation: navResult,
      issues: []
    }
    
    // 检查问题
    if (!status.localStorage.token) {
      diagnosis.issues.push('localStorage中没有token')
    }
    
    if (!status.authStore.token) {
      diagnosis.issues.push('authStore中没有token')
    }
    
    if (!status.authStore.isLoggedIn) {
      diagnosis.issues.push('isLoggedIn为false')
    }
    
    if (!navResult.success) {
      diagnosis.issues.push('路由跳转失败')
    }
    
    console.log('📊 诊断结果:', diagnosis)
    
    if (diagnosis.issues.length === 0) {
      console.log('🎉 没有发现问题')
    } else {
      console.log('⚠️ 发现以下问题:')
      diagnosis.issues.forEach(issue => console.log('   - ' + issue))
    }
    
    return diagnosis
  }
}

// 导出调试工具
export { AuthDebugger }

// 如果直接在浏览器中运行
if (typeof window !== 'undefined') {
  window.AuthDebugger = AuthDebugger
  
  // 添加全局调试函数
  window.debugAuth = () => {
    const authDebugger = new AuthDebugger()
    return authDebugger.runDiagnosis()
  }
  
  window.checkAuthStatus = () => {
    const authDebugger = new AuthDebugger()
    return authDebugger.checkAuthStatus()
  }
  
  window.testNavigation = (path = '/chat') => {
    const authDebugger = new AuthDebugger()
    return authDebugger.testRouteNavigation(path)
  }
  
  console.log('🔧 认证调试工具已加载')
  console.log('可用命令:')
  console.log('  - debugAuth() - 运行完整诊断')
  console.log('  - checkAuthStatus() - 检查认证状态')
  console.log('  - testNavigation("/path") - 测试路由跳转')
}