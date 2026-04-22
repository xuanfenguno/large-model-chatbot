<template>
  <div class="chat-container apple-glass">
    <!-- 侧边栏 -->
    <aside class="sidebar apple-sidebar">
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
        <!-- 功能路由入口 - 在最上方 -->
        <el-button
          type="primary"
          size="small"
          class="function-router-btn"
          @click="goToFunctionRouter"
          icon="Menu"
        >
          AI多功能助手
        </el-button>
        
        <!-- 语音助手入口 - 在中间 -->
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
              <el-dropdown-item command="settings" icon="Tools">设置工具</el-dropdown-item>
              <el-dropdown-item divided command="logout" icon="SwitchButton" class="logout-item">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </aside>

    <!-- 主聊天区域 -->
    <main class="chat-main apple-chat-area">
      <!-- 聊天头部 -->
      <header class="chat-header">
        <div class="chat-header-content">
          <!-- 左侧：AI API选择器 -->
          <div class="chat-header-left">
            <div class="ai-api-selector">
              <el-select v-model="selectedModel" placeholder="选择AI模型" size="default" class="ai-model-select" @change="handleModelChange" :loading="modelStatus === 'connecting'" filterable>
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
                    :disabled="!model.available"
                  >
                    <div class="model-option" :class="{ selected: selectedModel === model.id }">
                      <div class="model-icon-left">
                        <div class="model-icon">
                          {{ getModelIcon(model.provider) }}
                        </div>
                      </div>
                      <div class="model-content">
                        <div class="model-header">
                          <span class="model-name">{{ model.name }}</span>
                          <div class="model-badges">
                            <el-tag v-if="model.tag" :type="model.tagType" size="small" class="model-tag">
                              {{ model.tag }}
                            </el-tag>
                            <div v-if="model.available" class="status-indicator available"></div>
                            <div v-else class="status-indicator unavailable"></div>
                          </div>
                        </div>
                        <div class="model-meta">
                          <span class="provider">{{ model.provider }}</span>
                          <el-tag 
                            v-for="capability in model.capabilities.slice(0, 3)" 
                            :key="capability" 
                            size="small" 
                            type="info" 
                            class="capability-tag"
                          >
                            {{ capability }}
                          </el-tag>
                          <el-tag 
                            v-if="model.pricing" 
                            size="small" 
                            type="warning" 
                            class="pricing-tag"
                          >
                            ¥{{ (model.pricing.input + model.pricing.output).toFixed(2) }}/1M tokens
                          </el-tag>
                          <el-tag 
                            v-if="model.performance" 
                            size="small" 
                            :type="getPerformanceTagType(model.performance.speed)"
                            class="performance-tag"
                          >
                            {{ model.performance.speed }}
                          </el-tag>
                        </div>
                      </div>
                      <div class="model-arrow">
                        <el-icon :size="16" color="#94a3b8">
                          <ArrowRight />
                        </el-icon>
                      </div>
                    </div>
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
          </div>
 
          <!-- 中间：AI助手品牌（居中） -->
          <div class="chat-title">
            <div class="ai-brand">
              <div class="logo-icon">🤖</div>
              <div class="brand-name">小枫</div>
            </div>
          </div>
 
          <!-- 右侧：聊天模式选择器 -->
          <div class="chat-header-right">
            <div class="chat-controls">
              <div class="mode-selector-wrapper">
                <el-dropdown @command="handleModeChange" placement="bottom-end" trigger="click">
                  <el-button type="text" size="small" class="mode-dropdown-button">
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
                
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-for="(message, index) in messages" :key="message.id" class="message-wrapper">
          <!-- 时间显示 -->
          <div v-if="shouldShowTime(index)" class="message-time">
            {{ formatTime(message.created_at) }}
          </div>
          
          <!-- 消息项 -->
          <div :class="['message-item', message.role]">
            <div class="message-avatar">
              <template v-if="message.role === 'user'">
                <img v-if="userAvatarUrl" :src="userAvatarUrl" alt="User Avatar" class="avatar-img" />
                <el-icon v-else :size="36"><User /></el-icon>
              </template>
              <template v-else>
                <img v-if="aiAvatarUrl" :src="aiAvatarUrl" alt="AI Avatar" class="avatar-img" />
                <el-icon v-else :size="36"><ChatLineRound /></el-icon>
              </template>
            </div>
            <div class="message-bubble">
              <div v-if="message.is_loading" class="loading-content">
                <div class="ai-thinking">
                  <span class="thinking-dots">
                    <span></span><span></span><span></span>
                  </span>
                  <span class="thinking-text">AI正在思考，请稍候...</span>
                  <span v-if="message.waitTime" class="thinking-timer">{{ Math.floor(message.waitTime / 1000) }}秒</span>
                </div>
              </div>
              <div v-else-if="message.error" class="error-content">
                <div class="error-message">
                  <el-icon class="error-icon"><Warning /></el-icon>
                  {{ message.content }}
                </div>
                <el-button type="primary" size="small" @click="handleRetryMessage" class="retry-btn">
                  重试
                </el-button>
              </div>
              <div v-else>
                <MarkdownRenderer :source="message.content" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <footer class="chat-footer">
        <!-- 文字聊天模式 -->
        <div v-if="chatMode === 'text'" class="input-wrapper">
          <div class="input-with-image">
            <el-input
              v-model="inputContent"
              type="textarea"
              :rows="1"
              placeholder="说点什么吧～"
              resize="none"
              @keyup.enter.exact="handleSendMessage"
              @keyup.enter.ctrl.exact="handleSendMessage"
              class="message-input"
              :autosize="{ minRows: 1, maxRows: 6 }"
              :disabled="isSending"
            />
            <input
              type="file"
              accept="image/*"
              style="display: none"
              ref="fileInputRef"
              @change="handleFileChange"
              :disabled="isSending"
            />
            <el-button
              type="text"
              size="small"
              icon="Picture"
              @click="triggerFileInput"
              :disabled="isSending"
              class="image-upload-btn"
            />
          </div>
          
          <!-- 图片预览区域 -->
          <div v-if="imagePreviewUrl" class="image-preview-wrapper">
            <img :src="imagePreviewUrl" alt="Preview" class="image-preview" />
            <el-icon class="remove-image-btn" @click="removeImage"><Close /></el-icon>
          </div>
          
          <el-button
            type="primary"
            size="large"
            icon="Paperclip"
            :loading="isSending"
            @click="handleSendMessage"
            :disabled="!inputContent.trim() && !imagePreviewUrl"
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
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useSettingsStore } from '@/stores/settings'
import { useUnifiedAIApi } from '@/utils/ai-api'
import { useAIConfig } from '@/utils/ai-config'
import { service } from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import ChatModeSelector from '@/components/ChatModeSelector.vue'
import VoiceControls from '@/components/VoiceControls.vue'
import VoiceCall from '@/components/VoiceCall.vue'
import { Message, User, Setting, SwitchButton, Paperclip, Plus, Delete, Warning, Connection, ArrowDown, ChatLineRound, Microphone, Phone, ArrowRight, Picture, Close } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

// 大模型API框架
const { api: aiApi } = useUnifiedAIApi()
const { configManager } = useAIConfig()

// 响应式数据
const inputContent = ref('')
const isSending = ref(false)
const messagesContainer = ref(null)
const selectedModel = ref('deepseek-chat') // 默认模型（使用API框架的模型ID）
const models = ref([])
const chatMode = ref('text') // 聊天模式：text, voice, video
const modeSelectorRef = ref(null)
const voiceControlsRef = ref(null)

// 图片上传相关数据
const selectedImage = ref(null)
const imagePreviewUrl = ref('')
const fileInputRef = ref(null)

// 头像相关数据
const userAvatarUrl = ref('')
const aiAvatarUrl = ref('/images/robot-avatar.svg') // 默认机器人头像

// 语音通话相关状态
const isVoiceCallActive = ref(false)
const voiceCallRef = ref(null)
const socket = ref(null) // WebSocket连接

// AI API选择器相关数据
const modelGroups = ref([])

// 平铺的模型列表（用于显示，不分组）
const flatModels = computed(() => {
  return modelGroups.value.flatMap(group => group.models)
})

// 从API框架加载可用模型
const loadAvailableModels = async () => {
  try {
    const availableModels = await aiApi.getAvailableModels()
    
    // 按组分组模型
    const groups = {}
    availableModels.forEach(model => {
      const groupName = model.group || '通用'
      if (!groups[groupName]) {
        groups[groupName] = []
      }
      groups[groupName].push({
        id: model.id,
        name: model.name,
        provider: model.provider,
        group: model.group,
        capabilities: model.capabilities || [],
        pricing: model.pricing || {},
        performance: model.performance || {},
        tag: model.tag || '',
        tagType: model.tagType || 'info',
        icon: model.icon || '',
        available: model.available,
        description: model.description
      })
    })
    
    // 转换为模型组格式
    modelGroups.value = Object.keys(groups).map(groupName => ({
      label: groupName,
      models: groups[groupName]
    }))
    
    // 设置默认模型
    if (availableModels.length > 0) {
      const defaultModel = configManager.getDefaultModel()
      if (availableModels.some(m => m.id === defaultModel)) {
        selectedModel.value = defaultModel
      } else {
        selectedModel.value = availableModels[0].id
      }
    }
    
  } catch (error) {
    console.error('加载模型列表失败:', error)
    // 提供用户友好的错误通知
    let errorMessage = '加载模型列表失败'
    if (error.response) {
      const statusCode = error.response.status
      switch (statusCode) {
        case 401:
          errorMessage = '认证失败，请重新登录'
          break
        case 403:
          errorMessage = '权限不足，无法获取模型列表'
          break
        case 500:
          errorMessage = '服务器内部错误，加载模型列表失败'
          break
        default:
          errorMessage = `服务器错误 (${statusCode})，加载模型列表失败`
      }
    } else if (error.request) {
      errorMessage = '网络连接失败，无法加载模型列表'
    } else {
      errorMessage = error.message || '加载模型列表时发生未知错误'
    }
    
    // 使用默认的模型列表作为后备
    modelGroups.value = [
      {
        label: '高性能',
        models: [
          { id: 'gpt-4', name: 'GPT-4', provider: 'OpenAI', group: '高性能', tag: '智能', tagType: 'success', available: true },
          { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'Anthropic', group: '高性能', tag: '安全', tagType: 'warning', available: true }
        ]
      },
      {
        label: '高效能',
        models: [
          { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'OpenAI', group: '高效能', tag: '快速', tagType: 'info', available: true },
          { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'OpenAI', group: '高效能', tag: '经济', tagType: 'info', available: true }
        ]
      }
    ]
  }
}

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
    const response = await service.get('/models/')
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
  if ((!inputContent.value.trim() && !imagePreviewUrl.value) || isSending.value) {
    return
  }

  let content = inputContent.value.trim()
  inputContent.value = '' // 立即清空输入框，提升用户体验

  // 临时保存图片信息，发送成功后再清除
  const tempImage = imagePreviewUrl.value ? selectedImage.value : null
  const tempImageUrl = imagePreviewUrl.value
  imagePreviewUrl.value = ''
  selectedImage.value = null

  isSending.value = true

  try {
    // 如果有图片，先上传图片获取URL
    let imageUrl = null
    if (tempImage) {
      ElMessage.info('正在上传图片...')
      imageUrl = await uploadImage(tempImage)
      if (!imageUrl) {
        throw new Error('图片上传失败')
      }
    }

    // 如果只发送图片没有文字，添加默认提示让AI识别图片
    if (!content && imageUrl) {
      content = '请详细描述这张图片的内容，包括图片中的物体、人物、场景、文字等信息。'
    }

    // 在发送消息时传递当前选择的模型和图片URL
    const response = await chatStore.sendMessage(content, imageUrl, selectedModel.value)
    
    // 如果当前是语音模式，自动播放AI回复
    if (chatMode.value === 'voice') {
      await speakText(response)
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    
    // 根据错误类型提供更具体的错误信息
    let errorMessage = '发送消息失败'
    if (error.response) {
      // 服务器返回了错误状态码
      const statusCode = error.response.status
      switch (statusCode) {
        case 401:
          errorMessage = '认证失败，请重新登录'
          break
        case 403:
          errorMessage = '权限不足，无法发送消息'
          break
        case 429:
          errorMessage = '请求过于频繁，请稍后再试'
          break
        case 500:
          errorMessage = '服务器内部错误，请稍后再试'
          break
        case 502:
          errorMessage = '服务器暂时不可用，请稍后再试'
          break
        case 503:
          errorMessage = '服务器繁忙，请稍后再试'
          break
        default:
          errorMessage = `服务器错误 (${statusCode})，请稍后再试`
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '网络连接失败，请检查网络连接'
    } else {
      // 其他错误
      errorMessage = error.message || '发送消息时发生未知错误'
    }
    
    ElMessage.error({
      message: errorMessage,
      duration: 3000,
      showClose: true
    })
  } finally {
    isSending.value = false
  }
}

// 文字转语音
const speakText = (text) => {
  return new Promise((resolve) => {
    if (chatMode.value === 'voice' && voiceControlsRef.value) {
      // 使用 VoiceControls 组件播放语音
      voiceControlsRef.value.setAIResponse(text)
      resolve()
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

// 处理图片选择
const handleImageSelect = (file) => {
  if (!file.raw) {
    return
  }
  
  // 验证文件类型
  if (!file.raw.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }
  
  // 验证文件大小（限制为5MB）
  const maxSize = 5 * 1024 * 1024
  if (file.raw.size > maxSize) {
    ElMessage.warning('图片大小不能超过5MB')
    return
  }
  
  // 生成预览URL
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreviewUrl.value = e.target.result
    selectedImage.value = file.raw
  }
  reader.readAsDataURL(file.raw)
  
  ElMessage.success('图片已选择')
}

// 触发文件选择
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

// 处理文件选择变化
const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) {
    return
  }
  
  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }
  
  // 验证文件大小（限制为5MB）
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.warning('图片大小不能超过5MB')
    return
  }
  
  // 生成预览URL
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreviewUrl.value = e.target.result
    selectedImage.value = file
  }
  reader.readAsDataURL(file)
  
  ElMessage.success('图片已选择')
}

// 移除已选择的图片
const removeImage = () => {
  selectedImage.value = null
  imagePreviewUrl.value = ''
}

// 上传图片到后端（用于聊天图片识别）
const uploadImage = async (imageFile) => {
  try {
    const formData = new FormData()
    formData.append('image', imageFile)

    const token = localStorage.getItem('token')
    const response = await service.post('/upload-image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      },
      timeout: 30000
    })

    if (response.data && response.data.image_url) {
      return response.data.image_url
    }

    return null
  } catch (error) {
    console.error('图片上传失败:', error)
    ElMessage.error('图片上传失败，请稍后重试')
    return null
  }
}



// 获取模型图标
const getModelIcon = (provider) => {
  const iconMap = {
    'DeepSeek': 'DS',
    'OpenAI': 'AI',
    'Anthropic': 'AN',
    '阿里云': '云',
    'Alibaba Cloud': '云',
    'Google': 'G',
    'Microsoft': 'MS',
    'Meta': 'M',
    '百度': '百',
    '腾讯': '腾',
    '字节跳动': '字'
  }
  return iconMap[provider] || provider.charAt(0).toUpperCase()
}

// 根据性能速度获取标签类型
const getPerformanceTagType = (speed) => {
  if (speed === 'very_fast') return 'success'
  if (speed === 'fast') return 'success'
  if (speed === 'medium') return 'warning'
  if (speed === 'slow') return 'danger'
  return 'info'
}

// 处理模型切换
const handleModelChange = async (modelId) => {
  console.log('模型已切换到:', modelId)
  
  // 检查当前对话是否有历史消息
  if (messages.value && messages.value.length > 0) {
    try {
      const result = await ElMessageBox.confirm(
        `您即将切换到 ${modelId} 模型。当前对话中的消息将继续使用之前的模型上下文，是否需要开启新对话以使用新模型？`,
        '模型切换提醒',
        {
          confirmButtonText: '开启新对话',
          cancelButtonText: '继续当前对话',
          type: 'warning'
        }
      )
      
      // 用户选择开启新对话
      if (result === 'confirm') {
        // 更新模型状态为连接中
        modelStatus.value = 'connecting'
        
        try {
          // 验证模型是否可用
          const availableModels = await aiApi.getAvailableModels()
          const selectedModelObj = availableModels.find(m => m.id === modelId)
          
          if (!selectedModelObj || !selectedModelObj.available) {
            throw new Error('所选模型当前不可用')
          }
          
          // 更新配置管理器中的默认模型
          configManager.setDefaultModel(modelId)
          
          // 更新设置存储
          const settingsStore = useSettingsStore()
          settingsStore.updateAISettings({ defaultModel: modelId })
          
          // 更新模型状态为已连接
          modelStatus.value = 'connected'
          
          // 开启新对话
          await handleNewChat()
          
          // 显示模型统计信息
          const stats = aiApi.getStats()
          const modelName = modelGroups.value.flatMap(g => g.models).find(m => m.id === modelId)?.name
          ElMessage.success({
            message: `已切换到 ${modelName} 模型并开启新对话 (总调用: ${stats.client.totalCalls})`,
            duration: 3000
          })
          
          console.log('模型切换成功，当前模型:', modelId)
        } catch (error) {
          modelStatus.value = 'error'
          ElMessage.error(`模型切换失败: ${error.message}`)
          
          // 恢复到之前的模型
          const previousModel = configManager.getDefaultModel()
          selectedModel.value = previousModel
          
          console.error('模型切换错误:', error)
        }
        
        return // 提前返回，不再执行后续逻辑
      }
    } catch (cancelError) {
      // 用户选择继续当前对话或取消，继续执行下面的常规切换逻辑
      console.log('用户选择继续当前对话')
    }
  }
  
  // 更新模型状态为连接中（对于不需要新开对话的情况）
  modelStatus.value = 'connecting'
  
  try {
    // 验证模型是否可用
    const availableModels = await aiApi.getAvailableModels()
    const selectedModelObj = availableModels.find(m => m.id === modelId)
    
    if (!selectedModelObj || !selectedModelObj.available) {
      throw new Error('所选模型当前不可用')
    }
    
    // 更新配置管理器中的默认模型
    configManager.setDefaultModel(modelId)
    
    // 更新设置存储
    const settingsStore = useSettingsStore()
    settingsStore.updateAISettings({ defaultModel: modelId })
    
    // 更新模型状态为已连接
    modelStatus.value = 'connected'
    
    // 显示模型统计信息
    const stats = aiApi.getStats()
    const modelName = modelGroups.value.flatMap(g => g.models).find(m => m.id === modelId)?.name
    ElMessage.success({
      message: `已切换到 ${modelName} 模型 (总调用: ${stats.client.totalCalls})`,
      duration: 3000
    })
    
    console.log('模型切换成功，当前模型:', modelId)
  } catch (error) {
    modelStatus.value = 'error'
    
    // 提供更友好的错误消息
    let errorMessage = '模型切换失败'
    if (error.response) {
      const statusCode = error.response.status
      switch (statusCode) {
        case 401:
          errorMessage = '认证失败，请重新登录后再试'
          break
        case 403:
          errorMessage = '权限不足，无法切换模型'
          break
        case 500:
          errorMessage = '服务器内部错误，模型切换失败'
          break
        default:
          errorMessage = `服务器错误 (${statusCode})，模型切换失败`
      }
    } else if (error.request) {
      errorMessage = '网络连接失败，请检查网络连接'
    } else {
      errorMessage = error.message || '模型切换时发生未知错误'
    }
    
    ElMessage.error({
      message: errorMessage,
      duration: 3000,
      showClose: true
    })
    
    // 恢复到之前的模型
    const previousModel = configManager.getDefaultModel()
    selectedModel.value = previousModel
    
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
  } else if (command === 'settings') {
    // 打开设置页面
    router.push('/settings')
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
const endVoiceCall = async () => {
  // 实际项目中应该在这里关闭WebSocket连接
  if (voiceCallRef.value && typeof voiceCallRef.value.endCall === 'function') {
    try {
      await voiceCallRef.value.endCall()
    } catch (error) {
      console.error('结束通话时出错:', error)
    }
  }
  
  // 确保通话状态被更新，无论组件调用是否成功
  isVoiceCallActive.value = false
  
  ElMessage.info('通话已结束')
}

// 强制结束语音通话（直接更新状态而不依赖组件方法）
const forceEndVoiceCall = () => {
  isVoiceCallActive.value = false
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
  return textMap[mode] || '文字'
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

// 跳转到功能路由界面
const goToFunctionRouter = () => {
  router.push('/function-router')
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

// 检查用户认证状态（与路由守卫协调）
const checkAuth = () => {
  console.log('页面级认证检查:', {
    isLoggedIn: authStore.isLoggedIn,
    token: authStore.token,
    user: authStore.user,
    localStorageToken: localStorage.getItem('token'),
    localStorageUser: localStorage.getItem('user')
  })
  
  // 更可靠的认证检查：同时检查store和localStorage
  const hasValidToken = authStore.token || localStorage.getItem('token')
  const hasValidUser = authStore.user || localStorage.getItem('user')
  const isAuthenticated = hasValidToken && hasValidUser
  
  console.log('页面级认证检查结果:', {
    hasValidToken: !!hasValidToken,
    hasValidUser: !!hasValidUser,
    isAuthenticated
  })
  
  if (!isAuthenticated) {
    console.log('页面级认证失败，但仍允许访问')
    // 不再强制跳转到登录页面，而是允许访问但功能受限
    return false
  }
  
  // 确保认证状态同步
  if (!authStore.token && localStorage.getItem('token')) {
    authStore.token = localStorage.getItem('token')
    authStore.user = JSON.parse(localStorage.getItem('user') || 'null')
    console.log('页面级：已从localStorage恢复认证状态')
  }
  
  console.log('页面级认证成功')
  return true
}

// 定时刷新token（防止长时间使用后自动退出）
const setupTokenRefresh = () => {
  // 每30分钟检查一次token状态
  const refreshInterval = setInterval(async () => {
    try {
      const token = localStorage.getItem('token')
      if (token && authStore.isLoggedIn) {
        console.log('定时检查token状态...')
        
        // 尝试调用一个简单的API来验证token是否有效
        await service.get('/conversations/', {
          timeout: 5000,
          _isTokenCheck: true
        })
        
        console.log('token状态正常')
      }
    } catch (error) {
      console.log('token检查失败，尝试刷新...')
      
      // 如果token过期，尝试刷新
      if (error.response?.status === 401) {
        try {
          await authStore.refreshToken()
          console.log('token自动刷新成功')
        } catch (refreshError) {
          console.error('token自动刷新失败:', refreshError)
          // 刷新失败，但不要强制退出，让用户继续使用
        }
      }
    }
  }, 30 * 60 * 1000) // 30分钟

  // 清理定时器
  onUnmounted(() => {
    clearInterval(refreshInterval)
  })
}

// 页面加载时获取对话列表（优化加载）
const loadData = async () => {
  // 先检查认证状态，但不阻止页面渲染
  const authResult = checkAuth()
  
  try {
    // 即使未认证也尝试加载模型列表（这些可能不需要认证）
    await loadModels()
    
    // 只有在认证通过时才加载会话列表
    if (authResult) {
      await chatStore.fetchConversations()
    } else {
      // 未认证时清空会话列表
      chatStore.conversations = []
      console.log('未认证用户，会话列表已清空')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

// 页面挂载时调用
onMounted(async () => {
  console.log('Chat.vue 页面挂载开始')
  
  // 检查认证状态，但不阻止页面渲染
  const authResult = checkAuth()
  if (!authResult) {
    console.log('认证检查失败，但允许页面继续渲染')
    ElMessage.warning('请先登录以使用完整功能')
    // 认证失败时仍然允许页面渲染，只是功能受限
  }
  
  // 无论认证状态如何，都尝试加载数据
  try {
    await loadData()
  } catch (error) {
    console.error('加载数据失败:', error)
    // 数据加载失败不影响页面渲染
  }
  
  // 加载可用模型列表
  try {
    await loadAvailableModels()
  } catch (error) {
    console.error('加载模型列表失败:', error)
    // 模型加载失败不影响页面渲染
  }
  
  // 设置默认模型
  try {
    const settingsStore = useSettingsStore()
    const aiSettings = settingsStore.aiSettings
    if (aiSettings && aiSettings.defaultModel) {
      selectedModel.value = aiSettings.defaultModel
    }
  } catch (error) {
    console.error('设置默认模型失败:', error)
  }
  
  // 验证配置状态
  try {
    const configValidation = configManager.validateConfig()
    if (!configValidation.isValid && configValidation.errors.length > 0) {
      ElMessage.warning({
        message: 'API配置不完整，部分功能可能受限',
        duration: 5000
      })
    }
  } catch (error) {
    console.error('验证配置失败:', error)
  }
  
  // 设置token自动刷新机制
  setupTokenRefresh()
  
  // 获取用户头像
  await loadUserAvatar()
  
  console.log('Chat.vue 页面挂载完成')
})

// 加载用户头像
const loadUserAvatar = async () => {
  if (!authStore.isAuthenticated) {
    return
  }
  
  try {
    const response = await service.get('/user-info/')
    
    if (response.status === 200) {
      const userData = response.data
      if (userData.avatar_url) {
        userAvatarUrl.value = userData.avatar_url
      }
    }
  } catch (error) {
    console.error('加载用户头像失败:', error)
  }
}

// 监听authStore.user变化，实现头像实时更新
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser?.avatar) {
      userAvatarUrl.value = newUser.avatar
    }
  },
  { deep: true }
)

// 跳转到个人资料页面
const goToProfile = () => {
  router.push('/settings?tab=profile')
}

// 判断是否应该显示时间
const shouldShowTime = (index) => {
  if (index === 0) return true
  
  const currentMessage = messages.value[index]
  const prevMessage = messages.value[index - 1]
  
  if (!currentMessage || !prevMessage) return false
  
  // 计算时间差（分钟）
  const currentTime = new Date(currentMessage.created_at).getTime()
  const prevTime = new Date(prevMessage.created_at).getTime()
  const timeDiff = (currentTime - prevTime) / (1000 * 60)
  
  // 如果时间差大于5分钟，显示时间
  return timeDiff > 5
}
</script>

<style scoped>
/* 微信风格聊天样式 */
.messages-container {
  background-color: #f5f5dc; /* 浅黄色聊天背景 */
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message-wrapper {
  margin-bottom: 16px;
}

/* 时间显示 */
.message-time {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin: 10px 0;
  padding: 2px 10px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  display: inline-block;
  margin-left: 50%;
  transform: translateX(-50%);
}

/* 消息项 */
.message-item {
  display: flex;
  margin-bottom: 10px;
  max-width: 70%;
}

.message-item.user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-item.assistant {
  margin-right: auto;
  flex-direction: row;
}

/* 头像 */
.message-avatar {
  flex-shrink: 0;
}

.message-avatar .avatar-img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}

.message-item.user .message-avatar {
  margin-left: 8px;
}

.message-item.assistant .message-avatar {
  margin-right: 8px;
}

/* 消息气泡 */
.message-bubble {
  padding: 10px 14px;
  border-radius: 18px;
  word-wrap: break-word;
  white-space: pre-wrap;
  position: relative;
  max-width: 100%;
}

.message-item.user .message-bubble {
  background-color: #dcf8c6; /* 绿色气泡（用户） */
  border-bottom-right-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 150, 0, 0.1);
}

.message-item.assistant .message-bubble {
  background-color: #ffffff; /* 白色气泡（AI） */
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.message-header {
  display: none; /* 隐藏旧的消息头 */
}

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
  height: 100vh;
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
  padding: 0.25rem;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 0.3rem 0.5rem;
  margin-bottom: 0.15rem;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 40px;
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
  width: 32px;
  height: 32px;
  background: #667eea;
  border-radius: 50%;
  color: white;
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.conversation-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.conversation-title {
  font-size: 0.85rem;
  font-weight: 500;
  color: #303133;
  margin-bottom: 0.1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}



.conversation-mode {
  margin-top: 0.1rem;
}

.conversation-actions {
  margin-left: 0.25rem;
  display: flex;
  align-items: center;
}

.conversation-actions .el-button {
  padding: 2px 4px;
  min-height: auto;
}

/* 模型分组相关样式 */
.model-group {
  margin-bottom: 1rem;
}

.model-group-header {
  display: flex;
  align-items: center;
  margin: 0.5rem 0;
  padding: 0.25rem 0.5rem;
  background: #f0f2f5;
  border-radius: 4px;
}

.model-tag {
  margin-right: 0.5rem;
}

.conv-count {
  font-size: 0.75rem;
  color: #909399;
}

/* 左侧栏底部设置区域 */
.sidebar-footer {
  border-top: 1px solid #ebeef5;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  gap: 4px; /* 减少按钮间距 */
}

/* 功能路由按钮 - 在最上方 */
.function-router-btn {
  width: calc(100% - 1rem);
  height: 36px;
  background: linear-gradient(45deg, #667eea, #764ba2);
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

.function-router-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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

/* 语音助手按钮 - 在中间 */
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
  background: linear-gradient(45deg, #4facfe, #00f2fe); /* 更醒目的渐变背景 */
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.settings-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(79, 172, 254, 0.3);
  border-color: rgba(255, 255, 255, 0.6);
  background: linear-gradient(45deg, #3a9ce0, #00d9f0); /* 悬停时的深色渐变 */
  color: white;
}

.settings-button .el-icon {
  color: white;
  font-size: 14px;
  margin-right: 4px;
}

.settings-button span {
  font-size: 12px;
  color: white;
  font-weight: 600;
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
  margin: 0;
  overflow: hidden;
}

.chat-header {
  padding: 0;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #ebeef5;
}

.chat-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  position: relative;
  padding: 0;
  height: 60px;
  background: rgba(255, 255, 255, 0.98);
  border-bottom: 1px solid #ebeef5;
}

.chat-header-left {
  position: absolute !important;
  left: 0px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  display: flex !important;
  align-items: center !important;
  z-index: 20 !important;
  margin: 0 !important;
  padding: 0 !important;
}

.chat-header-right {
  position: absolute !important;
  right: 0px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  display: flex !important;
  align-items: center !important;
  z-index: 20 !important;
  margin: 0 !important;
  padding: 0 !important;
}

.chat-title {
  position: absolute !important;
  left: 50% !important;
  top: 50% !important;
  transform: translate(-50%, -50%) !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  min-width: 120px !important;
  z-index: 10 !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* 删除重复的chat-header-left样式 */

.ai-api-selector {
  display: flex;
  align-items: center;
  gap: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 14px;
  padding: 10px 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: static;
  z-index: 10;
  height: 52px;
  box-sizing: border-box;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  margin-right: 0;
  flex: 0 0 auto;
}

.ai-api-selector:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.ai-model-select {
  width: 320px;
  min-width: 280px;
}

.ai-model-select :deep(.el-input__inner) {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 10px 16px;
  height: 40px;
}

.ai-model-select :deep(.el-input__inner:focus) {
  border: none;
  box-shadow: none;
}

.ai-model-select :deep(.el-select__placeholder) {
  color: #64748b;
  font-weight: 500;
  font-size: 0.95rem;
}

.ai-model-select :deep(.el-select .el-input .el-select__caret) {
  color: #64748b;
  font-size: 0.9rem;
}

.ai-model-select :deep(.el-select-dropdown) {
  border: none;
  box-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.05),
    0 8px 24px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  overflow: hidden;
  min-width: 380px !important;
  width: auto !important;
  padding: 0;
  background: #ffffff;
  backdrop-filter: blur(10px);
  position: relative;
}

.ai-model-select :deep(.el-select-dropdown__list) {
  padding: 0;
}

.ai-model-select :deep(.el-select-dropdown__list) {
  padding: 0;
}



.model-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 0;
  transition: all 0.2s ease;
  cursor: pointer;
  margin: 0;
  border: none;
  width: 100%;
  box-sizing: border-box;
  background: transparent;
  position: relative;
  min-height: 60px;
}

.model-option:not(:last-child) {
  margin-bottom: 0;
}

.model-option:last-child {
  border-bottom: none;
}

.model-option:hover {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.model-option.selected {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.model-option.selected {
  background: #ffffff !important;
}

.model-option.selected .model-name {
  font-weight: 400 !important;
  color: #000000 !important;
}

.model-option.selected .provider {
  font-weight: 400 !important;
  color: #374151 !important;
}



.model-option:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.model-icon-left {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.model-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  font-size: 0.9rem;
  font-weight: bold;
  box-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.2),
    inset 0 1px 1px rgba(255, 255, 255, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
}

.model-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, transparent 50%);
  pointer-events: none;
}

.model-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.model-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.model-name {
  font-weight: 600;
  font-size: 1rem;
  color: #1e293b;
  line-height: 1.4;
}

.model-badges {
  display: flex;
  align-items: center;
  gap: 6px;
}

.model-tag {
  font-size: 0.75rem;
  height: 20px;
  line-height: 18px;
  padding: 0 6px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  position: relative;
}

.status-indicator.available {
  background: #10b981;
  box-shadow: 0 1px 3px rgba(16, 185, 129, 0.3);
}

.status-indicator.unavailable {
  background: #ef4444;
  box-shadow: 0 1px 3px rgba(239, 68, 68, 0.3);
}

.status-indicator::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.5);
  pointer-events: none;
}

.model-description {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.provider {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.description {
  font-size: 0.8rem;
  color: #94a3b8;
  line-height: 1.2;
}

.model-arrow {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s ease;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.model-option:hover .model-arrow {
  opacity: 1;
  transform: translateX(2px);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.model-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #475569;
  font-size: 0.9rem;
  font-weight: 500;
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
  flex: 1;
  justify-content: center;
  min-width: 120px;
}

.new-chat-btn {
  font-size: 1.1rem;
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
}

.new-chat-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.new-chat-btn:active {
  transform: translateY(0);
}

.ai-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo-icon {
  font-size: 2rem;
  color: #3b82f6;
}

.brand-name {
  font-size: 1.4rem;
  font-weight: 600;
  color: #1e293b;
}

/* 苹果风格玻璃效果 */
.apple-glass {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.apple-sidebar {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border-right: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.05);
}

.apple-chat-area {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
}

/* 苹果风格按钮 */
.apple-sidebar .btn-primary {
  background: rgba(0, 122, 255, 0.9);
  border: none;
  border-radius: 10px;
  color: white;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3);
}

.apple-sidebar .btn-primary:hover {
  background: rgba(0, 122, 255, 1);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
}

/* 侧边栏苹果风格按钮 */
.apple-sidebar .el-button {
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
}

.apple-sidebar .el-button:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.apple-sidebar .el-button--primary {
  background: rgba(0, 122, 255, 0.9);
  border-color: rgba(0, 122, 255, 0.6);
  color: white;
}

.apple-sidebar .el-button--success {
  background: rgba(52, 199, 89, 0.9);
  border-color: rgba(52, 199, 89, 0.6);
  color: white;
}

.apple-sidebar .el-button--danger {
  background: rgba(255, 59, 48, 0.9);
  border-color: rgba(255, 59, 48, 0.6);
  color: white;
}

/* 侧边栏下拉菜单 */
.apple-sidebar .el-dropdown-menu {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(30px);
}

.apple-sidebar .el-dropdown-menu .el-dropdown-menu__item {
  background: transparent;
  border-radius: 8px;
  margin: 2px 8px;
}

.apple-sidebar .el-dropdown-menu .el-dropdown-menu__item:hover {
  background: rgba(0, 122, 255, 0.1);
}

/* 苹果风格对话列表 */
.apple-sidebar .conversation-item {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  margin: 4px 0;
  border: 1px solid rgba(255, 255, 255, 0.4);
  transition: all 0.3s ease;
}

.apple-sidebar .conversation-item:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateX(4px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.apple-sidebar .conversation-item.active {
  background: rgba(0, 122, 255, 0.1);
  border: 1px solid rgba(0, 122, 255, 0.3);
}

/* 苹果风格输入框 */
.apple-chat-area .input-wrapper {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(20px);
}

/* 苹果风格下拉选择器 */
.apple-chat-area .el-select {
  backdrop-filter: blur(20px);
}

.apple-chat-area .el-select .el-input__wrapper {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 12px;
}
.apple-chat-area .el-select-dropdown {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(30px);
}

.apple-chat-area .el-select-dropdown .el-select-dropdown__item {
  background: transparent;
  border-radius: 8px;
  margin: 2px 8px;
}

.apple-chat-area .el-select-dropdown .el-select-dropdown__item:hover {
  background: rgba(0, 122, 255, 0.1);
}

.apple-chat-area .el-select-dropdown .el-select-dropdown__item.selected {
  background: rgba(0, 122, 255, 0.15);
  color: #007AFF;
}

/* 苹果风格下拉菜单 */
.apple-chat-area .el-dropdown {
  backdrop-filter: blur(20px);
}

.apple-chat-area .el-dropdown-menu {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(30px);
}

.apple-chat-area .el-dropdown-menu .el-dropdown-menu__item {
  background: transparent;
  border-radius: 8px;
  margin: 2px 8px;
}

.apple-chat-area .el-dropdown-menu .el-dropdown-menu__item:hover {
  background: rgba(0, 122, 255, 0.1);
}

/* 苹果风格按钮 */
.apple-chat-area .el-button {
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
}

.apple-chat-area .el-button:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.apple-chat-area .el-button--primary {
  background: rgba(0, 122, 255, 0.9);
  border-color: rgba(0, 122, 255, 0.6);
  color: white;
}

.apple-chat-area .el-button--primary:hover {
  background: rgba(0, 122, 255, 1);
}

/* 苹果风格消息容器 */
.apple-chat-area .messages-container {
  backdrop-filter: blur(10px);
}

/* 苹果风格消息气泡 */
.apple-chat-area .message-item.user .message-content {
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  color: white;
  border-radius: 20px 20px 4px 20px;
  box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3);
  backdrop-filter: blur(10px);
}

.apple-chat-area .message-item.assistant .message-content {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px 20px 20px 4px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(10px);
}

/* 苹果风格头像 */
.apple-chat-area .message-avatar {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

/* 苹果风格头部区域 */
.apple-chat-area .chat-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(30px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
}

/* 苹果风格底部区域 */
.apple-chat-area .chat-footer {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(30px);
  border-top: 1px solid rgba(255, 255, 255, 0.4);
}

.chat-title h1 {
  font-size: 2.2rem;
  font-weight: 800;
  margin: 0 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  letter-spacing: 0.5px;
  padding: 8px 20px;
  border-radius: 12px;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chat-controls {
  display: flex;
  align-items: center;
  margin-left: auto;
  flex: 0 0 auto;
  margin-right: 0;
}

.mode-selector-wrapper {
  position: static;
  z-index: 10;
}

.mode-dropdown-button {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px 20px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  height: 40px;
  font-weight: 600;
  color: #475569;
  min-width: 140px;
  justify-content: center;
}

.mode-dropdown-button:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
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

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid transparent;
}

.apple-chat-area .message-avatar {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
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
  gap: 0;
  align-items: flex-end;
  width: 98%;
  max-width: none;
  margin: 0 auto;
  padding: 0 1rem;
  position: relative;
}

.input-with-image {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
}

.message-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #dcdfe6;
  border-right: none;
  border-radius: 12px 0 0 12px;
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
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.send-button {
  padding: 0.75rem 1.5rem;
  height: 48px;
  background: #3b82f6;
  color: white;
  border: 1px solid #3b82f6;
  border-radius: 0 12px 12px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:hover {
  background: #2563eb;
  border-color: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.send-button:disabled {
  background: #9ca3af;
  border-color: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 图片上传按钮样式 */
.image-upload-btn {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
}

/* 图片预览样式 */
.image-preview-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #dcdfe6;
  border-radius: 12px;
  margin: 0.5rem 1rem;
  max-width: 98%;
  margin: 0 auto;
}

.image-preview {
  max-width: 150px;
  max-height: 150px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #ebeef5;
}

.remove-image-btn {
  color: #ff4d4f;
  cursor: pointer;
  padding: 4px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-image-btn:hover {
  color: #ff1f1f;
  transform: scale(1.2);
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

/* AI模型选择器样式 */
.ai-api-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}





.model-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.model-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.provider {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

.description {
  font-size: 0.85rem;
  color: #94a3b8;
  font-style: italic;
  line-height: 1.2;
}

.model-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #475569;
  font-size: 0.9rem;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-model-select {
    width: 200px;
  }
}

/* 深色主题支持 */
@media (prefers-color-scheme: dark) {
  .ai-api-selector {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
    border-color: #334155;
    backdrop-filter: blur(10px);
  }
  
  .ai-api-selector:hover {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
    border-color: #475569;
  }
  
  .ai-model-select :deep(.el-input__inner) {
    background: transparent;
    color: #f1f5f9;
  }
  
  .ai-model-select :deep(.el-select__placeholder) {
    color: #94a3b8;
  }
  
  .ai-model-select :deep(.el-select .el-input .el-select__caret) {
    color: #94a3b8;
  }
  
  .ai-model-select :deep(.el-select-dropdown) {
    background: #1e293b;
    border: none;
  }
  
  .ai-model-select :deep(.el-select-group__title) {
    background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
    color: #cbd5e1;
  }
  
  .model-option:hover {
    background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
  }
  
  .model-option.selected {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }
  
  .model-option.selected {
    background: #1e293b !important;
  }
  
  .model-option.selected .model-name {
    font-weight: 400 !important;
    color: #ffffff !important;
  }
  
  .model-option.selected .provider {
    font-weight: 400 !important;
    color: #cbd5e1 !important;
  }
  
  .model-name span {
    color: #f1f5f9;
  }
  
  .provider {
    color: #94a3b8;
  }
  
  .description {
    color: #64748b;
  }
}

/* 右下角用户头像悬浮块样式 */
.user-avatar-float {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 100;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-avatar-float:hover {
  transform: scale(1.1);
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  border: 2px solid white;
}

.user-avatar-float:hover .user-avatar {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

/* 模型选择器中的元信息样式 */
.model-meta {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.capability-tag,
.pricing-tag,
.performance-tag {
  font-size: 10px;
  margin-right: 2px;
}

/* AI思考中的加载动画样式 */
.ai-thinking {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  color: #606266;
  font-size: 14px;
}

.thinking-dots {
  display: flex;
  gap: 4px;
}

.thinking-dots span {
  width: 8px;
  height: 8px;
  background: #409eff;
  border-radius: 50%;
  animation: thinking-bounce 1.4s infinite ease-in-out both;
}

.thinking-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.thinking-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes thinking-bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.thinking-text {
  color: #409eff;
  font-weight: 500;
}

.thinking-timer {
  color: #909399;
  font-size: 12px;
  margin-left: 8px;
}
</style>