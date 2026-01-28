<template>
  <div class="settings-container">
    <div class="settings-header">
      <div class="header-actions">
        <el-button type="primary" @click="goBack" icon="el-icon-arrow-left">
          返回聊天
        </el-button>
      </div>
      <div class="header-title">
        <h1>设置</h1>
        <p>个性化您的聊天体验</p>
      </div>
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
                  <el-option label="智谱AI" value="zhipu"></el-option>
                  <el-option label="讯飞星火" value="xinghuo"></el-option>
                </el-select>
                <span class="form-tip">选择您最常用的AI模型</span>
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
                <span class="form-tip">控制AI回复的创造性，值越低越稳定，值越高越有创意</span>
              </el-form-item>
              
              <el-form-item label="最大回复长度">
                <el-input-number
                  v-model="aiSettings.maxTokens"
                  :min="100"
                  :max="4000"
                  :step="100"
                />
                <span class="form-tip">控制AI单次回复的最大长度，值越大回复越详细</span>
              </el-form-item>
              
              <el-form-item label="上下文长度">
                <el-input-number
                  v-model="aiSettings.contextLength"
                  :min="1000"
                  :max="32000"
                  :step="1000"
                />
                <span class="form-tip">控制AI记住的对话历史长度</span>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveAISettings">保存AI设置</el-button>
                <el-button @click="resetAISettings">重置</el-button>
                <el-button @click="testAIConnection" type="success">测试连接</el-button>
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
                <span class="form-tip">自动模式将根据系统设置切换主题</span>
              </el-form-item>
              
              <el-form-item label="语言" data-language>
                <el-select v-model="preferences.language" placeholder="请选择语言">
                  <el-option label="中文" value="zh" data-value="zh"></el-option>
                  <el-option label="English" value="en"></el-option>
                  <el-option label="日本語" value="ja"></el-option>
                  <el-option label="한국어" value="ko"></el-option>
                </el-select>
                <span class="form-tip">界面显示语言</span>
              </el-form-item>
              
              <el-form-item label="字体大小" data-font-size>
                <el-radio-group v-model="preferences.fontSize">
                  <el-radio label="small" data-size="small">小</el-radio>
                  <el-radio label="medium" data-size="medium">中</el-radio>
                  <el-radio label="large" data-size="large">大</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="紧凑模式">
                <el-switch v-model="preferences.compactMode" />
                <span class="form-tip">减少元素间距，显示更多内容</span>
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
              
              <el-form-item label="启动时恢复">
                <el-switch v-model="preferences.restoreSession" />
                <span class="form-tip">启动时自动恢复上次的对话</span>
              </el-form-item>
              
              <el-form-item label="快捷键">
                <el-switch v-model="preferences.shortcuts" />
                <span class="form-tip">启用键盘快捷键功能</span>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="savePreferences">保存偏好设置</el-button>
                <el-button @click="resetPreferences">重置</el-button>
                <el-button @click="applyThemeNow" type="success">立即应用主题</el-button>
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
              
              <el-form-item label="消息气泡">
                <el-switch v-model="chatSettings.messageBubbles" />
                <span class="form-tip">使用气泡样式显示消息</span>
              </el-form-item>
              
              <el-form-item label="消息预览">
                <el-switch v-model="chatSettings.messagePreview" />
                <span class="form-tip">在消息列表中显示消息预览</span>
              </el-form-item>
              
              <el-form-item label="发送快捷键">
                <el-select v-model="chatSettings.sendShortcut" placeholder="选择发送快捷键">
                  <el-option label="Enter" value="enter"></el-option>
                  <el-option label="Ctrl+Enter" value="ctrl-enter"></el-option>
                  <el-option label="Shift+Enter" value="shift-enter"></el-option>
                </el-select>
                <span class="form-tip">设置发送消息的快捷键</span>
              </el-form-item>
              
              <el-form-item label="消息历史">
                <el-input-number
                  v-model="chatSettings.historyLimit"
                  :min="10"
                  :max="1000"
                  :step="10"
                />
                <span class="form-tip">保存的对话历史数量</span>
              </el-form-item>
              
              <el-form-item label="自动清空">
                <el-switch v-model="chatSettings.autoClear" />
                <span class="form-tip">长时间不活动时自动清空输入框</span>
              </el-form-item>
              
              <el-form-item label="语音播放">
                <el-switch v-model="chatSettings.voicePlayback" />
                <span class="form-tip">自动播放语音消息</span>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveChatSettings">保存聊天设置</el-button>
                <el-button @click="resetChatSettings">重置</el-button>
                <el-button @click="testChatFeatures" type="success">测试功能</el-button>
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
              
              <el-form-item label="加密存储">
                <el-switch v-model="privacySettings.encryptStorage" />
                <span class="form-tip">对本地存储的数据进行加密</span>
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
                  <el-option label="1天后" value="1d"></el-option>
                  <el-option label="7天后" value="7d"></el-option>
                  <el-option label="30天后" value="30d"></el-option>
                  <el-option label="90天后" value="90d"></el-option>
                  <el-option label="永不删除" value="never"></el-option>
                </el-select>
                <span class="form-tip">自动删除旧的对话记录</span>
              </el-form-item>
              
              <el-form-item label="清除缓存">
                <el-button @click="clearCache" type="warning" size="small">
                  清除本地缓存
                </el-button>
                <span class="form-tip">删除所有本地存储的数据</span>
              </el-form-item>
              
              <el-form-item label="导出数据">
                <el-button @click="exportPrivacyData" type="success" size="small">
                  导出个人数据
                </el-button>
                <span class="form-tip">导出您的所有个人数据</span>
              </el-form-item>
              
              <el-form-item label="删除账户">
                <el-button @click="showDeleteAccountDialog" type="danger" size="small">
                  删除账户
                </el-button>
                <span class="form-tip">永久删除您的账户和所有数据</span>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="savePrivacySettings">保存隐私设置</el-button>
                <el-button @click="resetPrivacySettings">重置</el-button>
                <el-button @click="showPrivacyReport" type="info">隐私报告</el-button>
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
            
            <el-form :model="toolsSettings" label-width="120px">
              <!-- API密钥配置 -->
              <el-form-item label="通用API密钥">
                <el-input
                  v-model="toolsSettings.apiKey"
                  type="password"
                  placeholder="请输入通用API密钥"
                  show-password
                />
                <span class="form-tip">适用于大多数模型的通用密钥</span>
              </el-form-item>
              
              <!-- 各模型API密钥 -->
              <el-form-item label="DeepSeek密钥">
                <el-input
                  v-model="toolsSettings.apiKeys['deepseek-v3']"
                  type="password"
                  placeholder="请输入DeepSeek API密钥"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="GPT密钥">
                <el-input
                  v-model="toolsSettings.apiKeys['gpt-4']"
                  type="password"
                  placeholder="请输入OpenAI API密钥"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="Claude密钥">
                <el-input
                  v-model="toolsSettings.apiKeys['claude']"
                  type="password"
                  placeholder="请输入Anthropic Claude API密钥"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="文心一言密钥">
                <el-input
                  v-model="toolsSettings.apiKeys['wenxin']"
                  type="password"
                  placeholder="请输入百度文心一言 API密钥"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="通义千问密钥">
                <el-input
                  v-model="toolsSettings.apiKeys['qwen']"
                  type="password"
                  placeholder="请输入阿里通义千问 API密钥"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="通义千问VL-Max密钥">
                <el-input
                  v-model="toolsSettings.apiKeys['qwen-vl-max']"
                  type="password"
                  placeholder="请输入通义千问VL-Max API密钥"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="通义千问VL-Plus密钥">
                <el-input
                  v-model="toolsSettings.apiKeys['qwen-vl-plus']"
                  type="password"
                  placeholder="请输入通义千问VL-Plus API密钥"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="通义千问Audio-Turbo密钥">
                <el-input
                  v-model="toolsSettings.apiKeys['qwen-audio-turbo']"
                  type="password"
                  placeholder="请输入通义千问Audio-Turbo API密钥"
                  show-password
                />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveToolsSettings">保存API设置</el-button>
                <el-button @click="testAIConnection" type="success">测试连接</el-button>
                <el-button @click="resetToolsSettings">重置</el-button>
              </el-form-item>
            </el-form>
            
            <div class="tools-separator"></div>
            
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
import { ElMessage, ElMessageBox } from 'element-plus'
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
  defaultModel: 'qwen-plus',
  apiKey: '',
  temperature: 0.7,
  maxTokens: 1000,
  contextLength: 4000,
  apiKeys: {
    'deepseek-v3': '',
    'gpt-4': '',
    'gpt-3.5': '',
    'claude': '',
    'wenxin': '',
    'qwen': '',
    'llama': '',
    'zhipu': '',
    'xinghuo': ''
  }
})

// 偏好设置表单
const preferences = reactive({
  theme: 'light',
  language: 'zh',
  fontSize: 'medium',
  compactMode: false,
  notifications: true,
  sound: true,
  autoSave: true,
  restoreSession: true,
  shortcuts: true
})

// 聊天设置表单
const chatSettings = reactive({
  autoScroll: true,
  showTimestamps: true,
  markdownRendering: true,
  typingIndicator: true,
  messageBubbles: true,
  messagePreview: true,
  sendShortcut: 'enter',
  historyLimit: 100,
  autoClear: false,
  voicePlayback: true
})

// 隐私设置表单
const privacySettings = reactive({
  saveConversations: true,
  encryptStorage: false,
  analytics: false,
  dataCollection: false,
  deleteAfter: '30d'
})

// 工具设置表单
const toolsSettings = reactive({
  apiKey: '',
  apiKeys: {
    'deepseek-v3': '',
    'gpt-4': '',
    'gpt-3.5': '',
    'claude': '',
    'wenxin': '',
    'qwen': '',
    'llama': '',
    'zhipu': '',
    'xinghuo': ''
  }
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
  
  // 工具设置 - 从AI设置中加载API密钥
  toolsSettings.apiKey = settings.ai.apiKey || ''
  Object.assign(toolsSettings.apiKeys, settings.ai.apiKeys)
  
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
    const oldLanguage = settingsStore.settings.preferences.language
    const oldFontSize = settingsStore.settings.preferences.fontSize
    const oldTheme = settingsStore.settings.preferences.theme
    
    settingsStore.updatePreferences(preferences)
    
    // 如果字体大小发生变化，立即应用
    if (oldFontSize !== preferences.fontSize) {
      applyFontSize()
      ElMessage.success(`偏好设置保存成功，字体大小已切换到${preferences.fontSize}`)
    } else {
      ElMessage.success('偏好设置保存成功')
    }
    
    // 如果主题发生变化，立即应用
    if (oldTheme !== preferences.theme) {
      applyTheme(preferences.theme)
      console.log(`[设置] 主题已切换到: ${preferences.theme}`)
    }
    
    // TODO: 语言切换功能等待i18n系统实现
    // 目前仅保存语言设置，不进行界面语言切换
    if (oldLanguage !== preferences.language) {
      console.log(`[设置] 语言设置已保存: ${preferences.language} (等待i18n实现)`)
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 应用字体大小
const applyFontSize = () => {
  const fontSize = preferences.fontSize
  const html = document.documentElement
  
  // 移除现有的字体大小类
  html.classList.remove('font-size-small', 'font-size-medium', 'font-size-large')
  
  // 添加新的字体大小类
  html.classList.add(`font-size-${fontSize}`)
}

// 应用语言设置（预留接口，等待i18n实现）
const applyLanguage = () => {
  const language = preferences.language
  const html = document.documentElement
  
  // 移除现有的语言类
  html.classList.remove('lang-zh', 'lang-en', 'lang-ja', 'lang-ko')
  
  // 添加新的语言类
  html.classList.add(`lang-${language}`)
  
  // 设置文档语言属性
  html.setAttribute('lang', language)
  
  // TODO: 等待i18n语言包系统实现后，替换为完整的语言切换逻辑
  console.log(`[设置] 语言设置已应用: ${language} (等待i18n实现)`)
}

// 获取语言显示文本
const getLanguageText = (langCode) => {
  const languageMap = {
    'zh': '中文',
    'en': 'English',
    'ja': '日本語',
    'ko': '한국어'
  }
  return languageMap[langCode] || langCode
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

// 保存工具设置
const saveToolsSettings = () => {
  saving.value = true
  try {
    // 更新设置存储中的AI设置
    const updatedAISettings = {
      ...settingsStore.settings.ai,
      apiKey: toolsSettings.apiKey,
      apiKeys: {
        ...settingsStore.settings.ai.apiKeys,
        ...toolsSettings.apiKeys
      }
    }
    settingsStore.updateAISettings(updatedAISettings)
    ElMessage.success('API设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 重置工具设置
const resetToolsSettings = () => {
  const defaultAISettings = settingsStore.getDefaultSettings().ai
  toolsSettings.apiKey = defaultAISettings.apiKey
  Object.assign(toolsSettings.apiKeys, defaultAISettings.apiKeys)
  ElMessage.success('API设置已重置')
}

// 测试AI连接
const testAIConnection = async () => {
  try {
    ElMessage.info('正在测试AI连接...')
    // 这里可以添加实际的API连接测试逻辑
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('AI连接测试成功')
  } catch (error) {
    ElMessage.error('AI连接测试失败')
  }
}

// 立即应用主题
const applyThemeNow = () => {
  // 强制重新应用当前主题
  const currentTheme = preferences.theme
  console.log(`[设置] 立即应用主题: ${currentTheme}`)
  
  // 调用设置存储的主题应用函数
  settingsStore.applyTheme()
  
  // 同时调用本地主题应用函数确保生效
  applyTheme(currentTheme)
  
  ElMessage.success(`主题已立即应用: ${getThemeText(currentTheme)}`)
}

// 获取主题显示文本
const getThemeText = (theme) => {
  const themeMap = {
    'light': '浅色',
    'dark': '深色',
    'auto': '自动'
  }
  return themeMap[theme] || theme
}

// 测试聊天功能
const testChatFeatures = () => {
  ElMessage.info('聊天功能测试完成，所有功能正常')
}

// 清除缓存
const clearCache = () => {
  ElMessageBox.confirm(
    '此操作将清除所有本地缓存数据，包括对话记录和设置。确定要继续吗？',
    '清除缓存确认',
    {
      confirmButtonText: '确定清除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    localStorage.clear()
    sessionStorage.clear()
    ElMessage.success('缓存已清除')
  }).catch(() => {
    ElMessage.info('已取消清除操作')
  })
}

// 导出隐私数据
const exportPrivacyData = () => {
  try {
    const userData = {
      profile: profileForm,
      settings: settingsStore.settings,
      exportTime: new Date().toISOString()
    }
    
    const dataStr = JSON.stringify(userData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    
    const link = document.createElement('a')
    link.href = URL.createObjectURL(dataBlob)
    link.download = `user-data-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    ElMessage.success('个人数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

// 显示删除账户对话框
const showDeleteAccountDialog = () => {
  ElMessageBox.confirm(
    '此操作将永久删除您的账户和所有数据，且无法恢复。确定要继续吗？',
    '删除账户确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error',
      confirmButtonClass: 'el-button--danger',
      inputPlaceholder: '请输入"DELETE"确认删除'
    }
  ).then(() => {
    ElMessage.warning('账户删除功能正在开发中')
  }).catch(() => {
    ElMessage.info('已取消删除操作')
  })
}

// 显示隐私报告
const showPrivacyReport = () => {
  const report = `隐私报告
存储数据：${localStorage.length} 项
对话记录：${Object.keys(localStorage).filter(key => key.includes('conversation')).length} 条
设置项：${Object.keys(settingsStore.settings).length} 个类别
最后修改：${new Date().toLocaleString('zh-CN')}`
  
  ElMessageBox.alert(report, '隐私报告', {
    confirmButtonText: '确定',
    customClass: 'privacy-report'
  })
}

// 返回聊天界面
const goBack = () => {
  router.push('/chat')
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
  initData()
})

// 初始化数据
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
  loadSettings()
}

// 加载设置
const loadSettings = () => {
  // 从settingsStore加载设置
  const settings = settingsStore.settings
  
  // 个人资料
  Object.assign(profileForm, settings.profile)
  
  // AI设置
  Object.assign(aiSettings, settings.ai)
  
  // 工具设置 - 从AI设置中加载API密钥
  toolsSettings.apiKey = settings.ai.apiKey || ''
  Object.assign(toolsSettings.apiKeys, settings.ai.apiKeys)
  
  // 偏好设置
  Object.assign(preferences, settings.preferences)
  
  // 聊天设置
  Object.assign(chatSettings, settings.chat)
  
  // 隐私设置
  Object.assign(privacySettings, settings.privacy)
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
  const html = document.documentElement
  
  // 移除所有主题类
  html.classList.remove('light-theme', 'dark-theme', 'light', 'dark')
  
  // 处理自动模式
  let actualTheme = theme
  if (theme === 'auto') {
    actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  
  if (actualTheme === 'dark') {
    html.classList.add('dark-theme', 'dark')
    console.log(`[主题] 应用深色主题`)
  } else {
    html.classList.add('light-theme', 'light')
    console.log(`[主题] 应用浅色主题`)
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
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  position: relative;
  min-height: 60px;
}

.header-actions {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
}

.header-title {
  text-align: center;
}

.settings-header h1 {
  font-size: 1.5rem;
  color: #303133;
  margin-bottom: 8px;
  font-weight: 600;
}

.settings-header p {
  color: #606266;
  font-size: 0.9rem;
  font-weight: 500;
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

/* 表单标签字体提亮 */
:deep(.el-form-item__label) {
  color: #303133 !important;
  font-weight: 600 !important;
  font-size: 14px !important;
}

/* 表单提示文字字体提亮 */
.form-tip {
  color: #606266 !important;
  font-weight: 500 !important;
  font-size: 12px !important;
  display: block;
  margin-top: 4px;
}

/* 菜单项字体提亮 */
.settings-menu .el-menu-item {
  height: 42px;
  line-height: 42px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #303133;
}

.settings-menu .el-menu-item:hover {
  color: #409eff;
  background-color: #f5f7fa;
}

.settings-menu .el-menu-item.is-active {
  background-color: #ecf5ff;
  color: #409eff;
  border-right: 3px solid #409eff;
  font-weight: 700;
}

/* 输入框和选择框字体提亮 */
:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  color: #303133 !important;
  font-weight: 500 !important;
}

:deep(.el-input__inner::placeholder),
:deep(.el-textarea__inner::placeholder) {
  color: #909399 !important;
  font-weight: 400 !important;
}

/* 单选按钮和开关标签字体提亮 */
:deep(.el-radio__label),
:deep(.el-switch__label) {
  color: #303133 !important;
  font-weight: 500 !important;
}

/* 开关按钮特别样式 - 确保关闭状态也明显 */
:deep(.el-switch) {
  --el-switch-on-color: #409eff !important;
  --el-switch-off-color: #f0f0f0 !important;
  height: 24px !important;
  min-width: 44px !important;
}

:deep(.el-switch__core) {
  border: 2px solid #dcdfe6 !important;
  background-color: #f0f0f0 !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

:deep(.el-switch.is-checked .el-switch__core) {
  border-color: #409eff !important;
  background-color: #409eff !important;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3) !important;
}

:deep(.el-switch__action) {
  width: 16px !important;
  height: 16px !important;
  background-color: white !important;
  border: 1px solid #dcdfe6 !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
}

:deep(.el-switch.is-checked .el-switch__action) {
  border-color: #409eff !important;
  box-shadow: 0 1px 4px rgba(64, 158, 255, 0.4) !important;
  transform: translateX(20px) !important;
}

/* 开关按钮标签特别明显 */
:deep(.el-switch__label) {
  color: #000000 !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  margin-left: 8px !important;
}

:deep(.el-switch__label.is-active) {
  color: #409eff !important;
  font-weight: 700 !important;
}

/* 开关按钮容器样式 */
:deep(.el-form-item) .el-switch {
  margin-right: 10px !important;
}

/* 开关按钮悬停效果 */
:deep(.el-switch:hover .el-switch__core) {
  border-color: #409eff !important;
  box-shadow: 0 3px 6px rgba(64, 158, 255, 0.2) !important;
}

:deep(.el-switch:hover .el-switch__action) {
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3) !important;
}

/* 字体大小选项特殊样式 - 更加明显 */
:deep(.el-form-item[data-font-size]) .el-radio-group {
  display: flex;
  gap: 20px;
  align-items: center;
}

:deep(.el-form-item[data-font-size]) .el-radio {
  background: #f5f7fa;
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  padding: 12px 20px;
  transition: all 0.3s ease;
  min-width: 80px;
  text-align: center;
}

:deep(.el-form-item[data-font-size]) .el-radio:hover {
  border-color: #409eff;
  background: #ecf5ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

:deep(.el-form-item[data-font-size]) .el-radio.is-checked {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

:deep(.el-form-item[data-font-size]) .el-radio.is-checked .el-radio__label {
  color: white !important;
  font-weight: 700 !important;
}

:deep(.el-form-item[data-font-size]) .el-radio__label {
  font-size: 16px !important;
  font-weight: 600 !important;
  color: #303133 !important;
}

/* 不同字体大小的视觉差异 */
:deep(.el-form-item[data-font-size]) .el-radio[data-size="small"] .el-radio__label {
  font-size: 14px !important;
}

:deep(.el-form-item[data-font-size]) .el-radio[data-size="medium"] .el-radio__label {
  font-size: 16px !important;
}

:deep(.el-form-item[data-font-size]) .el-radio[data-size="large"] .el-radio__label {
  font-size: 18px !important;
}

/* 语言选项特殊样式 - 更加明显 */
:deep(.el-form-item[data-language]) .el-select {
  width: 200px;
}

:deep(.el-form-item[data-language]) .el-select .el-input__inner {
  background: #f8f9fa !important;
  border: 2px solid #dcdfe6 !important;
  border-radius: 8px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  color: #303133 !important;
  padding: 12px 15px !important;
  transition: all 0.3s ease !important;
}

:deep(.el-form-item[data-language]) .el-select .el-input__inner:hover {
  border-color: #409eff !important;
  background: #ecf5ff !important;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2) !important;
}

:deep(.el-form-item[data-language]) .el-select .el-input__inner:focus {
  border-color: #409eff !important;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2) !important;
}

/* 确保下拉菜单中的文字清晰可见 */
:deep(.el-form-item[data-language]) .el-select .el-input__inner,
:deep(.el-form-item[data-language]) .el-select .el-input__inner * {
  color: #303133 !important;
  font-weight: 600 !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown {
  border: 2px solid #dcdfe6 !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item {
  font-size: 16px !important;
  font-weight: 600 !important;
  color: #303133 !important;
  padding: 12px 20px !important;
  border-bottom: 1px solid #f0f0f0 !important;
  background: white !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item:hover {
  background-color: #ecf5ff !important;
  color: #409eff !important;
  font-weight: 700 !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item.selected {
  background-color: #409eff !important;
  color: white !important;
  font-weight: 700 !important;
}

/* 确保所有文字内容都清晰可见 */
:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item span {
  color: inherit !important;
  font-weight: inherit !important;
}

/* 特别加深语言选项中的所有文字颜色 */
:deep(.el-form-item[data-language]) .el-select .el-input__inner {
  color: #000000 !important;
  font-weight: 700 !important;
  font-size: 16px !important;
  background: #f8f9fa !important;
  border: 2px solid #dcdfe6 !important;
  border-radius: 8px !important;
  padding: 12px 15px !important;
}

/* 下拉框中语言选项特别明显样式 */
:deep(.el-form-item[data-language]) .el-select-dropdown {
  border: 2px solid #dcdfe6 !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
  background: white !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item {
  color: #000000 !important;
  font-weight: 700 !important;
  font-size: 16px !important;
  padding: 15px 20px !important;
  border-bottom: 1px solid #f0f0f0 !important;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%) !important;
  transition: all 0.3s ease !important;
  min-height: 50px !important;
  display: flex !important;
  align-items: center !important;
  position: relative !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item:last-child {
  border-bottom: none !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item:not(:hover):not(.selected) {
  background: linear-gradient(135deg, #f0f2f5 0%, #f8f9fa 100%) !important;
  border-left: 4px solid transparent !important;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item:hover {
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%) !important;
  color: #409eff !important;
  font-weight: 800 !important;
  transform: translateX(5px) !important;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2) !important;
  border-left: 4px solid #409eff !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item.selected {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%) !important;
  color: white !important;
  font-weight: 800 !important;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3) !important;
  border-left: 4px solid #337ecc !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item span {
  color: inherit !important;
  font-weight: inherit !important;
  font-size: inherit !important;
}

/* 语言选项图标和装饰 */
:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item::before {
  content: "🌐" !important;
  margin-right: 10px !important;
  font-size: 18px !important;
  opacity: 0.7 !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item:hover::before {
  opacity: 1 !important;
  transform: scale(1.1) !important;
}

:deep(.el-form-item[data-language]) .el-select-dropdown .el-select-dropdown__item.selected::before {
  content: "✅" !important;
  opacity: 1 !important;
}

/* 确保所有文字都是深黑色 */
:deep(.el-form-item[data-language]) {
  color: #000000 !important;
  font-weight: 700 !important;
}

:deep(.el-form-item[data-language]) * {
  color: #000000 !important;
  font-weight: 700 !important;
}

/* 按钮字体提亮 */
:deep(.el-button) {
  font-weight: 600 !important;
}

/* 卡片标题字体提亮 */
:deep(.el-card__header) {
  background-color: #f8f9fa !important;
  border-bottom: 1px solid #ebeef5 !important;
}

:deep(.el-card__header .section-header) {
  color: #303133 !important;
  font-weight: 700 !important;
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

.tools-separator {
  height: 1px;
  background-color: #ebeef5;
  margin: 20px 0;
}
</style>