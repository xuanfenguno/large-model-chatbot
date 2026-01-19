<template>
  <div class="chat-container">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">我的对话</h2>
        <el-button
          type="primary"
          size="small"
          icon="Plus"
          @click="handleNewChat"
          class="btn-primary"
        >
          新对话
        </el-button>
      </div>

      <div class="conversations-list">
        <div
          v-for="conversation in conversations"
          :key="conversation.id"
          class="conversation-item"
          :class="{ active: selectedConversationId === conversation.id }"
          @click="handleSelectConversation(conversation)"
        >
          <div class="conversation-avatar">
            <el-icon :size="24">
              <Message />
            </el-icon>
          </div>
          <div class="conversation-content">
            <div class="conversation-title">{{ conversation.title }}</div>
            <div class="conversation-time">{{ formatTime(conversation.updated_at) }}</div>
            <div class="conversation-mode">
              <el-tag size="small" :type="getModeTagType(conversation.mode)">
                {{ getModeText(conversation.mode) }}
              </el-tag>
            </div>
          </div>
          <div class="conversation-actions">
            <el-button
              type="text"
              size="small"
              icon="Delete"
              @click.stop="handleDeleteConversation(conversation.id)"
              class="delete-btn"
            />
          </div>
        </div>
      </div>

      <!-- 左侧栏底部设置区域 -->
      <div class="sidebar-footer">
        <!-- 语音助手入口 - 在上方 -->
        <el-button
          type="success"
          size="small"
          class="voice-assistant-btn"
          @click="goToVoiceChat"
          icon="Microphone"
        >
          语音助手
        </el-button>
        
        <!-- 视频通话入口 - 在下方 -->
        <el-button
          type="danger"
          size="small"
          class="video-chat-btn"
          @click="goToVideoChat"
          icon="VideoCamera"
        >
          视频通话
        </el-button>
        
        <el-dropdown @command="handleSettingsCommand" placement="top-start" class="settings-dropdown">
          <el-button
            type="text"
            size="small"
            class="settings-button"
          >
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile" icon="User">个人资料</el-dropdown-item>
              <el-dropdown-item command="ai" icon="Cpu">AI模型</el-dropdown-item>
              <el-dropdown-item command="preferences" icon="Setting">偏好设置</el-dropdown-item>
              <el-dropdown-item command="chat" icon="ChatDotRound">聊天设置</el-dropdown-item>
              <el-dropdown-item command="privacy" icon="Lock">隐私设置</el-dropdown-item>
              <el-dropdown-item command="tools" icon="Tools">设置工具</el-dropdown-item>
              <el-dropdown-item divided command="logout" icon="SwitchButton" class="logout-item">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </aside>

    <!-- 主聊天窗口 -->
    <main class="chat-main">
      <!-- 聊天头部 -->
      <header class="chat-header">
        <div class="chat-header-content">
          <!-- AI API选择器 -->
          <div class="ai-api-selector">
            <el-select
              v-model="selectedModel"
              placeholder="选择AI模型"
              size="medium"
              class="ai-model-select"
              @change="handleModelChange"
            >
              <el-option-group
                v-for="group in modelGroups"
                :key="group.label"
                :label="group.label"
              >
                <el-option
                  v-for="model in group.models"
                  :key="model.id"
                  :label="model.name"
                  :value="model.id"
                  :disabled="model.disabled"
                >
                  <span class="model-option">
                    <el-avatar :size="20" :src="model.icon" class="model-icon">
                      {{ model.name.charAt(0) }}
                    </el-avatar>
                    <span class="model-name">{{ model.name }}</span>
                    <el-tag v-if="model.tag" size="small" :type="model.tagType">
                      {{ model.tag }}
                    </el-tag>
                  </span>
                </el-option>
              </el-option-group>
            </el-select>
            
            <!-- 模型状态指示器 -->
            <div class="model-status">
              <el-tooltip :content="modelStatusText" placement="bottom">
                <el-badge :type="modelStatusType" is-dot>
                  <el-icon :size="16">
                    <Connection />
                  </el-icon>
                </el-badge>
              </el-tooltip>
            </div>
          </div>
          
          <!-- 聊天标题（居中） -->
          <div class="chat-title">
            <el-icon :size="24">
              <Message />
            </el-icon>
            <h1>{{ conversationTitle }}</h1>
          </div>
          
          <!-- 聊天模式选择器（靠右） -->
          <div class="chat-controls">
            <div class="mode-selector-wrapper">
              <el-dropdown 
                @command="handleModeChange"
                placement="bottom-end"
                trigger="click"
              >
                <el-button 
                  type="text" 
                  size="small"
                  class="mode-dropdown-button"
                >
                  <span class="mode-selector-label">聊天模式</span>
                  <el-icon class="el-icon--right">
                    <ArrowDown />
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="text" icon="ChatLineRound">文字聊天</el-dropdown-item>
                    <el-dropdown-item command="voice" icon="Microphone">语音聊天</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              
              <!-- 语音通话按钮 -->
              <el-button 
                v-if="chatMode === 'voice'"
                type="primary" 
                size="small"
                class="voice-call-button"
                @click="initiateVoiceCall"
                :disabled="isVoiceCallActive"
              >
                <el-icon><Phone /></el-icon>
                <span>{{ isVoiceCallActive ? '通话中' : '发起通话' }}</span>
              </el-button>
            </div>
          </div>
        </div>
      </header>

      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-for="(message, index) in messages" :key="message.id" class="message-item">
          <div class="message-avatar">
            <el-icon :size="20">
              <User />
            </el-icon>
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-role">{{ message.role === 'user' ? '我' : 'AI' }}</span>
              <span class="message-time">{{ formatTime(message.created_at) }}</span>
            </div>
            <div class="message-text">
              <!-- 处理加载状态 -->
              <div v-if="message.is_loading" class="loading-content">
                <el-skeleton :rows="3" animated />
              </div>
              <!-- 处理错误状态 -->
              <div v-else-if="message.error" class="error-content">
                <div class="error-message">
                  <el-icon class="error-icon"><Warning /></el-icon>
                  {{ message.content }}
                </div>
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handleRetryMessage"
                  class="retry-btn"
                >
                  重试
                </el-button>
              </div>
              <!-- 正常消息显示 -->
              <div v-else>
                <Vue3MarkdownIt :source="message.content" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <footer class="chat-footer">
        <!-- 文字聊天模式 -->
        <div v-if="chatMode === 'text'" class="input-wrapper">
          <el-input
            v-model="inputContent"
            type="textarea"
            :rows="1"
            placeholder="输入您的消息..."
            resize="none"
            @keyup.enter.exact="handleSendMessage"
            @keyup.enter.ctrl.exact="handleSendMessage"
            class="message-input"
            :autosize="{ minRows: 1, maxRows: 6 }"
            :disabled="isSending"
          >
            <template #append>
              <el-button
                type="text"
                size="small"
                icon="Plus"
                @click="handleAddAttachment"
                :disabled="isSending"
              />
            </template>
          </el-input>
          <el-button
            type="primary"
            size="large"
            icon="Paperclip"
            :loading="isSending"
            @click="handleSendMessage"
            :disabled="!inputContent.trim()"
            class="send-button"
          >
            发送
          </el-button>
        </div>
        
        <!-- 语音通话模式 -->
        <VoiceControls 
          v-else-if="chatMode === 'voice'"
          @voice-data="handleVoiceData"
          @transcription="handleVoiceTranscription"
          ref="voiceControlsRef"
        />
        

      </footer>
    </main>
    
    <!-- 语音通话组件 -->
    <VoiceCall 
      v-if="isVoiceCallActive"
      ref="voiceCallRef"
      :socket="socket"
      @call-ended="endVoiceCall"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useSettingsStore } from '@/stores/settings'
import { ElMessage, ElMessageBox } from 'element-plus'
import Vue3MarkdownIt from 'vue3-markdown-it'
import ChatModeSelector from '@/components/ChatModeSelector.vue'
import VoiceControls from '@/components/VoiceControls.vue'
import VoiceCall from '@/components/VoiceCall.vue'
import { Message, User, Setting, SwitchButton, Paperclip, Plus, Delete, Warning, Connection, ArrowDown, ChatLineRound, Microphone, Phone } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

// 响应式数据
const inputContent = ref('')
const isSending = ref(false)
const messagesContainer = ref(null)
const selectedModel = ref('deepseek-v3') // 默认模型
const models = ref([])
const chatMode = ref('text') // 聊天模式：text, voice, video
const modeSelectorRef = ref(null)
const voiceControlsRef = ref(null)

// 语音通话相关状态
const isVoiceCallActive = ref(false)
const voiceCallRef = ref(null)
const socket = ref(null) // WebSocket连接

// AI API选择器相关数据
const modelGroups = ref([
  {
    label: '开源模型',
    models: [
      { id: 'deepseek-v3', name: 'DeepSeek-V3', provider: 'DeepSeek', tag: '推荐', tagType: 'success', icon: '' },
      { id: 'qwen', name: '通义千问', provider: '阿里云', tag: '免费', tagType: 'info', icon: '' },
      { id: 'llama', name: 'Llama 3', provider: 'Meta', tag: '开源', tagType: 'warning', icon: '' }
    ]
  },
  {
    label: '商业模型',
    models: [
      { id: 'gpt-4', name: 'GPT-4', provider: 'OpenAI', tag: '智能', tagType: 'success', icon: '', disabled: false },
      { id: 'gpt-3.5', name: 'GPT-3.5', provider: 'OpenAI', tag: '快速', tagType: 'info', icon: '', disabled: false },
      { id: 'claude', name: 'Claude', provider: 'Anthropic', tag: '安全', tagType: 'warning', icon: '', disabled: false },
      { id: 'wenxin', name: '文心一言', provider: '百度', tag: '中文', tagType: 'success', icon: '', disabled: false }
    ]
  }
])

// 模型状态
const modelStatus = ref('connected') // connected, connecting, error
const modelStatusText = computed(() => {
  const statusMap = {
    connected: '模型连接正常',
    connecting: '正在连接模型...',
    error: '模型连接失败'
  }
  return statusMap[modelStatus.value] || '未知状态'
})

const modelStatusType = computed(() => {
  const typeMap = {
    connected: 'success',
    connecting: 'warning',
    error: 'danger'
  }
  return typeMap[modelStatus.value] || 'info'
})

// 计算属性
const conversations = computed(() => chatStore.conversations)
const selectedConversationId = computed(() => chatStore.selectedConversationId)
const messages = computed(() => chatStore.messages)
const conversationTitle = computed(() => chatStore.conversationTitle)

// 自动滚动到底部（优化性能）
watch(messages, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      // 使用requestAnimationFrame优化滚动性能
      requestAnimationFrame(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }
  })
}, { deep: true })

// 格式化时间
const formatTime = (timeStr) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) {
    return '刚刚'
  } else if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString()
  }
}

// 获取可用模型列表
const loadModels = async () => {
  try {
    const response = await fetch('/api/v1/models/')
    if (response.ok) {
      const data = await response.json()
      models.value = data
      // 设置默认模型
      if (models.value.length > 0) {
        selectedModel.value = models.value[0].id
      }
    }
  } catch (error) {
    console.error('获取模型列表失败:', error)
    // 默认模型列表
    models.value = [
      { id: 'deepseek-v3', name: 'DeepSeek V3', provider: 'DeepSeek' },
      { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'Anthropic' },
      { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', provider: 'OpenAI' },
      { id: 'qwen-vl-plus', name: 'Qwen VL Plus', provider: 'Alibaba Cloud' },
      { id: 'qwen-max', name: 'Qwen Max', provider: 'Alibaba Cloud' }
    ]
    selectedModel.value = 'deepseek-v3'
  }
}

// 处理新对话
const handleNewChat = async () => {
  try {
    await chatStore.createConversation()
  } catch (error) {
    ElMessage.error('创建新对话失败')
  }
}

// 处理选择对话
const handleSelectConversation = async (conversation) => {
  try {
    await chatStore.selectConversation(conversation.id)
  } catch (error) {
    ElMessage.error('加载对话消息失败')
  }
}

// 处理删除对话
const handleDeleteConversation = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个对话吗？',
      '删除提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await chatStore.deleteConversation(id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除对话失败')
    }
  }
}

// 处理发送消息（优化响应速度）
const handleSendMessage = async () => {
  if (!inputContent.value.trim() || isSending.value) {
    return
  }

  const content = inputContent.value.trim()
  inputContent.value = '' // 立即清空输入框，提升用户体验
  isSending.value = true

  try {
    // 在发送消息时传递当前选择的模型
    const response = await chatStore.sendMessage(content, null, selectedModel.value)
    
    // 如果当前是语音模式，自动播放AI回复
    if (chatMode.value === 'voice') {
      await speakText(response)
    }
  } catch (error) {
    ElMessage.error('发送消息失败')
  } finally {
    isSending.value = false
  }
}

// 文字转语音
const speakText = (text) => {
  return new Promise((resolve) => {
    if ('speechSynthesis' in window && chatMode.value === 'voice') {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'zh-CN'
      utterance.volume = 0.8
      utterance.rate = 1.0
      utterance.pitch = 1.0

      utterance.onend = () => {
        console.log('AI语音回复播放完成')
        resolve()
      }

      utterance.onerror = () => {
        console.error('语音合成错误')
        resolve()
      }

      speechSynthesis.speak(utterance)
    } else {
      resolve()
    }
  })
}

// 处理重试消息
const handleRetryMessage = async (content) => {
  if (isSending.value) {
    return
  }
  await handleSendMessage()
}

// 处理添加附件
const handleAddAttachment = () => {
  ElMessage.info('附件功能开发中...')
}



// 处理模型切换
const handleModelChange = async (modelId) => {
  console.log('模型已切换到:', modelId)
  
  // 更新模型状态为连接中
  modelStatus.value = 'connecting'
  
  try {
    // 模拟模型连接过程
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新设置存储中的默认模型
    const settingsStore = useSettingsStore()
    settingsStore.updateAISettings({ defaultModel: modelId })
    
    // 更新模型状态为已连接
    modelStatus.value = 'connected'
    
    const modelName = modelGroups.value.flatMap(g => g.models).find(m => m.id === modelId)?.name
    ElMessage.success(`模型已切换到: ${modelName}`)
    
    console.log('模型切换成功，当前模型:', modelId)
  } catch (error) {
    modelStatus.value = 'error'
    ElMessage.error('模型切换失败，请检查网络连接')
    console.error('模型切换错误:', error)
  }
}

// 处理设置命令
const handleSettingsCommand = async (command) => {
  if (command === 'logout') {
    // 处理退出登录
    try {
      await authStore.logout()
      router.push('/login')
    } catch (error) {
      ElMessage.error('退出登录失败')
    }
  } else {
    // 处理其他设置命令
    router.push(`/settings?tab=${command}`)
  }
}

// 处理设置（兼容原有调用）
const handleSettings = () => {
  router.push('/settings')
}

// 处理个人资料（兼容原有调用）
const handleProfile = () => {
  router.push('/settings?tab=profile')
}

// 处理退出登录（兼容原有调用）
const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}

// 处理模式切换
const handleModeChange = (newMode) => {
  console.log('切换到模式:', newMode)
  
  // 更新聊天模式
  chatMode.value = newMode
  
  // 根据模式显示不同的提示信息
  switch (newMode) {
    case 'text':
      ElMessage.success('已切换到文字聊天模式')
      break
    case 'voice':
      ElMessage.info('语音聊天模式 - 点击麦克风开始说话')
      // 检查WebRTC支持
      checkWebRTCSupport()
      break
  }
}

// 检查WebRTC支持
const checkWebRTCSupport = () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    ElMessage.warning('您的浏览器不支持语音通话功能，请使用Chrome、Edge等现代浏览器')
    return false
  }
  return true
}

// 发起语音通话
const initiateVoiceCall = async () => {
  if (!checkWebRTCSupport()) return
  
  try {
    // 这里需要先建立WebSocket连接
    // 简化实现：直接显示通话界面
    isVoiceCallActive.value = true
    
    // 实际项目中应该在这里建立WebSocket连接并发送通话请求
    ElMessage.info('正在发起语音通话...')
  } catch (error) {
    console.error('发起语音通话失败:', error)
    ElMessage.error('发起语音通话失败')
  }
}

// 结束语音通话
const endVoiceCall = () => {
  isVoiceCallActive.value = false
  
  // 实际项目中应该在这里关闭WebSocket连接
  if (voiceCallRef.value) {
    voiceCallRef.value.endCall()
  }
  
  ElMessage.info('通话已结束')
}

// 获取模式标签类型
const getModeTagType = (mode) => {
  const typeMap = {
    'text': 'primary',
    'voice': 'success', 
    'video': 'warning'
  }
  return typeMap[mode] || 'info'
}

// 获取模式显示文本
const getModeText = (mode) => {
  const textMap = {
    'text': '文字',
    'voice': '语音',
    'video': '视频'
  }
  return textMap[mode] || '未知'
}

// 处理语音数据
const handleVoiceData = (voiceData) => {
  console.log('收到语音数据:', voiceData)
  
  if (voiceData.type === 'speech-completed') {
    // 用户说完，自动发送消息并等待AI回复
    inputContent.value = voiceData.text
    handleSendMessage()
  } else if (voiceData.type === 'recording-started') {
    ElMessage.info('语音识别已开始，请说话...')
  } else if (voiceData.type === 'recording-ended') {
    console.log('语音识别已结束')
  } else if (voiceData.type === 'recording-error') {
    ElMessage.error(`语音识别错误: ${voiceData.error}`)
  }
}

// 处理语音转文字结果
const handleVoiceTranscription = (text) => {
  console.log('语音转文字结果:', text)
  // 实时显示语音转文字结果
  // 这里不需要设置输入内容，因为speech-completed事件会处理
}

// 跳转到语音聊天界面
const goToVoiceChat = () => {
  router.push('/voice-chat')
}

// 跳转到视频聊天界面
const goToVideoChat = () => {
  router.push('/video-chat')
}

// 监听聊天模式变化
watch(chatMode, (newMode, oldMode) => {
  if (oldMode === 'voice' && newMode !== 'voice') {
    // 如果从语音模式切换到其他模式，停止录音
    if (voiceControlsRef.value) {
      voiceControlsRef.value.stopRecordingExternal()
    }
  }
})

// 检查用户认证状态
const checkAuth = () => {
  console.log('检查认证状态:', authStore.isLoggedIn)
  console.log('token:', localStorage.getItem('token'))
  console.log('user:', localStorage.getItem('user'))
  
  if (!authStore.isLoggedIn) {
    console.log('认证失败，跳转到登录页面')
    ElMessage.warning('请先登录')
    router.push('/login')
    return false
  }
  console.log('认证成功')
  return true
}

// 页面加载时获取对话列表（优化加载）
const loadData = async () => {
  // 先检查认证状态
  if (!checkAuth()) {
    return
  }
  
  try {
    await chatStore.fetchConversations()
    await loadModels() // 加载模型列表
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载对话列表失败')
  }
}

// 页面挂载时调用
onMounted(() => {
  // 检查认证状态
  if (!checkAuth()) {
    return
  }
  
  // 加载数据
  loadData()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.sidebar {
  width: 300px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
}

.sidebar-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.conversation-item:hover {
  background: #e9ecef;
}

.conversation-item.active {
  background: #e3f2fd;
  border: 1px solid #bbdefb;
}

.conversation-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #667eea;
  border-radius: 50%;
  color: white;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.conversation-content {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #303133;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-time {
  font-size: 0.75rem;
  color: #909399;
}

.conversation-mode {
  margin-top: 0.25rem;
}

.conversation-actions {
  margin-left: 0.5rem;
}

/* 左侧栏底部设置区域 */
.sidebar-footer {
  border-top: 1px solid #ebeef5;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 语音助手按钮 - 在上方 */
.voice-assistant-btn {
  width: calc(100% - 1rem);
  height: 36px;
  background: linear-gradient(45deg, #ff6b6b, #ffd93d);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-weight: 600;
  font-size: 12px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  margin: 0 0.5rem;
}

.voice-assistant-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
  border-color: rgba(255, 255, 255, 0.6);
}

/* 视频通话按钮 - 在下方 */
.video-chat-btn {
  width: calc(100% - 1rem);
  height: 36px;
  background: linear-gradient(45deg, #ff416c, #ff4b2b);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-weight: 600;
  font-size: 12px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  margin: 0 0.5rem;
}

.video-chat-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 65, 108, 0.3);
  border-color: rgba(255, 255, 255, 0.6);
}

.settings-dropdown {
  width: auto;
}

.settings-button {
  width: calc(100% - 1rem);
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  background: white;
  transition: all 0.3s ease;
  margin: 0 0.5rem;
}

.settings-button:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.settings-button .el-icon {
  color: #606266;
  font-size: 14px;
  margin-right: 4px;
}

.settings-button span {
  font-size: 12px;
  color: #303133;
}

/* 设置菜单项字体提亮 */
:deep(.el-dropdown-menu__item) {
  font-weight: 500 !important;
  color: #303133 !important;
  font-size: 14px !important;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #f5f7fa !important;
  color: #409eff !important;
}

:deep(.el-dropdown-menu__item .el-icon) {
  color: #606266 !important;
  font-size: 16px !important;
}

:deep(.el-dropdown-menu__item:hover .el-icon) {
  color: #409eff !important;
}

/* 退出登录菜单项特殊样式 */
.logout-item {
  color: #f56c6c !important;
  font-weight: 600 !important;
}

.logout-item:hover {
  background-color: #fef0f0 !important;
  color: #f56c6c !important;
}

.delete-btn {
  color: #f56c6c;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin: 1rem;
  overflow: hidden;
}

.chat-header {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #ebeef5;
}

.chat-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.chat-header-left {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
}

.ai-api-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
  padding: 6px 10px;
  border: 1px solid #e4e7ed;
  position: static;
  z-index: 10;
  height: 36px;
  box-sizing: border-box;
}

.ai-model-select {
  width: 160px;
}

.ai-model-select :deep(.el-input__inner) {
  font-size: 0.95rem;
  font-weight: 500;
  color: #303133;
}

.ai-model-select :deep(.el-select__placeholder) {
  color: #606266;
  font-weight: 500;
}

.model-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-icon {
  flex-shrink: 0;
}

.model-name {
  flex: 1;
}

.model-status {
  display: flex;
  align-items: center;
}

.model-status .el-badge {
  cursor: pointer;
}

.model-status .el-icon {
  color: #67c23a;
}

.model-status .el-badge--warning .el-icon {
  color: #e6a23c;
}

.model-status .el-badge--danger .el-icon {
  color: #f56c6c;
}

.chat-title {
  display: flex;
  align-items: center;
  color: #303133;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.chat-title h1 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0.5rem;
}

.chat-controls {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.mode-selector-wrapper {
  position: static;
  z-index: 10;
}

.mode-dropdown-button {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  padding: 6px 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  height: 36px;
}

.mode-dropdown-button:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.mode-selector-label {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.mode-dropdown-button .el-icon {
  color: #909399;
  font-size: 14px;
}

.voice-call-button {
  margin-left: 8px;
  background: #67c23a;
  border-color: #67c23a;
}

.voice-call-button:hover:not(:disabled) {
  background: #85ce61;
  border-color: #85ce61;
}

.voice-call-button:disabled {
  background: #c2e7b0;
  border-color: #c2e7b0;
  cursor: not-allowed;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.9);
}

.message-item {
  display: flex;
  margin-bottom: 1.5rem;
}

.message-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #667eea;
  border-radius: 50%;
  color: white;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.message-role {
  font-size: 0.9rem;
  font-weight: 600;
  color: #303133;
}

.message-time {
  font-size: 0.75rem;
  color: #909399;
}

.message-text {
  font-size: 0.95rem;
  color: #606266;
  line-height: 1.6;
}

.message-text :deep(pre) {
  background: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  overflow-x: auto;
}

.message-text :deep(code) {
  background: #f8f9fa;
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
  font-family: monospace;
}

.message-text :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding-left: 1rem;
  margin: 0.5rem 0;
  color: #606266;
  font-style: italic;
}

.message-text :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.input-container {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-top: 1px solid #ebeef5;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #000000;
  resize: none;
  background: rgba(255, 255, 255, 0.95);
  height: 48px;
  line-height: 1.5;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  letter-spacing: 0.5px;
}

.message-input::placeholder {
  color: #606266;
  font-weight: 500;
  font-size: 1rem;
}

.message-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.send-button {
  padding: 0.75rem 1.5rem;
  height: 48px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:hover {
  background: #5a6fd8;
}

.send-button:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.video-controls-placeholder {
  padding: 1rem;
}

.video-redirect-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
}

.redirect-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.redirect-btn {
  background: linear-gradient(45deg, #ff416c, #ff4b2b);
  border: none;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
}

.redirect-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 65, 108, 0.3);
}

.back-btn {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  border: none;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
}

.feature-list {
  text-align: left;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-width: 400px;
}

.feature-list h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-weight: 600;
}

.feature-list ul {
  margin: 0;
  padding-left: 20px;
}

.feature-list li {
  margin-bottom: 8px;
  color: #606266;
  font-size: 0.95rem;
}

.feature-list li:last-child {
  margin-bottom: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1.1rem;
  text-align: center;
}
</style>