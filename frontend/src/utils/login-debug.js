/**
 * 登录问题诊断工具
 * 用于诊断登录成功但显示错误的问题
 */

import { useAuthStore } from '@/stores/auth'
import service from '@/utils/request'

class LoginDebugger {
  constructor() {
    this.authStore = useAuthStore()
  }

  // 模拟登录请求
  async simulateLogin(username = 'test', password = 'test') {
    console.log('🔧 开始模拟登录请求...')
    
    try {
      // 清除之前的认证状态
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      const requestData = { username, password }
      console.log('📤 发送登录请求:', requestData)
      
      const response = await service.post('/v1/login/', requestData, {
        timeout: 30000,
        _isLoginRequest: true
      })
      
      console.log('📥 收到登录响应:', response)
      console.log('📊 响应状态:', response.status)
      console.log('📋 响应数据:', response.data)
      
      // 分析响应数据格式
      this.analyzeResponse(response.data)
      
      return { success: true, response }
      
    } catch (error) {
      console.error('❌ 登录请求失败:', error)
      console.error('📊 错误状态:', error.response?.status)
      console.error('📋 错误数据:', error.response?.data)
      console.error('🔍 错误信息:', error.message)
      
      return { success: false, error }
    }
  }

  // 分析响应数据格式
  analyzeResponse(responseData) {
    console.log('🔍 分析响应数据格式...')
    
    if (!responseData) {
      console.error('❌ 响应数据为空')
      return
    }
    
    // 检查可能的字段
    const fields = {
      'access': responseData.access,
      'token': responseData.token,
      'username': responseData.username,
      'email': responseData.email,
      'user.username': responseData.user?.username,
      'user.email': responseData.user?.email,
      'data.access': responseData.data?.access,
      'data.token': responseData.data?.token,
      'data.username': responseData.data?.username
    }
    
    console.log('📋 响应字段分析:')
    Object.entries(fields).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        console.log(`   ${key}: ${value}`)
      }
    })
    
    // 检查必需字段
    const hasToken = responseData.access || responseData.token
    const hasUsername = responseData.username || responseData.user?.username
    
    console.log('🔑 必需字段检查:')
    console.log(`   token字段: ${hasToken ? '✅ 存在' : '❌ 缺失'}`)
    console.log(`   username字段: ${hasUsername ? '✅ 存在' : '❌ 缺失'}`)
    
    if (!hasToken || !hasUsername) {
      console.error('❌ 响应缺少必需字段')
    }
  }

  // 测试认证状态同步
  async testAuthSync() {
    console.log('🔄 测试认证状态同步...')
    
    // 模拟登录成功后的状态
    const testToken = 'test-token-12345'
    const testUser = { username: 'testuser', email: 'test@example.com' }
    
    // 设置localStorage
    localStorage.setItem('token', testToken)
    localStorage.setItem('user', JSON.stringify(testUser))
    
    console.log('📝 设置localStorage状态:')
    console.log('   token:', localStorage.getItem('token'))
    console.log('   user:', localStorage.getItem('user'))
    
    // 检查store状态
    console.log('🏪 检查store状态:')
    console.log('   token:', this.authStore.token)
    console.log('   user:', this.authStore.user)
    console.log('   isLoggedIn:', this.authStore.isLoggedIn)
    
    // 强制同步
    if (!this.authStore.token && localStorage.getItem('token')) {
      this.authStore.token = localStorage.getItem('token')
      this.authStore.user = JSON.parse(localStorage.getItem('user') || 'null')
      console.log('🔄 已强制同步状态')
    }
    
    console.log('🔄 同步后store状态:')
    console.log('   token:', this.authStore.token)
    console.log('   user:', this.authStore.user)
    console.log('   isLoggedIn:', this.authStore.isLoggedIn)
  }

  // 运行完整诊断
  async runDiagnosis(username = 'test', password = 'test') {
    console.log('🔬 开始登录问题诊断...\n')
    
    // 1. 测试登录请求
    console.log('1. 测试登录请求')
    const loginResult = await this.simulateLogin(username, password)
    
    // 2. 测试认证状态同步
    console.log('\n2. 测试认证状态同步')
    await this.testAuthSync()
    
    // 3. 检查当前认证状态
    console.log('\n3. 检查当前认证状态')
    const currentStatus = {
      localStorage: {
        token: localStorage.getItem('token'),
        user: localStorage.getItem('user')
      },
      authStore: {
        token: this.authStore.token,
        user: this.authStore.user,
        isLoggedIn: this.authStore.isLoggedIn
      }
    }
    console.log('📊 当前认证状态:', currentStatus)
    
    // 诊断结果
    const diagnosis = {
      loginSuccess: loginResult.success,
      authSync: !!this.authStore.token && !!localStorage.getItem('token'),
      issues: []
    }
    
    if (!loginResult.success) {
      diagnosis.issues.push('登录请求失败')
    }
    
    if (!diagnosis.authSync) {
      diagnosis.issues.push('认证状态同步失败')
    }
    
    console.log('\n📊 诊断结果:', diagnosis)
    
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
export { LoginDebugger }

// 如果直接在浏览器中运行
if (typeof window !== 'undefined') {
  window.LoginDebugger = LoginDebugger
  
  // 添加全局调试函数
  window.debugLogin = (username, password) => {
    const loginDebugger = new LoginDebugger()
    return loginDebugger.runDiagnosis(username, password)
  }
  
  window.testLoginRequest = (username, password) => {
    const loginDebugger = new LoginDebugger()
    return loginDebugger.simulateLogin(username, password)
  }
  
  window.testAuthSync = () => {
    const loginDebugger = new LoginDebugger()
    return loginDebugger.testAuthSync()
  }
  
  console.log('🔧 登录调试工具已加载')
  console.log('可用命令:')
  console.log('  - debugLogin("用户名", "密码") - 运行完整诊断')
  console.log('  - testLoginRequest("用户名", "密码") - 测试登录请求')
  console.log('  - testAuthSync() - 测试认证状态同步')
}