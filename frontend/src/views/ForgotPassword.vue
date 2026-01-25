<template>
  <div class="forgot-password-container">
    <div class="forgot-password-card">
      <div class="card-header">
        <el-link type="primary" :underline="false" @click="goBackToLogin" class="back-to-login-link glass-effect top-left-link">
          <el-icon><ArrowLeft /></el-icon>
          返回登录
        </el-link>
      </div>
      <div class="main-content-wrapper">
        <h2 class="form-title centered-title">重置密码</h2>
        <div class="form-content">
        <!-- 测试环境提示 -->
        

        <!-- 重置密码表单 (测试环境：直接显示) -->
        <div class="form-wrapper">
          <div class="reset-password-header">
            <p class="reset-subtitle">请填写用户名或邮箱，设置不少于6位的新密码</p>
          </div>
          
          <el-form
            ref="resetFormRef"
            :model="resetForm"
            :rules="resetRules"
            class="reset-password-form"
          >
            <!-- 用户名输入框 -->
            <el-form-item prop="username" label="用户名" class="el-form-item--username">
              <el-input
                v-model="resetForm.username"
                placeholder="请输入用户名"
                prefix-icon="User"
                size="large"
                :clearable="true"
              />
            </el-form-item>

            <!-- 邮箱输入框 -->
            <el-form-item prop="email" label="邮箱" class="el-form-item--email">
              <el-input
                v-model="resetForm.email"
                placeholder="请输入邮箱"
                prefix-icon="Message"
                size="large"
                :clearable="true"
              />
            </el-form-item>

            <!-- 新密码输入框 -->
            <el-form-item prop="newPassword" label="新密码" class="el-form-item--new-password">
              <el-input
                v-model="resetForm.newPassword"
                :type="showNewPwd ? 'text' : 'password'"
                placeholder="请输入新密码"
                prefix-icon="Lock"
                size="large"
                :clearable="true"
                :show-password="true"
                @input="checkPasswordStrength"
              />
            </el-form-item>

            <!-- 确认密码输入框 -->
            <el-form-item prop="confirmPassword" label="确认新密码" class="el-form-item--confirm-password">
              <el-input
                v-model="resetForm.confirmPassword"
                :type="showConfirmPwd ? 'text' : 'password'"
                placeholder="请再次输入新密码"
                prefix-icon="Lock"
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
                class="submit-btn glass-effect"
                :disabled="!canSubmit"
                :loading="isLoading"
                @click="handleResetPasswordTest"
              >
                <template #loading>
                  <span class="loading-text">重置中...</span>
                </template>
                <span class="btn-text">重置密码</span>
              </el-button>
            </el-form-item>
            
            <!-- 表单内部页脚 -->
            <div class="internal-footer">
              <p class="footer-text">记得密码？<el-link type="primary" @click="goBackToLogin" class="glass-effect">立即登录</el-link></p>
            </div>
            
          </el-form>
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
import { ArrowLeft, User, Lock, Message } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

const isLoading = ref(false)

// 密码显示状态
const showNewPwd = ref(false)
const showConfirmPwd = ref(false)

// 表单引用
const resetFormRef = ref(null)

// 重置密码表单数据（测试环境：分离用户名和邮箱字段）
const resetForm = reactive({
  username: '',
  email: '',
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
  
  // 密码长度不少于6位
  if (password.length >= 6) {
    level = 'medium'
    // 包含字母+数字 → 强
    if (/[a-zA-Z]/.test(password) && /[0-9]/.test(password)) {
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
  // 1. 用户名/邮箱至少填写一个且格式正确
  // 2. 密码长度不少于6位
  // 3. 两次密码输入一致
  // 4. 确认密码不为空
  const isUsernameValid = resetForm.username && resetForm.username.trim().length >= 3
  const isEmailValid = resetForm.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(resetForm.email)
  const isIdentifierValid = isUsernameValid || isEmailValid
  const isPwdValid = pwd.length >= 6
  const isConfirmValid = resetForm.confirmPassword && pwd === resetForm.confirmPassword
  return isIdentifierValid && isPwdValid && isConfirmValid
})

// 重置密码表单验证规则
const resetRules = {
  username: [
    { 
      validator: (rule, value, callback) => {
        // 如果邮箱为空，则用户名必须填写
        if (!resetForm.email || resetForm.email.trim() === '') {
          if (!value || value.trim() === '') {
            callback(new Error('请至少填写用户名或邮箱其中之一'))
          } else if (value.length < 3 || value.length > 50) {
            callback(new Error('用户名长度应在3-50个字符之间'))
          } else {
            callback()
          }
        } else {
          // 如果邮箱已填写，则用户名可选
          if (value && value.length > 0 && (value.length < 3 || value.length > 50)) {
            callback(new Error('用户名长度应在3-50个字符之间'))
          } else {
            callback()
          }
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { 
      validator: (rule, value, callback) => {
        // 如果用户名为空，则邮箱必须填写
        if (!resetForm.username || resetForm.username.trim() === '') {
          if (!value || value.trim() === '') {
            callback(new Error('请至少填写用户名或邮箱其中之一'))
          } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            callback(new Error('请输入正确的邮箱地址'))
          } else {
            callback()
          }
        } else {
          // 如果用户名已填写，则邮箱可选
          if (value && value.trim() !== '' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            callback(new Error('请输入正确的邮箱地址'))
          } else {
            callback()
          }
        }
      },
      trigger: 'blur'
    }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请输入新密码'))
        } else if (value.length < 6) {
          callback(new Error('密码长度应不少于6位'))
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

// 处理重置密码（测试环境）
const handleResetPasswordTest = async () => {
  if (!canSubmit.value) return
  
  try {
    isLoading.value = true
    
    // 优先使用用户名，如果没有则使用邮箱
    const identifier = resetForm.username || resetForm.email
    
    // 直接调用重置密码接口，传入用户名/邮箱和新密码
    const response = await axios.post('/api/v1/password/reset/test/', {
      identifier: identifier,
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

// 返回登录页面
const goBackToLogin = () => {
  router.push('/login')
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
  width: 100%;
  max-width: 480px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  min-height: 650px;
}

.forgot-password-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
}

.back-link {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #667eea;
  font-weight: 500;
  transition: color 0.3s ease;
}

.back-link:hover {
  color: #764ba2;
}
/* 卡片头部样式 - 包含返回按钮 */
.card-header {
  width: 100%;
  padding: 20px 20px 0 20px;
  box-sizing: border-box;
  position: relative;  /* 为返回按钮提供相对定位上下文 */
}

/* 返回登录链接样式 */
.back-to-login-link {
  position: absolute;  /* 绝对定位，不占用文档流空间 */
  top: 20px;
  left: 20px;
  z-index: 10;  /* 确保按钮在顶层 */
}

/* 主要内容包装器 - 使除返回按钮外的所有内容下移 */
.main-content-wrapper {
  margin-top: 40px;  /* 恢复适当的上边距 */
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 表单内容区域 */
.form-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 380px;  /* 限制最大宽度使内容更集中 */
  margin: 0 auto;    /* 居中对齐 */
}

.test-env-notice {
  margin-bottom: 25px;
}

/* 重置密码头部样式 */
.reset-password-header {
  text-align: center;
  margin-bottom: 25px;
}

.reset-subtitle {
  font-size: 16px;
  color: #2c3e50;
  margin: 0;
  line-height: 1.6;
  font-weight: 500;
}

/* 表单项目样式 - 实现完整的布局要求 */
.reset-password-form :deep(.el-form-item) {
  display: flex !important;
  align-items: center !important; /* 标签与输入框水平对齐 */
  gap: 12px !important; /* 减少标签与输入框间距 */
  margin-bottom: 25px !important; /* 减少底部间距使表单更紧凑 */
}

/* 所有标签统一宽度以实现视觉统一 */
.reset-password-form :deep(.el-form-item__label) {
  font-size: 14px; /* 统一字体大小 */
  font-weight: 600;
  color: #2c3e50;
  flex: 0 0 120px; /* 减少标签宽度，让输入框更长 */
  text-align: left;
  padding: 0;
  line-height: 1.5; /* 确保标签文本行高适中 */
}

/* 特定标签的字符间距 - 实现标签字符间有空格 */
.reset-password-form :deep(.el-form-item--username .el-form-item__label),
.reset-password-form :deep(.el-form-item--email .el-form-item__label),
.reset-password-form :deep(.el-form-item--new-password .el-form-item__label),
.reset-password-form :deep(.el-form-item--confirm-password .el-form-item__label) {
  font-family: 'Courier New', monospace;
  font-size: 8px; /* 进一步缩小字体 */
  letter-spacing: 3px; /* 调整字符间距 */
  text-align: left;
}

/* 输入框占据更多空间 */
.reset-password-form :deep(.el-form-item__content) {
  flex: 1 1 auto; /* 让输入框占据更多可用空间 */
  margin-left: 0 !important;
}

/* 输入框容器样式 */
.reset-password-form :deep(.el-input__wrapper) {
  background-color: #f8f9ff;
  border-radius: 12px;
  border: 1px solid #e2e6f0;
  height: 46px;  /* 稍微减小高度 */
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
  transition: all 0.3s ease;
  max-width: 240px;  /* 稍微减小最大宽度 */
}

.reset-password-form :deep(.el-input__wrapper):hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  border-color: #cbd5e1;
}

.reset-password-form :deep(.el-input__wrapper):focus-within {
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
  border-color: #667eea;
  transform: translateY(-2px);
  outline: none;
}

/* 输入框内部文字 */
.reset-password-form :deep(.el-input__inner) {
  color: #2d3748 !important;
  font-size: 15px;
  font-weight: 400;
  padding: 0 8px;
}

.reset-password-form :deep(.el-input__inner)::placeholder {
  color: #a0aec0 !important;
  opacity: 1;
  font-weight: 400;
}

/* 图标样式 */
.reset-password-form :deep(.el-input__prefix-inner) {
  font-size: 18px;
  color: #718096;
  margin-right: 10px;
}

/* 返回登录链接容器的间距样式 */
.spaced-back-link {
  margin-top: 5px;
  margin-bottom: 20px;
}

/* 毛玻璃效果样式 */
.glass-effect {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5) !important;
  border-radius: 8px !important;
  padding: 8px 16px !important;
  transition: all 0.3s ease !important;
  text-decoration: none !important;
  color: #409EFF !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  position: relative !important;
  z-index: 10 !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08) !important;
}

.glass-effect:hover {
  background: rgba(255, 255, 255, 0.95) !important;
  transform: translateX(-2px) !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.12) !important;
}

/* 按钮的毛玻璃效果 */
.submit-btn.glass-effect {
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.7) !important;
  color: #667eea !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
  font-weight: 600 !important;
  letter-spacing: 1px !important;
}

.submit-btn.glass-effect:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.95) !important;
  transform: translateY(-3px) !important;
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2) !important;
}

/* 顶部左侧链接样式 */
.top-left-link {
  position: absolute !important;
  left: 10px !important;  /* 向右移动一点 */
  top: 10px !important;  /* 向下移动一些 */
}

/* 标题区域样式 */
.header-section {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  position: relative !important;
  margin-bottom: 20px !important;
}

/* 居中标题样式 */
.centered-title {
  text-align: center !important;
  width: 100% !important;
  margin: 8px 0 1px 0 !important;  /* 进一步减少上下边距 */
}

/* 返回登录链接的样式 */
.back-to-login-link {
  border-radius: 8px;
  transition: all 0.3s ease;
  text-decoration: none !important;
  color: #409EFF !important;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* 提交按钮样式 */
.submit-btn {
  width: 100%;
  height: 46px;  /* 与输入框高度保持一致 */
  border-radius: 12px;  /* 与输入框圆角保持一致 */
  font-size: 15px;  /* 稍微减小字体 */
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);  /* 稍微减小阴影 */
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
}

/* 密码强度显示 - 增强版 */
.password-strength {
  text-align: left;
  margin: 20px 0 30px 0;
  padding: 12px 0;
  background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
  border-radius: 12px;
  font-size: 14px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  grid-column: 1 / -1; /* 跨越整行 */
}

.password-strength:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.strength-label {
  color: #4a5568;
  margin-right: 10px;
  font-weight: 600;
}

.strength-level {
  font-weight: 600;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
}

.strength-level.weak {
  background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
  color: #c53030;
  border: 1px solid #fc8181;
}

.strength-level.medium {
  background: linear-gradient(135deg, #feebc8 0%, #fbd38d 100%);
  color: #d69e2e;
  border: 1px solid #f6ad55;
}

.strength-level.strong {
  background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
  color: #38a169;
  border: 1px solid #68d391;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-text {
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* 表单底部链接 */
.form-footer {
  text-align: center;
  margin-top: 25px;
}

.footer-text {
  margin: 0;
  font-size: 14px;
  color: #718096;
}

.footer-text .el-link {
  font-weight: 600;
  color: #667eea;
  transition: color 0.3s ease;
}

.footer-text .el-link:hover {
  color: #764ba2;
  transform: translateX(2px);
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
    margin: 0 15px;
    border-radius: 20px;
  }
  
  .form-content {
    padding: 40px 25px 30px;
  }
  
  .reset-subtitle {
    font-size: 15px;
  }
  
  .reset-password-form :deep(.el-form-item) {
    flex-direction: column; /* 移动端改为垂直排列 */
    align-items: flex-start;
    gap: 8px;
  }
  
  .reset-password-form :deep(.el-form-item__label) {
    flex: none;
    width: 100%; /* 移动端标签占满整行 */
    text-align: left;
  }
  
  /* 移动端特定标签样式 */
    .reset-password-form :deep(.el-form-item--username .el-form-item__label),
    .reset-password-form :deep(.el-form-item--email .el-form-item__label),
    .reset-password-form :deep(.el-form-item--new-password .el-form-item__label),
    .reset-password-form :deep(.el-form-item--confirm-password .el-form-item__label) {
      font-size: 13px; /* 移动端优化字体大小 */
      letter-spacing: 3px; /* 移动端优化字符间距 */
    }
  
  .reset-password-form :deep(.el-input__wrapper) {
    height: 48px;
  }
  
  .submit-btn {
    height: 48px;
  }
}

/* 内部页脚样式 - 位于表单内部，提交按钮下方 */
.internal-footer {
  margin-top: 15px;
  text-align: center;
  padding-top: 15px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.internal-footer .footer-text {
  color: #606266;
  font-size: 14px;
}
</style>