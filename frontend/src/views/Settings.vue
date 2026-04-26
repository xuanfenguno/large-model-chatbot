<template>
  <div class="settings-page">
    <!-- 顶部导航栏 -->
    <div class="settings-header">
      <div class="header-left">
        <el-button 
          class="back-btn" 
          @click="goBack"
          :icon="ArrowLeft"
        >
          返回主界面
        </el-button>
        <h2 class="header-title">
          <el-icon><Setting /></el-icon>
          设置
        </h2>
      </div>
    </div>

    <div class="settings-container">
      <!-- 左侧导航菜单 -->
      <div class="settings-sidebar">
        <div class="user-card">
          <div class="user-avatar">
            <img 
              v-if="profileForm.avatar" 
              :src="profileForm.avatar" 
              alt="头像" 
            />
            <el-icon v-else class="avatar-icon"><User /></el-icon>
          </div>
          <div class="user-info">
            <h3 class="user-name">{{ profileForm.nickname || profileForm.username || '用户' }}</h3>
            <p class="user-email">{{ profileForm.email || '未设置邮箱' }}</p>
          </div>
        </div>

        <el-menu
          :default-active="activeTab"
          class="settings-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="profile">
            <el-icon><User /></el-icon>
            <span>个人资料</span>
          </el-menu-item>
          <el-menu-item index="account">
            <el-icon><Lock /></el-icon>
            <span>账户设置</span>
          </el-menu-item>
          <el-menu-item index="ai-models">
            <el-icon><Cpu /></el-icon>
            <span>AI模型设置</span>
          </el-menu-item>
          <el-menu-item index="appearance">
            <el-icon><Brush /></el-icon>
            <span>界面设置</span>
          </el-menu-item>
          <el-menu-item index="privacy">
            <el-icon><Lock /></el-icon>
            <span>隐私设置</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 右侧内容区域 -->
      <div class="settings-content">
        <!-- 个人资料 -->
        <div v-show="activeTab === 'profile'" class="content-section">
          <div class="section-header">
            <h3>个人资料</h3>
            <p class="section-desc">管理您的个人信息和头像</p>
          </div>
          
          <el-card class="settings-card">
            <el-form :model="profileForm" label-width="100px" class="settings-form">
              <!-- 头像上传区域 -->
              <el-form-item label="头像">
                <div class="avatar-upload-section">
                  <div class="avatar-preview">
                    <img 
                      v-if="profileForm.avatar" 
                      :src="profileForm.avatar" 
                      alt="当前头像" 
                      class="avatar-img"
                    />
                    <div v-else class="avatar-placeholder">
                      <el-icon><User /></el-icon>
                    </div>
                    <div class="avatar-overlay" @click="triggerUpload">
                      <el-icon><Camera /></el-icon>
                      <span>更换头像</span>
                    </div>
                  </div>
                  <div class="avatar-actions">
                    <el-upload
                      ref="uploadRef"
                      class="avatar-uploader"
                      :auto-upload="true"
                      :show-file-list="false"
                      accept=".jpg,.jpeg,.png,.gif,.webp"
                      :before-upload="beforeAvatarUpload"
                      :http-request="customUploadAvatar"
                    >
                      <el-button type="primary" plain>
                        <el-icon><Upload /></el-icon>
                        上传头像
                      </el-button>
                    </el-upload>
                    <el-button 
                      v-if="profileForm.avatar" 
                      type="danger" 
                      plain 
                      @click="removeAvatar"
                    >
                      <el-icon><Delete /></el-icon>
                      删除头像
                    </el-button>
                  </div>
                  <p class="upload-tip">支持 JPG、PNG、GIF、WEBP 格式，大小不超过 5MB</p>
                </div>
              </el-form-item>
              
              <el-divider />
              
              <el-form-item label="用户名">
                <el-input v-model="profileForm.username" disabled>
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
                <span class="form-hint">用户名不可修改</span>
              </el-form-item>
              
              <el-form-item label="昵称">
                <el-input 
                  v-model="profileForm.nickname" 
                  placeholder="请输入昵称"
                  maxlength="30"
                  show-word-limit
                >
                  <template #prefix>
                    <el-icon><EditPen /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item label="邮箱">
                <el-input 
                  v-model="profileForm.email" 
                  placeholder="请输入邮箱地址"
                  type="email"
                >
                  <template #prefix>
                    <el-icon><Message /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item label="个人简介">
                <el-input 
                  v-model="profileForm.bio" 
                  type="textarea" 
                  :rows="4" 
                  placeholder="请输入个人简介"
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  size="large"
                  @click="saveProfile" 
                  :loading="saving"
                  :disabled="saving"
                >
                  <el-icon><Check /></el-icon>
                  {{ saving ? '保存中...' : '保存更改' }}
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 账户设置 -->
        <div v-show="activeTab === 'account'" class="content-section">
          <div class="section-header">
            <h3>账户设置</h3>
            <p class="section-desc">管理您的账户安全和登录信息</p>
          </div>

          <el-card class="settings-card">
            <template #header>
              <div class="card-header">
                <span>账户信息</span>
              </div>
            </template>
            <div class="account-info">
              <div class="info-item">
                <span class="info-label">用户名</span>
                <span class="info-value">{{ profileForm.username }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">邮箱</span>
                <span class="info-value">{{ profileForm.email || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">注册时间</span>
                <span class="info-value">{{ profileForm.created_at || '未知' }}</span>
              </div>
            </div>
          </el-card>

          <el-card class="settings-card security-card">
            <template #header>
              <div class="card-header">
                <span>安全设置</span>
              </div>
            </template>
            <div class="security-item">
              <div class="security-info">
                <h4>修改密码</h4>
                <p>定期更改密码可以保护您的账户安全</p>
              </div>
              <el-button type="primary" plain @click="showChangePasswordDialog">
                修改密码
              </el-button>
            </div>
          </el-card>
        </div>

        <!-- AI模型设置 -->
        <div v-show="activeTab === 'ai-models'" class="content-section">
          <div class="section-header">
            <h3>AI模型设置</h3>
            <p class="section-desc">配置您的AI API密钥</p>
          </div>

          <el-card class="settings-card">
            <el-form label-width="140px" class="settings-form">
              <el-form-item label="Qwen API Key">
                <el-input 
                  v-model="aiSettings.qwenApiKey" 
                  type="password" 
                  placeholder="请输入Qwen API Key"
                  show-password
                  class="api-key-input"
                >
                  <template #prefix>
                    <el-icon><Key /></el-icon>
                  </template>
                </el-input>
                <span class="form-hint">用于通义千问模型</span>
              </el-form-item>
              
              <el-form-item label="DeepSeek API Key">
                <el-input 
                  v-model="aiSettings.deepseekApiKey" 
                  type="password" 
                  placeholder="请输入DeepSeek API Key"
                  show-password
                  class="api-key-input"
                >
                  <template #prefix>
                    <el-icon><Key /></el-icon>
                  </template>
                </el-input>
                <span class="form-hint">用于DeepSeek模型</span>
              </el-form-item>
              
              <el-form-item label="豆包 API Key">
                <el-input 
                  v-model="aiSettings.doubaoApiKey" 
                  type="password" 
                  placeholder="请输入豆包 API Key"
                  show-password
                  class="api-key-input"
                >
                  <template #prefix>
                    <el-icon><Key /></el-icon>
                  </template>
                </el-input>
                <span class="form-hint">用于字节跳动豆包模型</span>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  size="large"
                  @click="saveAiSettings"
                  :loading="savingAi"
                >
                  <el-icon><Check /></el-icon>
                  {{ savingAi ? '保存中...' : '保存AI设置' }}
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 界面设置 -->
        <div v-show="activeTab === 'appearance'" class="content-section">
          <div class="section-header">
            <h3>界面设置</h3>
            <p class="section-desc">自定义您的界面外观</p>
          </div>

          <el-card class="settings-card">
            <el-form label-width="120px" class="settings-form">
              <el-form-item label="主题模式">
                <el-radio-group v-model="appearanceSettings.theme" @change="changeTheme" size="large">
                  <el-radio-button label="auto">
                    <el-icon><Sunny /></el-icon>
                    自动
                  </el-radio-button>
                  <el-radio-button label="light">
                    <el-icon><Sunrise /></el-icon>
                    浅色
                  </el-radio-button>
                  <el-radio-button label="dark">
                    <el-icon><Moon /></el-icon>
                    深色
                  </el-radio-button>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="语言">
                <el-select v-model="appearanceSettings.language" placeholder="选择语言" size="large">
                  <el-option label="中文" value="zh-CN">
                    <span class="lang-option">🇨🇳 中文</span>
                  </el-option>
                  <el-option label="English" value="en-US">
                    <span class="lang-option">🇺🇸 English</span>
                  </el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  size="large"
                  @click="saveAppearanceSettings"
                  :loading="savingAppearance"
                >
                  <el-icon><Check /></el-icon>
                  {{ savingAppearance ? '保存中...' : '保存外观设置' }}
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 隐私设置 -->
        <div v-show="activeTab === 'privacy'" class="content-section">
          <div class="section-header">
            <h3>隐私设置</h3>
            <p class="section-desc">管理您的隐私和数据</p>
          </div>

          <el-card class="settings-card">
            <div class="privacy-list">
              <div class="privacy-item">
                <div class="privacy-info">
                  <h4>聊天记录保存</h4>
                  <p>开启后，您的聊天记录将被保存到服务器</p>
                </div>
                <el-switch 
                  v-model="privacySettings.saveChatHistory" 
                  size="large"
                  active-text="开启"
                  inactive-text="关闭"
                />
              </div>
              
              <el-divider />
              
              <div class="privacy-item">
                <div class="privacy-info">
                  <h4>数据统计</h4>
                  <p>允许我们收集匿名使用数据以改进产品</p>
                </div>
                <el-switch 
                  v-model="privacySettings.allowAnalytics" 
                  size="large"
                  active-text="允许"
                  inactive-text="拒绝"
                />
              </div>
            </div>
            
            <el-divider />
            
            <div class="privacy-actions">
              <el-button 
                type="primary" 
                size="large"
                @click="savePrivacySettings"
                :loading="savingPrivacy"
              >
                <el-icon><Check /></el-icon>
                {{ savingPrivacy ? '保存中...' : '保存隐私设置' }}
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <el-dialog
      v-model="changePasswordDialogVisible"
      title="修改密码"
      width="450px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="changePasswordFormRef"
        :model="changePasswordForm"
        :rules="changePasswordRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="currentPassword">
          <el-input
            v-model="changePasswordForm.currentPassword"
            type="password"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="changePasswordForm.newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="changePasswordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="changePasswordDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="changingPassword"
            @click="handleChangePassword"
          >
            {{ changingPassword ? '修改中...' : '确认修改' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings'
import { 
  User, 
  Cpu, 
  Setting, 
  Lock, 
  Brush,
  ArrowLeft,
  Camera,
  Upload,
  Delete,
  Check,
  EditPen,
  Message,
  Key,
  Sunny,
  Sunrise,
  Moon
} from '@element-plus/icons-vue'
import api from '@/utils/request'

const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const router = useRouter()
const route = useRoute()
const uploadRef = ref(null)

// 当前激活的标签页
const activeTab = ref(route.query.tab || 'profile')

// 保存状态
const saving = ref(false)
const savingAi = ref(false)
const savingAppearance = ref(false)
const savingPrivacy = ref(false)

// 个人资料表单
const profileForm = reactive({
  username: '',
  email: '',
  nickname: '',
  bio: '',
  avatar: ''
})

// AI设置
const aiSettings = reactive({
  qwenApiKey: '',
  deepseekApiKey: '',
  doubaoApiKey: ''
})

// 外观设置
const appearanceSettings = reactive({
  theme: 'auto',
  language: 'zh-CN'
})

// 隐私设置
const privacySettings = reactive({
  saveChatHistory: true,
  allowAnalytics: true
})

// 修改密码弹窗
const changePasswordDialogVisible = ref(false)
const changingPassword = ref(false)
const changePasswordFormRef = ref(null)
const changePasswordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 修改密码表单验证规则
const changePasswordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== changePasswordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 返回主界面
const goBack = () => {
  router.push('/chat')
}

// 菜单选择
const handleMenuSelect = (index) => {
  activeTab.value = index
  // 更新URL参数
  router.replace({ 
    path: '/settings', 
    query: { tab: index }
  })
}

// 触发上传
const triggerUpload = () => {
  uploadRef.value?.$el.querySelector('input').click()
}

// 从设置存储加载数据
const initSettingsData = () => {
  Object.assign(aiSettings, settingsStore.settings.ai)
  Object.assign(appearanceSettings, settingsStore.settings.preferences)
  Object.assign(privacySettings, settingsStore.settings.privacy)
}

// 更新设置信息
const updateSettingsInfo = () => {
  settingsStore.initSettings()
}

// 初始化个人资料数据
const initData = () => {
  // 从authStore获取用户信息
  if (authStore.user) {
    profileForm.username = authStore.user.username || ''
    profileForm.email = authStore.user.email || ''
    profileForm.nickname = authStore.user.nickname || authStore.user.username || ''
    profileForm.avatar = authStore.user.avatar || ''
    profileForm.bio = authStore.user.bio || ''
  }
  
  // 从设置存储加载数据
  initSettingsData()
}

// 保存个人资料
const saveProfile = async () => {
  saving.value = true
  try {
    const response = await api.put('/profile/', {
      nickname: profileForm.nickname,
      email: profileForm.email,
      bio: profileForm.bio,
    }, { timeout: 10000 })

    // 更新auth store中的用户信息
    if (authStore.user) {
      Object.assign(authStore.user, {
        nickname: profileForm.nickname,
        email: profileForm.email,
        bio: profileForm.bio,
      })
    }

    ElMessage.success('个人资料保存成功')
  } catch (error) {
    console.error('保存个人资料失败:', error)
    ElMessage.error('保存失败：' + (error.response?.data?.error || error.message))
  } finally {
    saving.value = false
  }
}

// 显示修改密码弹窗
const showChangePasswordDialog = () => {
  changePasswordDialogVisible.value = true
  // 清空表单
  changePasswordForm.currentPassword = ''
  changePasswordForm.newPassword = ''
  changePasswordForm.confirmPassword = ''
}

// 处理修改密码
const handleChangePassword = async () => {
  if (!changePasswordFormRef.value) return

  await changePasswordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        changingPassword.value = true
        const response = await api.post('/change-password/', {
          current_password: changePasswordForm.currentPassword,
          new_password: changePasswordForm.newPassword,
          confirm_password: changePasswordForm.confirmPassword
        }, { timeout: 10000 })

        ElMessage.success(response.data.message || '密码修改成功')
        changePasswordDialogVisible.value = false
      } catch (error) {
        console.error('修改密码失败:', error)
        ElMessage.error(error.response?.data?.error || '修改密码失败，请检查当前密码是否正确')
      } finally {
        changingPassword.value = false
      }
    }
  })
}

// 头像上传前的验证
const beforeAvatarUpload = (rawFile) => {
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  const maxSize = 5 * 1024 * 1024 // 5MB

  if (!allowedTypes.includes(rawFile.type)) {
    ElMessage.error('头像必须是 JPG/PNG/GIF/WEBP 格式!')
    return false
  }
  if (rawFile.size > maxSize) {
    ElMessage.error('头像大小不能超过 5MB!')
    return false
  }
  
  return true
}

// 自定义上传头像方法
const customUploadAvatar = async (options) => {
  const formData = new FormData()
  formData.append('avatar', options.file)

  // 获取 token - 优先使用 authStore.token
  const token = authStore.token || localStorage.getItem('token')
  
  if (!token || token === 'null' || token === null || token === undefined) {
    console.error('认证token无效或为空:', token, '登录状态:', authStore.isLoggedIn);
    ElMessage.error('认证信息无效，请重新登录')
    router.push('/login');
    return;
  }
  
  try {
    console.log('发送头像上传请求，token长度:', token ? token.length : 'N/A');
    
    const response = await fetch('/api/v1/upload-avatar/', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.status === 401) {
      console.error('认证失败，可能token已过期');
      ElMessage.error('登录已过期，请重新登录')
      authStore.logout();
      router.push('/login');
      return;
    }

    let result = {};
    try {
      result = await response.json();
    } catch (jsonError) {
      result = { error: `服务器返回非JSON格式: ${response.status}` };
    }

    if (response.ok) {
      ElMessage.success(result.message || '头像上传成功')
      console.log('头像上传成功，新头像URL:', result.avatar_url)
      profileForm.avatar = result.avatar_url
      
      // 重新获取用户信息，确保状态同步
      await authStore.fetchUserInfo()
      console.log('已重新获取用户信息')
      
      // 手动触发一个自定义事件，通知其他组件头像已更新
      window.dispatchEvent(new CustomEvent('avatar-updated', { 
        detail: { avatarUrl: result.avatar_url } 
      }))
      
      console.log('已触发头像更新事件，URL:', result.avatar_url)
      
      return result
    } else {
      ElMessage.error(result.error || `上传失败，状态码: ${response.status}`)
      return;
    }
  } catch (error) {
    console.error('头像上传错误详情:', error);
    ElMessage.error('头像上传失败，请重试')
    return;
  }
}

// 删除头像
const removeAvatar = async () => {
  try {
    const confirmed = await ElMessageBox.confirm(
      '确定要删除头像吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await api.delete('/api/v1/avatar/', { timeout: 10000 })
    profileForm.avatar = ''

    if (authStore.user) {
      authStore.user.avatar = ''
    }
    
    ElMessage.success('头像已删除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

// 保存AI设置
const saveAiSettings = async () => {
  savingAi.value = true
  try {
    await api.put('/ai-settings/', aiSettings, { timeout: 10000 })
    settingsStore.updateAISettings(aiSettings)
    ElMessage.success('AI设置保存成功')
  } catch (error) {
    ElMessage.error('AI设置保存失败：' + error.message)
  } finally {
    savingAi.value = false
  }
}

// 保存外观设置
const saveAppearanceSettings = async () => {
  savingAppearance.value = true
  try {
    await api.put('/appearance-settings/', appearanceSettings, { timeout: 10000 })
    settingsStore.updatePreferences(appearanceSettings)
    changeTheme(appearanceSettings.theme)
    ElMessage.success('外观设置保存成功')
  } catch (error) {
    ElMessage.error('外观设置保存失败：' + error.message)
  } finally {
    savingAppearance.value = false
  }
}

// 保存隐私设置
const savePrivacySettings = async () => {
  savingPrivacy.value = true
  try {
    await api.put('/privacy-settings/', privacySettings, { timeout: 10000 })
    settingsStore.updateSettings({ privacy: privacySettings })
    ElMessage.success('隐私设置保存成功')
  } catch (error) {
    ElMessage.error('隐私设置保存失败：' + error.message)
  } finally {
    savingPrivacy.value = false
  }
}

// 更改主题
const changeTheme = (theme) => {
  const html = document.documentElement
  html.classList.remove('light-theme', 'dark-theme', 'light', 'dark')
  
  if (theme === 'auto') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      html.classList.add('dark-theme', 'dark')
    } else {
      html.classList.add('light-theme', 'light')
    }
  } else if (theme === 'dark') {
    html.classList.add('dark-theme', 'dark')
  } else {
    html.classList.add('light-theme', 'light')
  }
}

// 组件挂载时初始化数据
onMounted(async () => {
  if (!authStore.token && !authStore.user) {
    router.push('/login')
    return
  }
  
  initSettingsData()
  updateSettingsInfo()
  initData()
})
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

/* 顶部导航栏 */
.settings-header {
  max-width: 1200px;
  margin: 0 auto 20px;
  background: #ffffff;
  border-radius: 16px;
  padding: 16px 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 24px;
  color: #333;
}

.header-title .el-icon {
  font-size: 28px;
  color: #667eea;
}

/* 主容器 */
.settings-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 20px;
  min-height: calc(100vh - 140px);
}

/* 左侧侧边栏 */
.settings-sidebar {
  width: 280px;
  flex-shrink: 0;
}

.user-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-icon {
  font-size: 40px;
  color: white;
}

.user-name {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.user-email {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.settings-menu {
  background: #ffffff;
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.settings-menu :deep(.el-menu-item) {
  height: 56px;
  line-height: 56px;
  font-size: 15px;
  border-radius: 0;
  margin: 0;
}

.settings-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.settings-menu :deep(.el-menu-item:hover) {
  background: rgba(102, 126, 234, 0.1);
}

.settings-menu :deep(.el-menu-item.is-active:hover) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.settings-menu :deep(.el-icon) {
  font-size: 20px;
  margin-right: 12px;
}

/* 右侧内容区域 */
.settings-content {
  flex: 1;
  min-width: 0;
}

.content-section {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header {
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0 0 8px;
  font-size: 24px;
  color: white;
  font-weight: 600;
}

.section-desc {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.settings-card {
  background: #ffffff;
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.settings-card :deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 16px 20px;
}

.card-header {
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

.settings-form {
  padding: 20px 0;
}

.settings-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #555;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
  display: block;
}

/* 头像上传区域 */
.avatar-upload-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
}

.avatar-preview {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-placeholder .el-icon {
  font-size: 48px;
  color: white;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  color: white;
}

.avatar-overlay:hover {
  opacity: 1;
}

.avatar-overlay .el-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.avatar-overlay span {
  font-size: 12px;
}

.avatar-actions {
  display: flex;
  gap: 12px;
}

.upload-tip {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

/* 账户信息 */
.account-info {
  padding: 8px 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #ebeef5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 500;
  color: #666;
}

.info-value {
  color: #333;
}

/* 安全设置 */
.security-card {
  margin-top: 20px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.security-info h4 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #333;
}

.security-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

/* API Key 输入框 */
.api-key-input {
  max-width: 400px;
}

/* 语言选项 */
.lang-option {
  font-size: 14px;
}

/* 隐私设置 */
.privacy-list {
  padding: 8px 0;
}

.privacy-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
}

.privacy-item:first-child {
  padding-top: 8px;
}

.privacy-info h4 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #333;
}

.privacy-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.privacy-actions {
  padding: 16px 0 8px;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .settings-container {
    flex-direction: column;
  }
  
  .settings-sidebar {
    width: 100%;
  }
  
  .settings-menu {
    display: flex;
    overflow-x: auto;
  }
  
  .settings-menu :deep(.el-menu-item) {
    flex-shrink: 0;
  }
}

/* 深色模式适配 */
:global(.dark) .settings-page {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

:global(.dark) .settings-header,
:global(.dark) .user-card,
:global(.dark) .settings-menu,
:global(.dark) .settings-card {
  background: #1e1e28;
}

:global(.dark) .header-title,
:global(.dark) .user-name,
:global(.dark) .card-header,
:global(.dark) .security-info h4,
:global(.dark) .privacy-info h4,
:global(.dark) .info-value {
  color: #e0e0e0;
}

:global(.dark) .user-email,
:global(.dark) .section-desc,
:global(.dark) .form-hint,
:global(.dark) .security-info p,
:global(.dark) .privacy-info p,
:global(.dark) .info-label {
  color: #a0a0a0;
}

:global(.dark) .settings-form :deep(.el-form-item__label) {
  color: #c0c0c0;
}

/* 弹窗样式 - 纯色背景 */
:deep(.el-dialog) {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

:deep(.el-dialog__header) {
  background: #ffffff;
  border-bottom: 1px solid #ebeef5;
  border-radius: 16px 16px 0 0;
  padding: 20px;
}

:deep(.el-dialog__title) {
  color: #333;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  background: #ffffff;
  padding: 20px;
}

:deep(.el-dialog__footer) {
  background: #ffffff;
  border-top: 1px solid #ebeef5;
  border-radius: 0 0 16px 16px;
  padding: 16px 20px;
}

/* 深色模式弹窗 */
:global(.dark) :deep(.el-dialog),
:global(.dark) :deep(.el-dialog__header),
:global(.dark) :deep(.el-dialog__body),
:global(.dark) :deep(.el-dialog__footer) {
  background: #1e1e28;
}

:global(.dark) :deep(.el-dialog__title) {
  color: #e0e0e0;
}

:global(.dark) :deep(.el-dialog__header),
:global(.dark) :deep(.el-dialog__footer) {
  border-color: #333;
}
</style>
