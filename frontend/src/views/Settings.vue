<template>
  <div class="settings-container">
    <div class="settings-header">
      <h1>设置</h1>
      <p>管理您的账户和偏好设置</p>
    </div>
    
    <div class="settings-content">
      <!-- 左侧导航菜单 -->
      <div class="settings-sidebar">
        <el-menu 
          :default-active="activeTab" 
          class="settings-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="profile">
            <el-icon><User /></el-icon>
            <span>个人资料</span>
          </el-menu-item>
          <el-menu-item index="ai">
            <el-icon><Cpu /></el-icon>
            <span>AI模型</span>
          </el-menu-item>
          <el-menu-item index="preferences">
            <el-icon><Setting /></el-icon>
            <span>偏好</span>
          </el-menu-item>
          <el-menu-item index="chat">
            <el-icon><ChatDotRound /></el-icon>
            <span>聊天</span>
          </el-menu-item>
          <el-menu-item index="privacy">
            <el-icon><Lock /></el-icon>
            <span>隐私</span>
          </el-menu-item>
          <el-menu-item index="tools">
            <el-icon><Tools /></el-icon>
            <span>工具</span>
          </el-menu-item>
        </el-menu>
      </div>
      
      <!-- 右侧内容区域 -->
      <div class="settings-main">
        <!-- 个人资料设置 -->
        <div v-if="activeTab === 'profile'" class="settings-section">
          <el-card>
            <template #header>
              <div class="section-header">
                <el-icon><User /></el-icon>
                <span>个人资料</span>
              </div>
            </template>
            
            <el-form :model="profileForm" label-width="100px">
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
                <el-button type="primary" @click="saveProfile">保存个人资料</el-button>
                <el-button @click="resetProfile">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- AI模型设置 -->
        <div v-if="activeTab === 'ai'" class="settings-section">
          <el-card>
            <template #header>
              <div class="section-header">
                <el-icon><Cpu /></el-icon>
                <span>AI模型</span>
              </div>
            </template>
            
            <el-form :model="aiSettings" label-width="120px">
              <el-form-item label="默认AI模型">
                <el-select v-model="aiSettings.defaultModel" placeholder="请选择默认AI模型">
                  <el-option label="DeepSeek-V3" value="deepseek-v3"></el-option>
                  <el-option label="GPT-4" value="gpt-4"></el-option>
                  <el-option label="GPT-3.5" value="gpt-3.5"></el-option>
                  <el-option label="Claude" value="claude"></el-option>
                  <el-option label="文心一言" value="wenxin"></el-option>
                  <el-option label="通义千问" value="qwen"></el-option>
                  <el-option label="Llama 3" value="llama"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="API密钥">
                <el-input
                  v-model="aiSettings.apiKey"
                  type="password"
                  placeholder="请输入API密钥"
                  show-password
                />
                <span class="form-tip">密钥将安全存储，不会泄露</span>
              </el-form-item>
              
              <el-form-item label="温度设置">
                <el-slider
                  v-model="aiSettings.temperature"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  show-stops
                />
                <div class="slider-labels">
                  <span>精确</span>
                  <span>平衡</span>
                  <span>创意</span>
                </div>
              </el-form-item>
              
              <el-form-item label="最大回复长度">
                <el-input-number
                  v-model="aiSettings.maxTokens"
                  :min="100"
                  :max="4000"
                  :step="100"
                />
                <span class="form-tip">控制AI回复的最大长度</span>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveAISettings">保存AI设置</el-button>
                <el-button @click="resetAISettings">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 偏好设置 -->
        <div v-if="activeTab === 'preferences'" class="settings-section">
          <el-card>
            <template #header>
              <div class="section-header">
                <el-icon><Setting /></el-icon>
                <span>偏好</span>
              </div>
            </template>
            
            <el-form :model="preferences" label-width="120px">
              <el-form-item label="主题模式">
                <el-radio-group v-model="preferences.theme">
                  <el-radio label="light">浅色</el-radio>
                  <el-radio label="dark">深色</el-radio>
                  <el-radio label="auto">自动</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="语言">
                <el-select v-model="preferences.language" placeholder="请选择语言">
                  <el-option label="中文" value="zh"></el-option>
                  <el-option label="English" value="en"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="消息通知">
                <el-switch v-model="preferences.notifications" />
                <span class="form-tip">开启后接收新消息通知</span>
              </el-form-item>
              
              <el-form-item label="声音提示">
                <el-switch v-model="preferences.sound" />
                <span class="form-tip">开启后播放消息提示音</span>
              </el-form-item>
              
              <el-form-item label="自动保存">
                <el-switch v-model="preferences.autoSave" />
                <span class="form-tip">自动保存对话记录</span>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="savePreferences">保存偏好设置</el-button>
                <el-button @click="resetPreferences">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 聊天设置 -->
        <div v-if="activeTab === 'chat'" class="settings-section">
          <el-card>
            <template #header>
              <div class="section-header">
                <el-icon><ChatDotRound /></el-icon>
                <span>聊天</span>
              </div>
            </template>
            
            <el-form :model="chatSettings" label-width="120px">
              <el-form-item label="自动滚动">
                <el-switch v-model="chatSettings.autoScroll" />
                <span class="form-tip">新消息时自动滚动到底部</span>
              </el-form-item>
              
              <el-form-item label="显示时间戳">
                <el-switch v-model="chatSettings.showTimestamps" />
                <span class="form-tip">显示消息发送时间</span>
              </el-form-item>
              
              <el-form-item label="Markdown渲染">
                <el-switch v-model="chatSettings.markdownRendering" />
                <span class="form-tip">启用Markdown格式渲染</span>
              </el-form-item>
              
              <el-form-item label="打字指示器">
                <el-switch v-model="chatSettings.typingIndicator" />
                <span class="form-tip">显示对方正在输入状态</span>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveChatSettings">保存聊天设置</el-button>
                <el-button @click="resetChatSettings">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 隐私设置 -->
        <div v-if="activeTab === 'privacy'" class="settings-section">
          <el-card>
            <template #header>
              <div class="section-header">
                <el-icon><Lock /></el-icon>
                <span>隐私</span>
              </div>
            </template>
            
            <el-form :model="privacySettings" label-width="120px">
              <el-form-item label="保存对话记录">
                <el-switch v-model="privacySettings.saveConversations" />
                <span class="form-tip">保存聊天记录到本地</span>
              </el-form-item>
              
              <el-form-item label="数据分析">
                <el-switch v-model="privacySettings.analytics" />
                <span class="form-tip">帮助改进产品体验</span>
              </el-form-item>
              
              <el-form-item label="数据收集">
                <el-switch v-model="privacySettings.dataCollection" />
                <span class="form-tip">收集匿名使用数据</span>
              </el-form-item>
              
              <el-form-item label="自动删除">
                <el-select v-model="privacySettings.deleteAfter" placeholder="选择自动删除时间">
                  <el-option label="7天后" value="7d"></el-option>
                  <el-option label="30天后" value="30d"></el-option>
                  <el-option label="90天后" value="90d"></el-option>
                  <el-option label="永不删除" value="never"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="savePrivacySettings">保存隐私设置</el-button>
                <el-button @click="resetPrivacySettings">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 设置工具 -->
        <div v-if="activeTab === 'tools'" class="settings-section">
          <el-card>
            <template #header>
              <div class="section-header">
                <el-icon><Tools /></el-icon>
                <span>工具</span>
              </div>
            </template>
            
            <div class="tools-container">
              <!-- 导入导出设置 -->
              <div class="tool-section">
                <h3 class="tool-title">导入导出设置</h3>
                <div class="tool-actions">
                  <el-button type="primary" @click="exportSettings" icon="Download">
                    导出设置
                  </el-button>
                  <el-upload
                    action=""
                    :show-file-list="false"
                    :before-upload="beforeImportSettings"
                    accept=".json"
                  >
                    <el-button type="success" icon="Upload">导入设置</el-button>
                  </el-upload>
                </div>
                <p class="tool-description">将当前设置导出为JSON文件，或从文件导入设置</p>
              </div>

              <!-- 重置设置 -->
              <div class="tool-section">
                <h3 class="tool-title">重置设置</h3>
                <div class="tool-actions">
                  <el-button type="warning" @click="validateSettings" icon="Check">
                    验证设置
                  </el-button>
                  <el-button type="danger" @click="showResetDialog" icon="Refresh">
                    重置所有设置
                  </el-button>
                </div>
                <p class="tool-description">验证设置的有效性或重置所有设置为默认值</p>
              </div>

              <!-- 设置信息 -->
              <div class="tool-section">
                <h3 class="tool-title">设置信息</h3>
                <div class="settings-info">
                  <div class="info-item">
                    <span class="info-label">设置版本：</span>
                    <span class="info-value">{{ settingsInfo.version }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">最后修改：</span>
                    <span class="info-value">{{ settingsInfo.lastModified }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">设置大小：</span>
                    <span class="info-value">{{ settingsInfo.size }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">验证状态：</span>
                    <el-tag :type="settingsInfo.valid ? 'success' : 'danger'">
                      {{ settingsInfo.valid ? '有效' : '无效' }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings'
import { User, Cpu, Setting, ChatDotRound, Lock, Tools, Download, Upload, Check, Refresh } from '@element-plus/icons-vue'

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
  avatar: '',
  bio: ''
})

// AI设置表单
const aiSettings = reactive({
  defaultModel: 'deepseek-v3',
  apiKey: '',
  temperature: 0.7,
  maxTokens: 1000
})

// 偏好设置表单
const preferences = reactive({
  theme: 'light',
  language: 'zh',
  notifications: true,
  sound: true,
  autoSave: true
})

// 聊天设置表单
const chatSettings = reactive({
  autoScroll: true,
  showTimestamps: true,
  markdownRendering: true,
  typingIndicator: true
})

// 隐私设置表单
const privacySettings = reactive({
  saveConversations: true,
  analytics: false,
  dataCollection: false,
  deleteAfter: '30d'
})

// 处理菜单选择
const handleMenuSelect = (index) => {
  router.push({ 
    path: '/settings', 
    query: { tab: index } 
  })
}

// 初始化设置数据
const initSettingsData = () => {
  // 从设置存储加载数据
  const settings = settingsStore.settings
  
  // 个人资料
  Object.assign(profileForm, settings.profile)
  
  // AI设置
  Object.assign(aiSettings, settings.ai)
  
  // 偏好设置
  Object.assign(preferences, settings.preferences)
  
  // 聊天设置
  Object.assign(chatSettings, settings.chat)
  
  // 隐私设置
  Object.assign(privacySettings, settings.privacy)
}

// 保存个人资料
const saveProfile = () => {
  saving.value = true
  try {
    settingsStore.updateProfile(profileForm)
    ElMessage.success('个人资料保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 重置个人资料
const resetProfile = () => {
  settingsStore.resetSettings('profile')
  Object.assign(profileForm, settingsStore.settings.profile)
  ElMessage.success('个人资料已重置')
}

// 保存AI设置
const saveAISettings = () => {
  saving.value = true
  try {
    settingsStore.updateAISettings(aiSettings)
    ElMessage.success('AI设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 重置AI设置
const resetAISettings = () => {
  settingsStore.resetSettings('ai')
  Object.assign(aiSettings, settingsStore.settings.ai)
  ElMessage.success('AI设置已重置')
}

// 保存偏好设置
const savePreferences = () => {
  saving.value = true
  try {
    settingsStore.updatePreferences(preferences)
    ElMessage.success('偏好设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 重置偏好设置
const resetPreferences = () => {
  settingsStore.resetSettings('preferences')
  Object.assign(preferences, settingsStore.settings.preferences)
  ElMessage.success('偏好设置已重置')
}

// 保存聊天设置
const saveChatSettings = () => {
  saving.value = true
  try {
    settingsStore.updateSettings({ chat: chatSettings })
    ElMessage.success('聊天设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 重置聊天设置
const resetChatSettings = () => {
  settingsStore.resetSettings('chat')
  Object.assign(chatSettings, settingsStore.settings.chat)
  ElMessage.success('聊天设置已重置')
}

// 保存隐私设置
const savePrivacySettings = () => {
  saving.value = true
  try {
    settingsStore.updateSettings({ privacy: privacySettings })
    ElMessage.success('隐私设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 重置隐私设置
const resetPrivacySettings = () => {
  settingsStore.resetSettings('privacy')
  Object.assign(privacySettings, settingsStore.settings.privacy)
  ElMessage.success('隐私设置已重置')
}

// 设置信息
const settingsInfo = reactive({
  version: '1.0.0',
  lastModified: '',
  size: '0 KB',
  valid: true
})

// 更新设置信息
const updateSettingsInfo = () => {
  const settings = settingsStore.settings
  const settingsStr = JSON.stringify(settings)
  
  settingsInfo.size = `${Math.round(settingsStr.length / 1024 * 100) / 100} KB`
  
  // 获取最后修改时间
  const savedSettings = localStorage.getItem('userSettings')
  if (savedSettings) {
    const lastModified = new Date()
    settingsInfo.lastModified = lastModified.toLocaleString('zh-CN')
  }
  
  // 验证设置
  const errors = settingsStore.validateSettings()
  settingsInfo.valid = errors.length === 0
}

// 导出设置
const exportSettings = () => {
  try {
    settingsStore.exportSettings()
    ElMessage.success('设置导出成功')
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

// 导入设置前的验证
const beforeImportSettings = (file) => {
  const isJSON = file.type === 'application/json' || file.name.endsWith('.json')
  if (!isJSON) {
    ElMessage.error('请选择JSON格式的文件')
    return false
  }
  
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  
  importSettings(file)
  return false // 阻止默认上传行为
}

// 导入设置
const importSettings = async (file) => {
  try {
    await settingsStore.importSettings(file)
    ElMessage.success('设置导入成功')
    // 重新加载设置数据
    initSettingsData()
    updateSettingsInfo()
  } catch (error) {
    ElMessage.error('导入失败：' + error.message)
  }
}

// 验证设置
const validateSettings = () => {
  const errors = settingsStore.validateSettings()
  if (errors.length === 0) {
    ElMessage.success('设置验证通过，所有设置项有效')
  } else {
    ElMessage.error(`发现${errors.length}个问题：${errors.join('，')}`)
  }
  updateSettingsInfo()
}

// 显示重置确认对话框
const showResetDialog = () => {
  ElMessageBox.confirm(
    '此操作将重置所有设置为默认值，且不可恢复。确定要继续吗？',
    '重置设置确认',
    {
      confirmButtonText: '确定重置',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    }
  ).then(() => {
    resetAllSettings()
  }).catch(() => {
    ElMessage.info('已取消重置操作')
  })
}

// 重置所有设置
const resetAllSettings = () => {
  try {
    settingsStore.resetSettings()
    initSettingsData()
    updateSettingsInfo()
    ElMessage.success('所有设置已重置为默认值')
  } catch (error) {
    ElMessage.error('重置失败：' + error.message)
  }
}

// 组件挂载时初始化数据
onMounted(() => {
  initSettingsData()
  updateSettingsInfo()
})

// 初始化数据
const initData = () => {
  // 从authStore获取用户信息
  if (authStore.user) {
    profileForm.username = authStore.user.username || ''
    profileForm.email = authStore.user.email || ''
    profileForm.nickname = authStore.user.nickname || ''
    profileForm.avatar = authStore.user.avatar || ''
    profileForm.bio = authStore.user.bio || ''
  }
  
  // 从localStorage加载设置
  loadSettings()
}

// 加载设置
const loadSettings = () => {
  const savedAISettings = localStorage.getItem('aiSettings')
  const savedPreferences = localStorage.getItem('preferences')
  
  if (savedAISettings) {
    Object.assign(aiSettings, JSON.parse(savedAISettings))
  }
  
  if (savedPreferences) {
    Object.assign(preferences, JSON.parse(savedPreferences))
  }
}

// 头像上传处理
const beforeAvatarUpload = (file) => {
  const isJPG = file.type === 'image/jpeg'
  const isPNG = file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG && !isPNG) {
    ElMessage.error('头像只能是 JPG 或 PNG 格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  
  // 这里可以添加上传到服务器的逻辑
  const reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onload = () => {
    profileForm.avatar = reader.result
  }
  
  return false // 阻止自动上传
}

// 应用主题
const applyTheme = (theme) => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

onMounted(() => {
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

.settings-header {
  text-align: center;
  margin-bottom: 20px;
}

.settings-header h1 {
  font-size: 1.5rem;
  color: #303133;
  margin-bottom: 8px;
  font-weight: 600;
}

.settings-header p {
  color: #909399;
  font-size: 0.9rem;
}

.settings-content {
  display: flex;
  gap: 15px;
  min-height: 500px;
}

.settings-sidebar {
  width: 200px;
  flex-shrink: 0;
}

.settings-menu {
  border-radius: 6px;
  background: #fff;
  box-shadow: 0 1px 8px 0 rgba(0, 0, 0, 0.08);
}

.settings-menu .el-menu-item {
  height: 42px;
  line-height: 42px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  color: #606266;
}

.settings-menu .el-menu-item:hover {
  color: #409eff;
  background-color: #f5f7fa;
}

.settings-menu .el-menu-item.is-active {
  background-color: #ecf5ff;
  color: #409eff;
  border-right: 3px solid #409eff;
  font-weight: 600;
}

.settings-main {
  flex: 1;
  min-width: 0;
}

.settings-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
  font-size: 1.1rem;
}

.section-header .el-icon {
  color: #409eff;
  font-size: 1.2rem;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 15px;
}

.settings-card {
  border-radius: 6px;
  box-shadow: 0 1px 8px 0 rgba(0, 0, 0, 0.08);
}

.settings-card .el-card__header {
  background: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  padding: 12px 16px;
}

.tab-content {
  padding: 15px 0;
}

.tab-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-preview {
  border: 2px solid #e4e7ed;
}

.form-tip {
  font-size: 0.9rem;
  color: #606266;
  margin-left: 10px;
  font-weight: 500;
}

/* 表单标签样式增强 */
:deep(.el-form-item__label) {
  font-weight: 600 !important;
  color: #303133 !important;
  font-size: 0.95rem !important;
}

/* 输入框字体增强 */
:deep(.el-input__inner) {
  font-size: 0.95rem !important;
  font-weight: 500 !important;
}

/* 按钮字体增强 */
:deep(.el-button) {
  font-weight: 500 !important;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: 10px;
  }
  
  .settings-content {
    flex-direction: column;
  }
  
  .settings-sidebar {
    width: 100%;
  }
  
  .settings-menu {
    display: flex;
    overflow-x: auto;
  }
  
  .settings-menu .el-menu-item {
    flex-shrink: 0;
    min-width: 120px;
  }
}

/* 设置工具样式 */
.tools-container {
  padding: 0 20px;
}

.tool-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.tool-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.tool-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.tool-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.tool-description {
  font-size: 0.9rem;
  color: #606266;
  margin: 0;
  line-height: 1.4;
}

.settings-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  font-weight: 600;
  color: #303133;
  min-width: 90px;
  font-size: 0.95rem;
}

.info-value {
  color: #409eff;
  font-weight: 500;
  font-size: 0.95rem;
}

@media (max-width: 768px) {
  .tools-container {
    padding: 0 10px;
  }
  
  .tool-actions {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .settings-info {
    grid-template-columns: 1fr;
  }
}
</style>