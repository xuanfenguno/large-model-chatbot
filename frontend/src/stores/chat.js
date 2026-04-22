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
  
  // 大模型 API
  const { api: aiApi } = useUnifiedAIApi()

  // 获取会话列表（优化缓存）
  const fetchConversations = async () => {
    try {
      const response = await service.get('/conversations/', {
        params: {
          page: 1,
          page_size: 50
        }
      })
      conversations.value = response.data
      
      console.log(`从后端获取会话列表成功，共 ${conversations.value.length} 个会话`)
      
      // 清理 localStorage 中无效的会话缓存
      const backendIds = conversations.value.map(c => c.id)
      const storedConvs = JSON.parse(localStorage.getItem('chat-store') || '{}')
      const localConvs = storedConvs.conversations || []
      
      // 找出 localStorage 中存在但后端不存在的会话 ID
      const invalidIds = localConvs
        .filter(c => !backendIds.includes(c.id))
        .map(c => c.id)
      
      console.log(`发现 ${invalidIds.length} 个无效会话：${invalidIds.join(', ')}`)
      
      // 清理这些无效会话的缓存
      invalidIds.forEach(id => {
        localStorage.removeItem(`messages-${id}`)
        console.log(`清理无效会话缓存：${id}`)
      })
      
      // 如果当前选中的会话不存在于后端，清空选择
      if (selectedConversationId.value && !backendIds.includes(selectedConversationId.value)) {
        console.warn(`当前选中的会话 ${selectedConversationId.value} 不存在于后端，清空选择`)
        selectedConversationId.value = null
        messages.value = []
        
        // 立即保存更新
        try {
          localStorage.setItem('chat-store', JSON.stringify({
            selectedConversationId: null,
            messages: [],
            conversations: conversations.value  // 使用后端返回的最新数据
          }))
        } catch (e) {
          console.error('缓存会话列表失败:', e)
        }
      }
      
      // 更新 localStorage 中的会话列表（使用后端数据）
      try {
        localStorage.setItem('chat-store', JSON.stringify({
          selectedConversationId: selectedConversationId.value,
          messages: messages.value,
          conversations: conversations.value
        }))
      } catch (e) {
        console.error('缓存会话列表失败:', e)
      }
      
    } catch (error) {
      console.error('获取会话列表失败:', error)
      let errorMessage = '获取会话列表失败'
      
      if (error.response) {
        // 服务器响应了错误状态码
        const { status, data } = error.response
        if (status === 401) {
          errorMessage = '用户未登录或登录已过期，请重新登录'
        } else if (status === 403) {
          errorMessage = '您没有权限访问会话列表'
        } else if (data && data.error) {
          errorMessage = data.error
        } else {
          errorMessage = `服务器错误 (${status})`
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        errorMessage = '网络连接失败，请检查网络连接'
      } else {
        // 其他错误
        errorMessage = error.message || '未知错误'
      }
      
      ElMessage({
        message: errorMessage,
        type: 'error',
        duration: 5000
      })
    }
  }

  // 创建新会话
  const createConversation = async (title) => {
    try {
      const response = await service.post('/conversations/', {
        title: title || '新会话',
        mode: 'chat'
      }, {
        timeout: 10000
      })
      // 创建成功后重新获取会话列表，确保数据一致性
      await fetchConversations()
      selectedConversationId.value = response.data.id
      messages.value = []
      
      // 保存更新后的会话列表到 localStorage
      try {
        localStorage.setItem('chat-store', JSON.stringify({
          selectedConversationId: selectedConversationId.value,
          messages: messages.value,
          conversations: conversations.value
        }))
      } catch (e) {
        console.error('缓存会话列表失败:', e)
      }
      
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
      // 先尝试从 localStorage 加载缓存的消息
      const cachedMessages = localStorage.getItem(`messages-${conversationId}`)
      if (cachedMessages) {
        try {
          messages.value = JSON.parse(cachedMessages)
          console.log(`从缓存加载了 ${messages.value.length} 条消息`)
        } catch (e) {
          console.error('解析缓存消息失败:', e)
        }
      }

      // 然后从服务器获取最新消息
      const response = await service.get(`/conversations/${conversationId}/messages/`, {
        params: {
          page: 1,
          page_size: 100
        }
      })
      
      // 更新消息列表
      messages.value = response.data
      
      // 缓存到 localStorage
      try {
        localStorage.setItem(`messages-${conversationId}`, JSON.stringify(response.data))
      } catch (e) {
        console.error('缓存消息失败:', e)
      }
    } catch (error) {
      console.error('获取消息列表失败:', error)
      
      // 如果是 404 错误，说明会话不存在，需要清理无效引用
      if (error.response?.status === 404 || error.response?.status === 500) {
        console.warn(`会话 ${conversationId} 不存在，清理无效引用`)
        
        // 从会话列表中移除该会话
        const convIndex = conversations.value.findIndex(c => c.id === conversationId)
        if (convIndex !== -1) {
          conversations.value.splice(convIndex, 1)
          
          // 更新 localStorage
          try {
            localStorage.setItem('chat-store', JSON.stringify({
              selectedConversationId: selectedConversationId.value,
              messages: messages.value,
              conversations: conversations.value
            }))
          } catch (e) {
            console.error('缓存会话列表失败:', e)
          }
        }
        
        // 如果当前选中的是这个不存在的会话，清空选择
        if (selectedConversationId.value === conversationId) {
          selectedConversationId.value = null
          messages.value = []
        }
        
        ElMessage({
          message: '该会话已不存在，已自动清理',
          type: 'warning',
          duration: 3000
        })
        return
      }
      
      // 如果网络请求失败，尝试使用缓存
      const cachedMessages = localStorage.getItem(`messages-${conversationId}`)
      if (cachedMessages) {
        try {
          messages.value = JSON.parse(cachedMessages)
          ElMessage({
            message: '已加载缓存的聊天记录',
            type: 'warning',
            duration: 3000
          })
        } catch (e) {
          console.error('解析缓存消息失败:', e)
        }
      } else {
        ElMessage({
          message: '获取消息列表失败',
          type: 'error'
        })
      }
    }
  }

  // 发送消息（使用SSE流式响应，AI回复逐字动态生成）
  const sendMessage = async (content, image = null, model = null) => {
    isLoading.value = true

    // 初始化aiMessage变量，以防在定义前发生错误
    let aiMessage = null
    const startTime = Date.now()

    try {
      // 如果没有选择会话，自动创建新会话
      if (!selectedConversationId.value) {
        const newConversation = await createConversation(content.slice(0, 30) + '...')
        if (!newConversation) {
          throw new Error('创建新会话失败')
        }
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
      aiMessage = {
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

      // 使用SSE流式发送消息，实现逐字动态生成效果
        let fullContent = ''
        let isFirstChunk = true
        let waitTimer = null

        // 更新等待时间
        const updateWaitTime = () => {
          const waitTime = Date.now() - startTime
          const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
          if (aiIndex !== -1) {
            messages.value[aiIndex] = {
              ...messages.value[aiIndex],
              waitTime: waitTime
            }
          }
        }

        // 启动计时器，每秒更新一次
        waitTimer = setInterval(updateWaitTime, 1000)

        await aiApi.sendMessageStream(
          content,
          {
            model: model,
            history: history,
            conversation_id: selectedConversationId.value,
            image_url: image,
            temperature: 0.6,
            maxTokens: 2000
          },
          // 收到数据块时的回调（逐字显示）- chunk是字符串
          (chunkContent) => {
            fullContent += chunkContent

            // 实时更新AI回复内容，实现逐字动态生成效果
            const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
            if (aiIndex !== -1) {
              messages.value[aiIndex] = {
                ...messages.value[aiIndex],
                content: fullContent,
                is_loading: false
              }
            }

            // 滚动到底部
            setTimeout(() => {
              const messagesContainer = document.querySelector('.messages-container')
              if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight
              }
            }, 0)
          },
          // 完成时的回调
          (result) => {
            // 清除计时器
            if (waitTimer) {
              clearInterval(waitTimer)
              waitTimer = null
            }

            const responseTime = Date.now() - startTime

            if (result && result.success) {
              // 更新最终AI回复
              const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
              if (aiIndex !== -1) {
                messages.value[aiIndex] = {
                  id: Date.now() + 2,
                  role: 'assistant',
                  content: fullContent || result.content || '请求成功',
                  created_at: new Date().toISOString(),
                  model: model,
                  responseTime: responseTime
                }
              }

              // 实时更新缓存
              try {
                localStorage.setItem(`messages-${selectedConversationId.value}`, JSON.stringify(messages.value))
              } catch (e) {
                console.error('缓存消息失败:', e)
              }

              // 更新会话列表中的该会话信息（标题和最后更新时间）
              const convIndex = conversations.value.findIndex(c => c.id === selectedConversationId.value)
              if (convIndex !== -1) {
                // 如果当前会话标题是默认的，使用第一条消息作为新标题
                const currentConv = conversations.value[convIndex]
                if (currentConv.title === '新会话' || currentConv.title === 'New Chat') {
                  const firstMessage = messages.value[0]?.content || content
                  conversations.value[convIndex].title = firstMessage.slice(0, 30) + (firstMessage.length > 30 ? '...' : '')
                }
                // 更新最后活动时间
                conversations.value[convIndex].updated_at = new Date().toISOString()

                // 将会话移到列表最前面
                const updatedConv = conversations.value.splice(convIndex, 1)[0]
                conversations.value.unshift(updatedConv)

                // 保存更新后的会话列表到 localStorage
                try {
                  localStorage.setItem('chat-store', JSON.stringify({
                    selectedConversationId: selectedConversationId.value,
                    messages: messages.value,
                    conversations: conversations.value
                  }))
                } catch (e) {
                  console.error('缓存会话列表失败:', e)
                }
              }

              // 显示成功消息
              ElMessage({
                message: `消息发送成功 (${responseTime}ms)`,
                type: 'success',
                duration: 2000
              })
            } else {
              // 处理错误
              const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
              if (aiIndex !== -1) {
                messages.value[aiIndex] = {
                  ...aiMessage,
                  content: (result && result.error) ? result.error : '抱歉，消息发送失败。请稍后重试。',
                  is_loading: false,
                  error: true
                }
              }
            }
          }
        )

    } catch (error) {
      // 清除计时器
      if (waitTimer) {
        clearInterval(waitTimer)
        waitTimer = null
      }

      // 处理错误
      if (aiMessage) {
        const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
        if (aiIndex !== -1) {
          messages.value[aiIndex] = {
            ...aiMessage,
            content: error.message || '抱歉，消息发送失败。请稍后重试。',
            is_loading: false,
            error: true
          }
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

    // 初始化aiMessage变量，以防在定义前发生错误
    let aiMessage = null

    try {
      // 如果没有选择会话，自动创建新会话
      if (!selectedConversationId.value) {
        const newConversation = await createConversation(content.slice(0, 30) + '...')
        if (!newConversation) {
          throw new Error('创建新会话失败')
        }
      }

      // 创建本地用户消息预览
      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: content,
        created_at: new Date().toISOString()
      }
      
      messages.value.push(userMessage)
      
      // 创建AI回复的占位消息
      aiMessage = {
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
          conversation_id: selectedConversationId.value,
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
          const aiIndex = messages.value.findIndex(msg => msg.id === aiMessage.id)
          if (aiIndex !== -1) {
            messages.value[aiIndex] = {
              ...messages.value[aiIndex],
              id: Date.now() + 2,
              is_loading: false,
              is_streaming: false,
              model: result.model
            }
            
            // 实时更新缓存
            try {
              localStorage.setItem(`messages-${selectedConversationId.value}`, JSON.stringify(messages.value))
            } catch (e) {
              console.error('缓存消息失败:', e)
            }
          }
          
          // 更新会话列表中的该会话信息（标题和最后更新时间）
          const convIndex = conversations.value.findIndex(c => c.id === selectedConversationId.value)
          if (convIndex !== -1) {
            // 如果当前会话标题是默认的，使用第一条消息作为新标题
            const currentConv = conversations.value[convIndex]
            if (currentConv.title === '新会话' || currentConv.title === 'New Chat') {
              const firstMessage = messages.value[0]?.content || content
              conversations.value[convIndex].title = firstMessage.slice(0, 30) + (firstMessage.length > 30 ? '...' : '')
            }
            // 更新最后活动时间
            conversations.value[convIndex].updated_at = new Date().toISOString()
            
            // 将会话移到列表最前面
            const updatedConv = conversations.value.splice(convIndex, 1)[0]
            conversations.value.unshift(updatedConv)
            
            // 保存更新后的会话列表到 localStorage
            try {
              localStorage.setItem('chat-store', JSON.stringify({
                selectedConversationId: selectedConversationId.value,
                messages: messages.value,
                conversations: conversations.value
              }))
            } catch (e) {
              console.error('缓存会话列表失败:', e)
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
      if (aiMessage) {
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
      }
    } finally {
      isStreaming.value = false
    }
  }

  // 删除会话
  const deleteConversation = async (conversationId) => {
    try {
      await service.delete(`/conversations/${conversationId}/`, {
        timeout: 10000
      })
      
      // 立即从前端移除该会话
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      
      // 如果当前选中的是这个会话，清空选择
      if (selectedConversationId.value === conversationId) {
        selectedConversationId.value = null
        messages.value = []
      }
      
      // 清理该会话的所有缓存
      localStorage.removeItem(`messages-${conversationId}`)
      
      // 保存更新后的会话列表到 localStorage
      try {
        localStorage.setItem('chat-store', JSON.stringify({
          selectedConversationId: selectedConversationId.value,
          messages: messages.value,
          conversations: conversations.value
        }))
      } catch (e) {
        console.error('缓存会话列表失败:', e)
      }

      ElMessage({
        message: '会话删除成功',
        type: 'success'
      })
    } catch (error) {
      console.error('删除会话失败:', error)
      console.log('错误详情:', {
        hasResponse: !!error.response,
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        isAxiosError: error.isAxiosError
      })
      
      // 检查是否是 404 或 500 错误（会话不存在）
      const isNotFound = error.response?.status === 404 || error.response?.status === 500
      
      if (isNotFound) {
        console.warn(`会话 ${conversationId} 不存在，视为已删除`)
        
        // 从前端移除该会话
        conversations.value = conversations.value.filter(c => c.id !== conversationId)
        
        // 如果当前选中的是这个会话，清空选择
        if (selectedConversationId.value === conversationId) {
          selectedConversationId.value = null
          messages.value = []
        }
        
        // 清理缓存
        localStorage.removeItem(`messages-${conversationId}`)
        
        // 保存更新
        try {
          localStorage.setItem('chat-store', JSON.stringify({
            selectedConversationId: selectedConversationId.value,
            messages: messages.value,
            conversations: conversations.value
          }))
        } catch (e) {
          console.error('缓存会话列表失败:', e)
        }
        
        ElMessage({
          message: '会话已删除',
          type: 'success'
        })
        return
      }
      
      // 其他错误才显示失败
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
}, {
  persist: {
    key: 'chat-store',
    storage: localStorage,
    paths: ['selectedConversationId', 'messages']  // 移除 'conversations'，避免恢复过期的会话列表
  }
})