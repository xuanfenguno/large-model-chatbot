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
    </aside>

    <!-- 主聊天窗口 -->
    <main class="chat-main">
      <!-- 聊天头部 -->
      <header class="chat-header">
        <div class="chat-title">
          <el-icon :size="24">
            <Message />
          </el-icon>
          <h1>{{ conversationTitle }}</h1>
        </div>
        <div class="chat-controls">
          <!-- 模型选择 -->
          <el-select
            v-model="selectedModel"
            placeholder="选择模型"
            size="small"
            class="model-select"
            @change="handleModelChange"
          >
            <el-option
              v-for="model in models"
              :key="model.id"
              :label="`${model.name} (${model.provider})`"
              :value="model.id"
            />
          </el-select>
          
          <div class="chat-actions">
            <el-button
              type="text"
              size="small"
              icon="Setting"
              @click="handleSettings"
            >
              设置
            </el-button>
            <el-button
              type="text"
              size="small"
              icon="User"
              @click="handleProfile"
            >
              个人资料
            </el-button>
            <el-button
              type="text"
              size="small"
              icon="SwitchButton"
              @click="handleLogout"
            >
              退出登录
            </el-button>
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
        <div class="input-container">
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
              <el-button
                type="text"
                size="small"
                icon="VideoCamera"
                @click="handleStartVideo"
                :disabled="isSending"
              />
              <el-button
                type="primary"
                size="small"
                icon="Paperclip"
                :loading="isSending"
                @click="handleSendMessage"
                :disabled="!inputContent.trim()"
              >
                发送
              </el-button>
            </template>
          </el-input>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { ElMessage, ElMessageBox } from 'element-plus'
import Vue3MarkdownIt from 'vue3-markdown-it'
import { Message, User, Setting, SwitchButton, Paperclip, Plus, VideoCamera, Delete, Warning } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

// 响应式数据
const inputContent = ref('')
const isSending = ref(false)
const messagesContainer = ref(null)
const selectedModel = ref('deepseek-v3') // 默认模型
const models = ref([])

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
    await chatStore.sendMessage(content, null, selectedModel.value)
  } catch (error) {
    ElMessage.error('发送消息失败')
  } finally {
    isSending.value = false
  }
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

// 处理开始视频
const handleStartVideo = () => {
  ElMessage.info('视频通话功能开发中...')
}

// 处理模型切换
const handleModelChange = (modelId) => {
  console.log('模型已切换到:', modelId)
  ElMessage.success(`模型已切换到: ${models.value.find(m => m.id === modelId)?.name}`)
}

// 处理设置
const handleSettings = () => {
  ElMessage.info('设置功能开发中...')
}

// 处理个人资料
const handleProfile = () => {
  ElMessage.info('个人资料功能开发中...')
}

// 处理退出登录
const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}

// 页面加载时获取对话列表（优化加载）
const loadData = async () => {
  try {
    await chatStore.fetchConversations()
    await loadModels() // 加载模型列表
  } catch (error) {
    ElMessage.error('加载对话列表失败')
  }
}

// 页面挂载时调用
onMounted(loadData)
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

.conversation-actions {
  margin-left: 0.5rem;
}

.delete-btn {
  color: #f56c6c;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(245, 247, 250, 0.8);
  backdrop-filter: blur(10px);
}

.chat-header {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-title {
  display: flex;
  align-items: center;
  color: #303133;
}

.chat-title h1 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0.5rem;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: rgba(245, 247, 250, 0.6);
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