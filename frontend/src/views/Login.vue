<template>
  <div class="login-container">
    <div class="login-card">
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
                <el-link type="info" :underline="false">忘记密码？</el-link>
              </div>
            </el-form>

            <div class="social-login">
              <div class="divider">其他登录方式</div>
              <div class="social-icons">
                <el-button class="social-btn wechat" circle>
                  <i class="fa-brands fa-weixin"></i>
                </el-button>
                <el-button class="social-btn qq" circle>
                  <i class="fa-brands fa-qq"></i>
                </el-button>
                <el-button class="social-btn github" circle>
                  <i class="fa-brands fa-github"></i>
                </el-button>
              </div>
            </div>
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
                  我同意 <el-link type="primary" :underline="false">用户协议</el-link> 和 <el-link type="primary" :underline="false">隐私政策</el-link>
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
import { ElMessage } from 'element-plus'

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
        const success = await authStore.login(loginForm.username, loginForm.password)
        if (success) {
          ElMessage.success('登录成功')
          router.push('/')
        } else {
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

// 初始化时根据查询参数决定显示哪个表单
onMounted(() => {
  if (route.query.tab === 'register') {
    isRegisterForm.value = true
  } else {
    isRegisterForm.value = false
  }
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
  overflow: hidden;
  position: relative;
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

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #ebeef5;
  z-index: 1;
}

.divider span {
  position: relative;
  z-index: 2;
  background: white;
  padding: 0 15px;
}

.social-icons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.social-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ebeef5;
  transition: all 0.3s ease;
}

.social-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.social-btn.wechat {
  color: #1aad19;
}

.social-btn.qq {
  color: #12b7f5;
}

.social-btn.github {
  color: #333;
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
</style>