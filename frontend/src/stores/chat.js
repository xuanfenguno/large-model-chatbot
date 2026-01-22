import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import service from '@/utils/request'
import { useUnifiedAIApi } from '@/utils/ai-api'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const selectedConversationId = ref(null)
  const messages = ref([])
  const isLoading = ref(false)
  const isStreaming = ref(false)
  
  // 大模型API
  const { api: aiApi } = useUnifiedAIApi()

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
      // 创建成功后重新获取会话列表，确保数据一致性
      await fetchConversations()
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

  // 发送消息（使用新的大模型API框架）
  const sendMessage = async (content, image = null, model = null) => {
    isLoading.value = true

    try {
      // 如果没有选择会话，自动创建新会话
      if (!selectedConversationId.value) {
        const newConversation = await createConversation(content.slice(0, 30) + '...')
        if (!newConversation) {
          throw new Error('创建新会话失败')
        }
      }

      // 首先将用户消息保存到后端数据库
      const userMessageResponse = await service.post('/v1/messages/', {
        conversation_id: selectedConversationId.value,
        role: 'user',
        content: content,
        image_url: image
      })

      // 创建本地用户消息预览
      const userMessage = {
        id: userMessageResponse.data.id,
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

      // 构建对话历史
      const history = messages.value
        .filter(msg => msg.id !== aiMessage.id) // 排除当前占位消息
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }))

      // 使用新的大模型API发送消息
      const result = await aiApi.sendMessage(content, {
        model: model,
        history: history,
        temperature: 0.6,
        maxTokens: 2000
      })

      if (result.success) {
        // 将AI回复保存到后端数据库
        const aiMessageResponse = await service.post('/v1/messages/', {
          conversation_id: selectedConversationId.value,
          role: 'assistant',
          content: result.content,
          model: result.model
        })

        // 更新AI回复
        const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
        if (aiIndex !== -1) {
          messages.value[aiIndex] = {
            id: aiMessageResponse.data.id,
            role: 'assistant',
            content: result.content,
            created_at: new Date().toISOString(),
            model: result.model,
            responseTime: result.responseTime
          }
        }
        
        // 显示成功消息
        ElMessage({
          message: `消息发送成功 (${result.responseTime}ms)`,
          type: 'success',
          duration: 2000
        })
      } else {
        // 处理API错误
        throw new Error(result.error)
      }

    } catch (error) {
      // 处理错误
      const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
      if (aiIndex !== -1) {
        messages.value[aiIndex] = {
          ...aiMessage,
          content: error.message || '抱歉，消息发送失败。请稍后重试。',
          is_loading: false,
          error: true
        }
      }
      
      // 错误消息已经在错误处理器中显示，这里不需要重复显示
    } finally {
      isLoading.value = false
    }
  }

  // 流式发送消息（支持实时显示）
  const sendMessageStream = async (content, model = null) => {
    isStreaming.value = true

    try {
      // 如果没有选择会话，自动创建新会话
      if (!selectedConversationId.value) {
        const newConversation = await createConversation(content.slice(0, 30) + '...')
        if (!newConversation) {
          throw new Error('创建新会话失败')
        }
      }

      // 首先将用户消息保存到后端数据库
      const userMessageResponse = await service.post('/v1/messages/', {
        conversation_id: selectedConversationId.value,
        role: 'user',
        content: content
      })

      // 创建本地用户消息预览
      const userMessage = {
        id: userMessageResponse.data.id,
        role: 'user',
        content: content,
        created_at: new Date().toISOString()
      }
      
      messages.value.push(userMessage)
      
      // 创建AI回复的占位消息
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '',
        is_loading: true,
        is_streaming: true,
        created_at: new Date().toISOString()
      }
      messages.value.push(aiMessage)

      // 构建对话历史
      const history = messages.value
        .filter(msg => msg.id !== aiMessage.id)
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }))

      await aiApi.sendMessageStream(
        content,
        {
          model: model,
          history: history,
          temperature: 0.6,
          maxTokens: 2000
        },
        // 数据块回调
        (chunk) => {
          const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
          if (aiIndex !== -1) {
            messages.value[aiIndex].content += chunk
          }
        },
        // 完成回调
        async (result) => {
          // 将AI回复保存到后端数据库
          const aiMessageResponse = await service.post('/v1/messages/', {
            conversation_id: selectedConversationId.value,
            role: 'assistant',
            content: messages.value.find(msg => msg.id === aiMessage.id)?.content || '',
            model: result.model
          })

          const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
          if (aiIndex !== -1) {
            messages.value[aiIndex] = {
              ...messages.value[aiIndex],
              id: aiMessageResponse.data.id,
              is_loading: false,
              is_streaming: false,
              model: result.model
            }
          }
          
          if (result.success) {
            ElMessage({
              message: '流式消息发送完成',
              type: 'success',
              duration: 2000
            })
          }
        }
      )

    } catch (error) {
      const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
      if (aiIndex !== -1) {
        messages.value[aiIndex] = {
          ...aiMessage,
          content: error.message || '抱歉，流式消息发送失败。',
          is_loading: false,
          is_streaming: false,
          error: true
        }
      }
    } finally {
      isStreaming.value = false
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
    isStreaming,
    fetchConversations,
    createConversation,
    selectConversation,
    fetchMessages,
    sendMessage,
    sendMessageStream,
    deleteConversation,
    clearMessages,
    conversationTitle
  }
})