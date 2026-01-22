<template>
  <div class="login-container">
    <div class="login-card">
      <!-- 机器人Logo - 正上方居中 -->
      <div class="logo-container-center-top">
        <div class="robot-logo-login">🤖</div>
      </div>
      <!-- 登录/注册切换按钮 -->
      <div class="form-switcher">
        <button 
          :class="['switch-btn', { active: !isRegisterForm }]"
          @click="switchToLogin"
        >
          登录
        </button>
        <button 
          :class="['switch-btn', { active: isRegisterForm }]"
          @click="switchToRegister"
        >
          注册
        </button>
      </div>

      <!-- 表单内容 -->
      <div class="form-content">
        <!-- 登录表单 -->
        <transition name="slide" mode="out-in">
          <div v-if="!isRegisterForm" class="form-wrapper">
            <div class="form-header">
              <h1 class="form-title">欢迎回来</h1>
              <p class="form-subtitle">探索无限可能，开启智能对话</p>
            </div>

            <el-form
              ref="loginFormRef"
              :model="loginForm"
              :rules="loginRules"
              class="login-form"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="用户名"
                  prefix-icon="User"
                  size="large"
                  :clearable="true"
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="密码"
                  prefix-icon="Lock"
                  size="large"
                  show-password
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  class="submit-btn"
                  :loading="isLoading"
                  @click="handleLogin"
                >
                  <template #loading>
                    <span class="loading-text">登录中...</span>
                  </template>
                  <span class="btn-text">登录</span>
                </el-button>
              </el-form-item>

              <div class="form-footer">
                <el-link type="info" :underline="false" @click="goToForgotPassword">忘记密码？</el-link>
              </div>
            </el-form>
          </div>

          <!-- 注册表单 -->
          <div v-else class="form-wrapper">
            <div class="form-header">
              <h1 class="form-title">创建账户</h1>
              <p class="form-subtitle">开启您的智能对话之旅</p>
            </div>

            <el-form
              ref="registerFormRef"
              :model="registerForm"
              :rules="registerRules"
              class="register-form"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="用户名"
                  prefix-icon="User"
                  size="large"
                  :clearable="true"
                />
              </el-form-item>

              <el-form-item prop="email">
                <el-input
                  v-model="registerForm.email"
                  type="email"
                  placeholder="邮箱"
                  prefix-icon="Message"
                  size="large"
                  :clearable="true"
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="密码"
                  prefix-icon="Lock"
                  size="large"
                  show-password
                />
              </el-form-item>

              <el-form-item prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="确认密码"
                  prefix-icon="Lock"
                  size="large"
                  show-password
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  class="submit-btn"
                  :loading="isLoading"
                  @click="handleRegister"
                >
                  <template #loading>
                    <span class="loading-text">注册中...</span>
                  </template>
                  <span class="btn-text">注册</span>
                </el-button>
              </el-form-item>

              <div class="form-footer">
                <el-checkbox v-model="agreeTerms" class="terms-checkbox">
                  我同意 <span class="link-text" @click="openUserAgreement">用户协议</span> 和 <span class="link-text" @click="openPrivacyPolicy">隐私政策</span>
                </el-checkbox>
              </div>
            </el-form>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElLoading } from 'element-plus'
import { ChatDotRound, ChatDotSquare, Platform } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isLoading = ref(false)
const isRegisterForm = ref(false)
const agreeTerms = ref(false)

const loginFormRef = ref(null)
const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ]
})

const registerFormRef = ref(null)
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const registerRules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
})

// 切换到登录表单
const switchToLogin = () => {
  isRegisterForm.value = false
  // 清空之前的查询参数
  router.replace({ path: '/login', query: {} })
}

// 切换到注册表单
const switchToRegister = () => {
  isRegisterForm.value = true
  // 设置查询参数以记住选项卡状态
  router.replace({ path: '/login', query: { tab: 'register' } })
}

// 处理登录
const handleLogin = async () => {
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        isLoading.value = true
        console.log('开始登录，用户名:', loginForm.username)
        
        // 清除之前的认证状态
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        
        const success = await authStore.login(loginForm.username, loginForm.password)
        console.log('登录结果:', success)
        
        if (success) {
          console.log('登录成功，准备跳转...')
          ElMessage.success('登录成功')
          
          // 立即检查认证状态
          console.log('跳转前认证状态检查:', {
            token: authStore.token,
            user: authStore.user,
            isLoggedIn: authStore.isLoggedIn,
            localStorageToken: localStorage.getItem('token'),
            localStorageUser: localStorage.getItem('user')
          })
          
          console.log('开始跳转到聊天界面...')
          
          // 确保认证状态已更新后再跳转
          await new Promise(resolve => setTimeout(resolve, 100))
          
          console.log('执行跳转前再次检查认证状态:', {
            token: authStore.token,
            user: authStore.user,
            isLoggedIn: authStore.isLoggedIn,
            localStorageToken: localStorage.getItem('token'),
            localStorageUser: localStorage.getItem('user')
          })
          
          // 强制刷新认证状态
          if (!authStore.token && localStorage.getItem('token')) {
            authStore.token = localStorage.getItem('token')
            authStore.user = JSON.parse(localStorage.getItem('user') || 'null')
            console.log('已从localStorage强制恢复认证状态')
          }
          
          console.log('执行跳转')
          
          // 分离跳转逻辑，避免影响登录成功状态
          try {
            await router.push('/chat')
            console.log('跳转完成')
          } catch (jumpError) {
            console.error('跳转错误（不影响登录成功）:', jumpError)
            // 跳转失败不影响登录成功状态，可以手动导航
            window.location.href = '/chat'
          }
        } else {
          console.log('登录失败')
          ElMessage.error('登录失败，请检查用户名和密码')
        }
      } catch (error) {
        console.error('登录错误:', error)
        ElMessage.error('登录失败，请稍后重试')
      } finally {
        isLoading.value = false
      }
    }
  })
}

// 处理注册
const handleRegister = async () => {
  if (!agreeTerms.value) {
    ElMessage.warning('请先同意用户协议和隐私政策')
    return
  }

  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        isLoading.value = true
        const success = await authStore.register(
          registerForm.username,
          registerForm.email,
          registerForm.password
        )
        if (success) {
          ElMessage.success('注册成功')
          // 自动切换到登录表单
          isRegisterForm.value = false
          router.replace({ path: '/login', query: { tab: 'login' } })
        } else {
          ElMessage.error('注册失败，请稍后重试')
        }
      } catch (error) {
        console.error('注册错误:', error)
        ElMessage.error('注册失败，请稍后重试')
      } finally {
        isLoading.value = false
      }
    }
  })
}

// 处理微信登录
const handleWechatLogin = async () => {
  try {
    // 显示加载状态
    const loading = ElLoading.service({
      lock: true,
      text: '正在获取微信授权...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    // 调用后端API获取微信授权URL
    const response = await axios.get('/api/v1/auth/wechat/')
    const authUrl = response.data.auth_url
    const testMode = response.data.test_mode
    
    // 关闭加载提示
    loading.close()
    
    // 检查是否为测试模式
    if (testMode) {
      // 测试模式：直接调用回调处理函数
      await handleWechatCallbackTest(authUrl)
    } else {
      // 真实模式：跳转到微信授权页面
      window.location.href = authUrl
    }
    
  } catch (error) {
    console.error('微信登录错误:', error)
    ElMessage.error('微信登录失败，请稍后重试')
  }
}

// 处理QQ登录
const handleQQLogin = async () => {
  try {
    // 显示加载状态
    const loading = ElLoading.service({
      lock: true,
      text: '正在获取QQ授权...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    // 调用后端API获取QQ授权URL
    const response = await axios.get('/api/v1/auth/qq/')
    const authUrl = response.data.auth_url
    const testMode = response.data.test_mode
    
    // 关闭加载提示
    loading.close()
    
    // 检查是否为测试模式
    if (testMode) {
      // 测试模式：直接调用回调处理函数
      await handleQQCallbackTest(authUrl)
    } else {
      // 真实模式：跳转到QQ授权页面
      window.location.href = authUrl
    }
    
  } catch (error) {
    console.error('QQ登录错误:', error)
    ElMessage.error('QQ登录失败，请稍后重试')
  }
}

// 处理GitHub登录
const handleGithubLogin = async () => {
  try {
    // 显示加载状态
    const loading = ElLoading.service({
      lock: true,
      text: '正在获取GitHub授权...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    // 调用后端API获取GitHub授权URL
    const response = await axios.get('/api/v1/auth/github/')
    const authUrl = response.data.auth_url
    const testMode = response.data.test_mode
    
    // 关闭加载提示
    loading.close()
    
    // 检查是否为测试模式
    if (testMode) {
      // 测试模式：直接调用回调处理函数
      await handleGithubCallbackTest(authUrl)
    } else {
      // 真实模式：跳转到GitHub授权页面
      window.location.href = authUrl
    }
    
  } catch (error) {
    console.error('GitHub登录错误:', error)
    ElMessage.error('GitHub登录失败，请稍后重试')
  }
}

// 处理微信登录回调
const handleWechatCallback = async () => {
  // 检查URL中是否有微信回调参数
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const state = urlParams.get('state')
  
  if (code && state) {
    try {
      const loading = ElLoading.service({
        lock: true,
        text: '正在处理微信登录...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      
      // 调用后端处理微信回调
      const response = await axios.get(`/api/v1/auth/wechat/callback/?code=${code}&state=${state}`)
      const { access: token, username, nickname, avatar, provider } = response.data
      
      // 保存用户信息和token
      authStore.token = token
      authStore.user = { username, email: username, nickname, avatar, provider }
      
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify({ username, email: username, nickname, avatar, provider }))
      
      axios.defaults.headers.Authorization = `Bearer ${token}`
      
      loading.close()
      
      ElMessage.success(`微信登录成功！欢迎 ${nickname}`)
      router.push('/')
      
    } catch (error) {
      console.error('微信登录回调错误:', error)
      ElMessage.error('微信登录失败，请稍后重试')
    }
  }
}

// 处理QQ登录回调
const handleQQCallback = async () => {
  // 检查URL中是否有QQ回调参数
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const state = urlParams.get('state')
  
  if (code && state) {
    try {
      const loading = ElLoading.service({
        lock: true,
        text: '正在处理QQ登录...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      
      // 调用后端处理QQ回调
      const response = await axios.get(`/api/v1/auth/qq/callback/?code=${code}&state=${state}`)
      const { access: token, username, nickname, avatar, provider } = response.data
      
      // 保存用户信息和token
      authStore.token = token
      authStore.user = { username, email: username, nickname, avatar, provider }
      
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify({ username, email: username, nickname, avatar, provider }))
      
      axios.defaults.headers.Authorization = `Bearer ${token}`
      
      loading.close()
      
      ElMessage.success(`QQ登录成功！欢迎 ${nickname}`)
      router.push('/')
      
    } catch (error) {
      console.error('QQ登录回调错误:', error)
      ElMessage.error('QQ登录失败，请稍后重试')
    }
  }
}

// 处理GitHub登录回调
const handleGithubCallback = async () => {
  // 检查URL中是否有GitHub回调参数
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const state = urlParams.get('state')
  
  if (code && state) {
    try {
      const loading = ElLoading.service({
        lock: true,
        text: '正在处理GitHub登录...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      
      // 调用后端处理GitHub回调
      const response = await axios.get(`/api/v1/auth/github/callback/?code=${code}&state=${state}`)
      const { access: token, username, nickname, avatar, provider } = response.data
      
      // 保存用户信息和token
      authStore.token = token
      authStore.user = { username, email: username, nickname, avatar, provider }
      
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify({ username, email: username, nickname, avatar, provider }))
      
      axios.defaults.headers.Authorization = `Bearer ${token}`
      
      loading.close()
      
      ElMessage.success(`GitHub登录成功！欢迎 ${nickname}`)
      router.push('/')
      
    } catch (error) {
      console.error('GitHub登录回调错误:', error)
      ElMessage.error('GitHub登录失败，请稍后重试')
    }
  }
}

// 打开用户协议
const openUserAgreement = () => {
  router.push('/user-agreement')
}

// 打开隐私政策页面
const openPrivacyPolicy = () => {
  router.push('/privacy-policy')
}

// 跳转到忘记密码页面
const goToForgotPassword = () => {
  router.push('/forgot-password')
}

// 测试模式下的微信回调处理
const handleWechatCallbackTest = async (authUrl) => {
  try {
    const loading = ElLoading.service({
      lock: true,
      text: '正在处理微信登录...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    // 从URL中提取参数
    const url = new URL(authUrl, window.location.origin)
    const code = url.searchParams.get('code')
    const state = url.searchParams.get('state')
    
    // 调用后端处理微信回调
    const response = await axios.get(`/api/v1/auth/wechat/callback/?code=${code}&state=${state}`)
    const { access: token, username, nickname, avatar, provider } = response.data
    
    // 保存用户信息和token
    authStore.token = token
    authStore.user = { username, email: username, nickname, avatar, provider }
    
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify({ username, email: username, nickname, avatar, provider }))
    
    axios.defaults.headers.Authorization = `Bearer ${token}`
    
    loading.close()
    
    ElMessage.success(`微信登录成功！欢迎 ${nickname}`)
    router.push('/')
    
  } catch (error) {
    console.error('微信登录测试回调错误:', error)
    ElMessage.error('微信登录失败，请稍后重试')
  }
}

// 测试模式下的QQ回调处理
const handleQQCallbackTest = async (authUrl) => {
  try {
    const loading = ElLoading.service({
      lock: true,
      text: '正在处理QQ登录...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    // 从URL中提取参数
    const url = new URL(authUrl, window.location.origin)
    const code = url.searchParams.get('code')
    const state = url.searchParams.get('state')
    
    // 调用后端处理QQ回调
    const response = await axios.get(`/api/v1/auth/qq/callback/?code=${code}&state=${state}`)
    const { access: token, username, nickname, avatar, provider } = response.data
    
    // 保存用户信息和token
    authStore.token = token
    authStore.user = { username, email: username, nickname, avatar, provider }
    
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify({ username, email: username, nickname, avatar, provider }))
    
    axios.defaults.headers.Authorization = `Bearer ${token}`
    
    loading.close()
    
    ElMessage.success(`QQ登录成功！欢迎 ${nickname}`)
    router.push('/')
    
  } catch (error) {
    console.error('QQ登录测试回调错误:', error)
    ElMessage.error('QQ登录失败，请稍后重试')
  }
}

// 测试模式下的GitHub回调处理
const handleGithubCallbackTest = async (authUrl) => {
  try {
    const loading = ElLoading.service({
      lock: true,
      text: '正在处理GitHub登录...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    // 从URL中提取参数
    const url = new URL(authUrl, window.location.origin)
    const code = url.searchParams.get('code')
    const state = url.searchParams.get('state')
    
    // 调用后端处理GitHub回调
    const response = await axios.get(`/api/v1/auth/github/callback/?code=${code}&state=${state}`)
    const { access: token, username, nickname, avatar, provider } = response.data
    
    // 保存用户信息和token
    authStore.token = token
    authStore.user = { username, email: username, nickname, avatar, provider }
    
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify({ username, email: username, nickname, avatar, provider }))
    
    axios.defaults.headers.Authorization = `Bearer ${token}`
    
    loading.close()
    
    ElMessage.success(`GitHub登录成功！欢迎 ${nickname}`)
    router.push('/')
    
  } catch (error) {
    console.error('GitHub登录测试回调错误:', error)
    ElMessage.error('GitHub登录失败，请稍后重试')
  }
}

// 初始化时根据查询参数决定显示哪个表单
onMounted(() => {
  if (route.query.tab === 'register') {
    isRegisterForm.value = true
  } else {
    isRegisterForm.value = false
  }
  
  // 检查是否需要处理各种OAuth登录回调
  handleWechatCallback()
  handleQQCallback()
  handleGithubCallback()
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.form-switcher {
  display: flex;
  background: #f5f7fa;
}

.switch-btn {
  flex: 1;
  padding: 16px 0;
  border: none;
  background: transparent;
  font-size: 16px;
  font-weight: 500;
  color: #909399;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.switch-btn.active {
  color: #409eff;
  background: white;
}

.switch-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #409eff;
  border-radius: 3px 3px 0 0;
}

.form-content {
  padding: 30px;
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.form-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
  line-height: 1.5;
}

.login-form,
.register-form {
  width: 100%;
}

.login-form :deep(.el-form-item),
.register-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.login-form :deep(.el-input__wrapper),
.register-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.login-form :deep(.el-input__wrapper):hover,
.register-form :deep(.el-input__wrapper):hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.login-form :deep(.el-input__wrapper):focus-within,
.register-form :deep(.el-input__wrapper):focus-within {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.4);
  border-color: #409eff !important;
  outline: none;
  transform: translateY(-1px);
}

/* 设置输入框字体颜色 */
.login-form :deep(.el-input__inner),
.register-form :deep(.el-input__inner) {
  color: #303133 !important;
  font-size: 14px;
  font-weight: 400;
}

.login-form :deep(.el-input__inner)::placeholder,
.register-form :deep(.el-input__inner)::placeholder {
  color: #909399 !important;
  opacity: 1;
}

.submit-btn {
  width: 100%;
  height: 48px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-text {
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
}

.terms-checkbox {
  font-size: 13px;
  color: #606266 !important;
}

/* 复选框方框样式 */
.terms-checkbox :deep(.el-checkbox__inner) {
  border: 2px solid #dcdfe6 !important;
  width: 16px;
  height: 16px;
}

.terms-checkbox :deep(.el-checkbox__inner:hover) {
  border-color: #409eff !important;
}

.terms-checkbox :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #409eff !important;
  border-color: #409eff !important;
}

.terms-checkbox .link-text {
  color: #409eff !important;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.3s ease;
}

.terms-checkbox .link-text:hover {
  color: #66b1ff !important;
  text-decoration: underline;
}

.social-login {
  margin-top: 30px;
  text-align: center;
}

.divider {
  position: relative;
  text-align: center;
  color: #909399;
  font-size: 13px;
  margin-bottom: 20px;
}

.divider::before,
.divider::after {
  content: "";
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background-color: #e4e7ed;
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.social-icons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.social-btn {
  width: 48px;
  height: 48px;
  border: 1px solid #e4e7ed;
  background-color: #fff;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.social-btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s;
}

.social-btn:hover::before {
  left: 100%;
}

.social-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.social-btn:active {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.social-btn.wechat {
  color: #1aad19;
  border-color: #1aad19;
}

.social-btn.wechat:hover {
  background-color: #1aad19;
  color: white;
}

.social-btn.qq {
  color: #12b7f5;
  border-color: #12b7f5;
}

.social-btn.qq:hover {
  background-color: #12b7f5;
  color: white;
}

.social-btn.github {
  color: #333;
  border-color: #333;
}

.social-btn.github:hover {
  background-color: #333;
  color: white;
}

.social-btn i {
  font-size: 20px;
  transition: transform 0.3s ease;
}

.social-btn:hover i {
  transform: scale(1.1);
}

/* 动画效果 */
.slide-enter-active {
  transition: all 0.3s ease;
}

.slide-leave-active {
  transition: all 0.2s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 15px;
  }
  
  .login-card {
    max-width: 100%;
    border-radius: 15px;
  }
  
  .form-content {
    padding: 25px 20px;
  }
  
  .form-title {
    font-size: 22px;
  }
  
  .social-icons {
    gap: 12px;
  }
  
  .social-btn {
    width: 40px;
    height: 40px;
  }
}

@media (max-width: 480px) {
  .form-content {
    padding: 20px 15px;
  }
  
  .form-title {
    font-size: 20px;
  }
  
  .switch-btn {
    font-size: 15px;
    padding: 14px 0;
  }
}

/* 登录页面机器人Logo样式 - 正上方居中 */
:deep(.logo-container-center-top) {
  position: absolute;
  top: -40px; /* 使用绝对定位，向上偏移 */
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  background: white;
  border-radius: 50%;
  padding: 15px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  justify-content: center;
  align-items: center;
  width: fit-content;
}

:deep(.robot-logo-login) {
  font-size: 60px !important;
  line-height: 1 !important;
  display: inline-block !important;
}
</style>