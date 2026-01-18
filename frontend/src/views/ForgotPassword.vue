<template>
  <div class="forgot-password-container">
    <div class="forgot-password-card">
      <!-- 返回登录按钮 -->
      <div class="back-link">
        <el-link type="primary" underline="never" @click="goBackToLogin">
          <el-icon><ArrowLeft /></el-icon>
          返回登录
        </el-link>
      </div>

      <!-- 表单内容 -->
      <div class="form-content">
        <!-- 重置密码表单 -->
        <div class="form-wrapper">
          <div class="reset-password-header">
            <h2 class="reset-title">设置新密码</h2>
            <p class="reset-subtitle">请设置8-20位新密码，包含字母+数字，不能为纯数字/纯字母</p>
          </div>
          
          <el-form
            ref="resetFormRef"
            :model="resetForm"
            :rules="resetRules"
            class="reset-password-form"
          >
            <!-- 新密码输入框 -->
            <el-form-item prop="newPassword" label="新密码">
              <el-input
                v-model="resetForm.newPassword"
                :type="showNewPwd ? 'text' : 'password'"
                placeholder="请输入新密码"
                size="large"
                :clearable="true"
                :show-password="true"
                @input="checkPasswordStrength"
              />
            </el-form-item>

            <!-- 确认密码输入框 -->
            <el-form-item prop="confirmPassword" label="确认新密码">
              <el-input
                v-model="resetForm.confirmPassword"
                :type="showConfirmPwd ? 'text' : 'password'"
                placeholder="请再次输入新密码"
                size="large"
                :clearable="true"
                :show-password="true"
              />
            </el-form-item>

            <!-- 密码强度显示 -->
            <div class="password-strength" v-show="resetForm.newPassword">
              <span class="strength-label">密码强度：</span>
              <span :class="['strength-level', passwordStrength.level]">{{ passwordStrength.text }}</span>
            </div>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="reset-btn"
                :disabled="!canSubmit"
                :loading="isLoading"
                @click="handleResetPassword"
              >
                <template #loading>
                  <span class="loading-text">重置中...</span>
                </template>
                <span class="btn-text">重置密码</span>
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 开发环境提示 -->
        <div v-if="resetUrl" class="dev-info">
          <el-alert
            title="开发环境提示"
            type="info"
            :closable="false"
            description="在开发环境中，重置链接将显示在此处。生产环境会发送到邮箱。"
            show-icon
          />
          <div class="reset-link">
            <p><strong>重置链接：</strong></p>
            <el-link type="primary" @click="openResetLink">{{ resetUrl }}</el-link>
            <p><strong>有效期至：</strong>{{ expiresAt }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

const isLoading = ref(false)
const resetUrl = ref('')
const expiresAt = ref('')

// 密码显示状态
const showNewPwd = ref(false)
const showConfirmPwd = ref(false)

// 表单引用
const resetFormRef = ref(null)

// 重置密码表单数据
const resetForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

// 密码强度状态
const passwordStrength = reactive({
  level: 'weak',
  text: '弱'
})

// 计算密码强度等级
const checkPasswordStrength = () => {
  const password = resetForm.newPassword
  
  if (!password) {
    passwordStrength.level = 'weak'
    passwordStrength.text = '弱'
    return
  }
  
  let level = 'weak'
  
  // 密码长度8-20位
  if (password.length >= 8 && password.length <= 20) {
    // 包含字母+数字 → 中
    if (/[a-zA-Z]/.test(password) && /[0-9]/.test(password)) {
      level = 'medium'
    }
    // 包含字母+数字+特殊符号 → 强
    if (/[a-zA-Z]/.test(password) && /[0-9]/.test(password) && /[!@#$%^&*]/.test(password)) {
      level = 'strong'
    }
  }
  
  const levelMap = {
    weak: '弱',
    medium: '中',
    strong: '强'
  }
  
  passwordStrength.level = level
  passwordStrength.text = levelMap[level]
}

// 计算是否可以提交：核心校验规则
const canSubmit = computed(() => {
  const pwd = resetForm.newPassword
  // 1. 密码长度8-20位
  // 2. 包含字母+数字
  // 3. 两次密码输入一致
  // 4. 确认密码不为空
  const isPwdValid = pwd.length >= 8 && pwd.length <= 20 && /[a-zA-Z]/.test(pwd) && /[0-9]/.test(pwd)
  const isConfirmValid = resetForm.confirmPassword && pwd === resetForm.confirmPassword
  return isPwdValid && isConfirmValid
})

// 重置密码表单验证规则
const resetRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请输入新密码'))
        } else if (value.length < 8 || value.length > 20) {
          callback(new Error('密码长度应为8-20位'))
        } else if (!/[a-zA-Z]/.test(value) || !/\d/.test(value)) {
          callback(new Error('密码必须包含字母和数字'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请确认新密码'))
        } else if (value !== resetForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 返回登录页面
const goBackToLogin = () => {
  router.push('/login')
}

// 处理重置密码
const handleResetPassword = async () => {
  if (!canSubmit.value) return
  
  try {
    isLoading.value = true
    
    const response = await axios.post('/api/v1/password/reset/', {
      new_password: resetForm.newPassword,
      confirm_password: resetForm.confirmPassword
    })
    
    ElMessage.success(response.data.message)
    
    // 重置成功后跳转到登录页面
    setTimeout(() => {
      router.push('/login')
    }, 2000)
    
  } catch (error) {
    console.error('重置密码错误:', error)
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else {
      ElMessage.error('重置密码失败，请稍后重试')
    }
  } finally {
    isLoading.value = false
  }
}

// 打开重置链接（开发环境）
const openResetLink = () => {
  if (resetUrl.value) {
    window.open(resetUrl.value, '_self')
  }
}


</script>

<style scoped>
.forgot-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.forgot-password-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  padding: 40px;
  width: 100%;
  max-width: 420px;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.back-link {
  position: absolute;
  top: 20px;
  left: 20px;
}

.form-content {
  margin-top: 20px;
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 重置密码头部样式 */
.reset-password-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px 0;
  border-bottom: 2px solid #f0f0f0;
}

.reset-title {
  font-size: 22px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.reset-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 表单标签样式 - 加深字体颜色，左对齐 */
.reset-password-form :deep(.el-form-item__label) {
  font-size: 14px;
  font-weight: 500;
  color: #333 !important;
  margin-bottom: 8px;
  display: block;
  text-align: left;
  width: 100%;
  white-space: nowrap;
  overflow: visible;
  letter-spacing: 0.5px;
}

/* 表单项间距和对齐 - 垂直布局 */
.reset-password-form :deep(.el-form-item) {
  margin-bottom: 24px;
  display: block;
}

.reset-password-form :deep(.el-form-item__content) {
  display: block;
  width: 100%;
}

/* 输入框样式 */
.reset-password-form :deep(.el-input) {
  width: 100%;
}

.reset-password-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  border: 2px solid #e0e0e0;
  transition: all 0.3s ease;
  padding: 8px 12px;
}

.reset-password-form :deep(.el-input__wrapper:hover) {
  border-color: #c0c0c0;
}

.reset-password-form :deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

/* 密码强度显示 */
.password-strength {
  text-align: center;
  margin: 15px 0 25px 0;
  padding: 8px 0;
  background: #f8f8f8;
  border-radius: 4px;
  font-size: 13px;
}

.strength-label {
  color: #666;
  margin-right: 8px;
}

.strength-level {
  font-weight: 500;
  padding: 2px 10px;
  border-radius: 3px;
  font-size: 12px;
}

.strength-level.weak {
  background-color: #ffebee;
  color: #f44336;
  border: 1px solid #ffcdd2;
}

.strength-level.medium {
  background-color: #fff3e0;
  color: #ff9800;
  border: 1px solid #ffe0b2;
}

.strength-level.strong {
  background-color: #e8f5e8;
  color: #4caf50;
  border: 1px solid #c8e6c9;
}

.reset-btn {
  width: 100%;
  margin-top: 10px;
  height: 48px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border: none;
  transition: all 0.3s ease;
}

.reset-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(103, 194, 58, 0.3);
}

.reset-btn:disabled {
  background: #c6e2ff;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.forgot-password-form {
  width: 100%;
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
  height: 48px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
  transition: all 0.3s ease;
}

.loading-text {
  display: inline-flex;
  align-items: center;
}

.btn-text {
  font-weight: 500;
}

.dev-info {
  margin-top: 20px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.reset-link {
  margin-top: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
}

.reset-link p {
  margin: 5px 0;
}

/* 过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 响应式设计 */
@media (max-width: 480px) {
  .forgot-password-card {
    padding: 30px 20px;
    margin: 0 10px;
  }
  
  .reset-box {
    width: 100%;
    padding: 20px;
  }
}
</style>