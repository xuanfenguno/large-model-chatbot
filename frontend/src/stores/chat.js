import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import service from '@/utils/request'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const selectedConversationId = ref(null)
  const messages = ref([])
  const isLoading = ref(false)

  // 获取会话列表（优化缓存）
  const fetchConversations = async () => {
    try {
      const response = await service.get('/v1/conversations/', {
        timeout: 10000
      })
      conversations.value = response.data
    } catch (error) {
      ElMessage({
        message: '获取会话列表失败',
        type: 'error'
      })
    }
  }

  // 创建新会话
  const createConversation = async (title) => {
    try {
      const response = await service.post('/v1/conversations/', {
        title: title || '新会话'
      }, {
        timeout: 10000
      })
      conversations.value.push(response.data)
      selectedConversationId.value = response.data.id
      messages.value = []
      return response.data
    } catch (error) {
      ElMessage({
        message: '创建会话失败',
        type: 'error'
      })
    }
  }

  // 选择会话（优化加载）
  const selectConversation = async (conversationId) => {
    try {
      selectedConversationId.value = conversationId
      // 使用防抖和缓存优化
      await fetchMessages(conversationId)
    } catch (error) {
      ElMessage({
        message: '选择会话失败',
        type: 'error'
      })
    }
  }

  // 获取消息列表（优化响应速度）
  const fetchMessages = async (conversationId) => {
    try {
      const response = await service.get(`/v1/conversations/${conversationId}/messages/`, {
        timeout: 10000
      })
      messages.value = response.data
    } catch (error) {
      ElMessage({
        message: '获取消息列表失败',
        type: 'error'
      })
    }
  }

  // 发送消息（优化响应速度和用户体验）
  const sendMessage = async (content, image = null, model = null) => {
    if (!selectedConversationId.value) {
      ElMessage({
        message: '请先创建或选择一个会话',
        type: 'warning'
      })
      return
    }

    // 创建本地用户消息预览
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: content,
      image_url: image,
      created_at: new Date().toISOString()
    }
    
    messages.value.push(userMessage)
    
    // 创建AI回复的占位消息
    const aiMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: '',
      is_loading: true,
      created_at: new Date().toISOString()
    }
    messages.value.push(aiMessage)

    isLoading.value = true

    try {
      // 调用AI接口
      const requestData = {
        conversation_id: selectedConversationId.value,
        message: content,
        image_url: image
      };
      
      // 如果指定了模型，则添加到请求数据中
      if (model) {
        requestData.model = model;
      }
      
      const response = await service.post('/v1/messages/chat/', requestData, {
        timeout: 30000
      })

      // 更新AI回复
      const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
      if (aiIndex !== -1) {
        messages.value[aiIndex] = {
          id: response.data.ai_message.id,
          role: 'assistant',
          content: response.data.ai_message.content,
          created_at: response.data.ai_message.created_at
        }
      }

    } catch (error) {
      // 处理错误
      const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
      if (aiIndex !== -1) {
        messages.value[aiIndex] = {
          ...aiMessage,
          content: '抱歉，消息发送失败。请稍后重试。',
          is_loading: false,
          error: true
        }
      }
      
      ElMessage({
        message: '发送消息失败',
        type: 'error'
      })
    } finally {
      isLoading.value = false
    }
  }

  // 删除会话
  const deleteConversation = async (conversationId) => {
    try {
      await service.delete(`/v1/conversations/${conversationId}/`, {
        timeout: 10000
      })
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      
      if (selectedConversationId.value === conversationId) {
        selectedConversationId.value = null
        messages.value = []
      }

      ElMessage({
        message: '会话删除成功',
        type: 'success'
      })
    } catch (error) {
      ElMessage({
        message: '删除会话失败',
        type: 'error'
      })
    }
  }

  // 清空消息
  const clearMessages = () => {
    messages.value = []
  }

  // 会话标题
  const conversationTitle = computed(() => {
    if (!selectedConversationId.value) {
      return '新会话'
    }
    const conversation = conversations.value.find(c => c.id === selectedConversationId.value)
    return conversation?.title || '新会话'
  })

  return {
    conversations,
    selectedConversationId,
    messages,
    isLoading,
    fetchConversations,
    createConversation,
    selectConversation,
    fetchMessages,
    sendMessage,
    deleteConversation,
    clearMessages,
    conversationTitle
  }
})