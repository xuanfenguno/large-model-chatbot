<template>
  <div class="settings-container">
    <!-- 顶部导航 -->
    <div class="settings-header">
      <h2>设置</h2>
    </div>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 个人资料标签页 -->
      <el-tab-pane label="个人资料" name="profile">
        <div class="profile-section">
          <el-form :model="profileForm" label-width="100px" class="profile-form">
            <!-- 头像上传区域 -->
            <el-form-item label="头像">
              <div class="avatar-upload-section">
                <div class="current-avatar">
                  <img 
                    v-if="profileForm.avatar" 
                    :src="profileForm.avatar" 
                    alt="当前头像" 
                    class="current-avatar-img"
                  />
                  <div v-else class="avatar-placeholder">
                    <User />
                  </div>
                </div>
                <div class="avatar-upload-controls">
                  <el-upload
                    class="avatar-uploader"
                    :auto-upload="true"
                    :show-file-list="false"
                    accept=".jpg,.jpeg,.png,.gif,.webp"
                    :before-upload="beforeAvatarUpload"
                    :http-request="customUploadAvatar"
                  >
                    <el-button type="primary" plain>选择头像</el-button>
                    <p class="upload-tip">支持 JPG、PNG、GIF、WEBP 格式，大小不超过 5MB</p>
                  </el-upload>
                  <el-button 
                    v-if="profileForm.avatar" 
                    type="danger" 
                    plain 
                    @click="removeAvatar"
                    class="remove-avatar-btn"
                  >
                    删除头像
                  </el-button>
                </div>
              </div>
            </el-form-item>
            
            <el-form-item label="昵称">
              <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
            </el-form-item>
            
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱地址" />
            </el-form-item>
            
            <el-form-item label="个人简介">
              <el-input 
                v-model="profileForm.bio" 
                type="textarea" 
                :rows="3" 
                placeholder="请输入个人简介" 
              />
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="saveProfile" 
                :loading="saving"
                :disabled="saving"
              >
                {{ saving ? '保存中...' : '保存' }}
              </el-button>
              <el-button @click="resetPassword">重置密码</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 账户设置标签页 -->
      <el-tab-pane label="账户设置" name="account">
        <div class="account-section">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>账户信息</span>
              </div>
            </template>
            <div class="account-info">
              <p><strong>用户名：</strong>{{ profileForm.username }}</p>
              <p><strong>邮箱：</strong>{{ profileForm.email }}</p>
              <p><strong>注册时间：</strong>{{ profileForm.created_at || '未知' }}</p>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- AI模型设置标签页 -->
      <el-tab-pane label="AI模型设置" name="ai-models">
        <div class="ai-settings-section">
          <el-form label-width="150px">
            <el-form-item label="Qwen API Key">
              <el-input 
                v-model="aiSettings.qwenApiKey" 
                type="password" 
                placeholder="请输入Qwen API Key"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="DeepSeek API Key">
              <el-input 
                v-model="aiSettings.deepseekApiKey" 
                type="password" 
                placeholder="请输入DeepSeek API Key"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="豆包 API Key">
              <el-input 
                v-model="aiSettings.doubaoApiKey" 
                type="password" 
                placeholder="请输入豆包 API Key"
                show-password
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveAiSettings">保存AI设置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 界面设置标签页 -->
      <el-tab-pane label="界面设置" name="appearance">
        <div class="appearance-section">
          <el-form label-width="120px">
            <el-form-item label="主题模式">
              <el-radio-group v-model="appearanceSettings.theme" @change="changeTheme">
                <el-radio label="auto">自动</el-radio>
                <el-radio label="light">浅色</el-radio>
                <el-radio label="dark">深色</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="语言">
              <el-select v-model="appearanceSettings.language" placeholder="选择语言">
                <el-option label="中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveAppearanceSettings">保存外观设置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 隐私设置标签页 -->
      <el-tab-pane label="隐私设置" name="privacy">
        <div class="privacy-section">
          <el-form label-width="150px">
            <el-form-item label="聊天记录保存">
              <el-switch v-model="privacySettings.saveChatHistory" />
            </el-form-item>
            
            <el-form-item label="数据统计">
              <el-switch v-model="privacySettings.allowAnalytics" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="savePrivacySettings">保存隐私设置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings'
import { User, Cpu, Setting, ChatDotRound, Lock, Tools, Download, Upload, Check, Refresh } from '@element-plus/icons-vue'
import api from '@/utils/request'

const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const router = useRouter()
const route = useRoute()

// 从路由参数获取当前激活的标签页
const activeTab = computed(() => {
  return route.query.tab || 'profile'
})

const saving = ref(false)

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
    const response = await api.put('/api/v1/profile/', {
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

// 重置密码
const resetPassword = async () => {
  try {
    await api.post('/api/v1/password/reset/request/', {
      email: profileForm.email
    }, { timeout: 10000 })

    ElMessage.success('密码重置链接已发送到您的邮箱')
  } catch (error) {
    ElMessage.error('重置失败：' + error.message)
  }
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
  
  // 读取文件并更新预览
  const reader = new FileReader()
  reader.readAsDataURL(rawFile)
  reader.onload = () => {
    // 注意：这里不直接更新 profileForm.avatar，而是让 customUploadAvatar 处理
    // 因为我们需要让 http-request 正常工作
  }
  
  return true // 允许上传，使用自定义上传方法
}

// 自定义上传头像方法
const customUploadAvatar = async (options) => {
  const formData = new FormData()
  formData.append('avatar', options.file)

  // 在初始检查时，如果是认证无效则跳转，否则不跳转
  // 等待认证状态就绪
  if (!authStore.accessToken && authStore.isLoggedIn) {
    // 如果用户已登录但token尚未加载，等待一小段时间再检查
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  // 再次检查认证token是否有效
  if (!authStore.accessToken || authStore.accessToken === 'null' || authStore.accessToken === null || authStore.accessToken === undefined) {
    console.error('认证token无效或为空:', authStore.accessToken, '登录状态:', authStore.isLoggedIn);
    ElMessage.error('认证信息无效，请重新登录')
    // 尝试跳转到登录页面（这种情况应该跳转）
    router.push('/login');
    return; // 直接返回，不抛出错误
  }
  
  try {
    console.log('发送头像上传请求，token长度:', authStore.accessToken ? authStore.accessToken.length : 'N/A');
    console.log('认证状态:', authStore.isLoggedIn);
    console.log('用户信息:', authStore.user);
    
    const response = await fetch('/api/v1/upload-avatar/', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`
      }
    })

    console.log('收到响应，状态码:', response.status);

    // 特别处理 401 认证失败的情况
    if (response.status === 401) {
      console.error('认证失败，可能token已过期');
      ElMessage.error('登录已过期，请重新登录')
      // 清除当前认证信息
      authStore.logout();
      router.push('/login');
      return; // 直接返回，不继续执行
    }

    // 检查是否有响应体
    let result = {};
    try {
      result = await response.json();
    } catch (jsonError) {
      console.error('解析响应JSON失败:', jsonError);
      result = { error: `服务器返回非JSON格式: ${response.status}` };
    }

    console.log('响应数据:', result);

    if (response.ok) {
      ElMessage.success(result.message || '头像上传成功')
      // 更新头像URL
      profileForm.avatar = result.avatar_url
      
      // 更新auth store中的头像信息
      if (authStore.user) {
        authStore.user.avatar = result.avatar_url
      }
      
      // 强制刷新用户信息
      await authStore.fetchUserInfo();
      
      return result
    } else {
      console.error('上传失败响应:', result);
      ElMessage.error(result.error || `上传失败，状态码: ${response.status}`)
      // 对于其他类型的错误（如文件格式、大小限制等），不跳转到登录页
      return; // 直接返回，不抛出错误
    }
  } catch (error) {
    console.error('头像上传错误详情:', error);
    // 对于网络错误等其他错误，也不跳转到登录页
    ElMessage.error('头像上传失败，请重试')
    return; // 直接返回，不抛出错误
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

    // 更新auth store中的头像信息
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
  try {
    await api.put('/api/v1/ai-settings/', aiSettings, { timeout: 10000 })
    settingsStore.updateAISettings(aiSettings)
    ElMessage.success('AI设置保存成功')
  } catch (error) {
    ElMessage.error('AI设置保存失败：' + error.message)
  }
}

// 保存外观设置
const saveAppearanceSettings = async () => {
  try {
    await api.put('/api/v1/appearance-settings/', appearanceSettings, { timeout: 10000 })
    settingsStore.updatePreferences(appearanceSettings)
    changeTheme(appearanceSettings.theme)
    ElMessage.success('外观设置保存成功')
  } catch (error) {
    ElMessage.error('外观设置保存失败：' + error.message)
  }
}

// 保存隐私设置
const savePrivacySettings = async () => {
  try {
    await api.put('/api/v1/privacy-settings/', privacySettings, { timeout: 10000 })
    settingsStore.updateSettings({ privacy: privacySettings })
    ElMessage.success('隐私设置保存成功')
  } catch (error) {
    ElMessage.error('隐私设置保存失败：' + error.message)
  }
}

// 更改主题
const changeTheme = (theme) => {
  const html = document.documentElement
  // 移除所有主题类
  html.classList.remove('light-theme', 'dark-theme', 'light', 'dark')
  
  if (theme === 'auto') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      html.classList.add('dark-theme', 'dark')
      console.log(`[主题] 应用深色主题`)
    } else {
      html.classList.add('light-theme', 'light')
      console.log(`[主题] 应用浅色主题`)
    }
  } else if (theme === 'dark') {
    html.classList.add('dark-theme', 'dark')
    console.log(`[主题] 应用深色主题`)
  } else {
    html.classList.add('light-theme', 'light')
    console.log(`[主题] 应用浅色主题`)
  }
}

// 组件挂载时初始化数据
onMounted(async () => {
  // 确保认证状态已就绪后再初始化数据
  if (!authStore.token && !authStore.user) {
    // 如果没有认证信息，重定向到登录页面
    router.push('/login')
    return
  }
  
  // 等待认证信息完全加载
  if (!authStore.accessToken) {
    // 短暂延迟以确保认证状态加载完成
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  initSettingsData()
  updateSettingsInfo()
  initData()
})
</script>

<style scoped>
.settings-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 15px;
  min-height: calc(100vh - 60px);
}

/* 头像上传样式 */
.avatar-upload-section {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.current-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #f5f5f5;
  overflow: hidden;
}

.current-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 32px;
  color: #909399;
}

.avatar-upload-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.upload-tip {
  margin: 5px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.remove-avatar-btn {
  margin-top: 10px;
}

/* 表单样式 */
.profile-form {
  max-width: 600px;
}

/* 卡片样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.account-info p {
  margin: 8px 0;
  line-height: 1.6;
}
</style>