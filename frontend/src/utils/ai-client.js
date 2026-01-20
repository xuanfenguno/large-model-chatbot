/**
 * 大模型API客户端
 * 统一封装多种AI模型的API调用
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'

class AIClient {
  constructor() {
    this.providers = {
      'openai': new OpenAIProvider(),
      'deepseek': new DeepSeekProvider(),
      'claude': new ClaudeProvider(),
      'gemini': new GeminiProvider(),
      'qwen': new QwenProvider(),
      'kimi': new KimiProvider(),
      'doubao': new DouBaoProvider(),
      'bailian': new BaiLianProvider()
    }
    
    // 默认配置
    this.defaultConfig = {
      temperature: 0.6,
      maxTokens: 2000,
      topP: 0.7,
      timeout: 30000
    }
    
    // API调用统计
    this.stats = {
      totalCalls: 0,
      successfulCalls: 0,
      failedCalls: 0,
      averageResponseTime: 0
    }
  }

  /**
   * 发送消息到AI模型
   * @param {string} message - 用户消息
   * @param {Object} options - 配置选项
   * @param {string} options.model - 模型ID
   * @param {number} options.temperature - 温度参数
   * @param {number} options.maxTokens - 最大token数
   * @param {Array} options.history - 对话历史
   * @returns {Promise<Object>} AI回复
   */
  async sendMessage(message, options = {}) {
    const startTime = Date.now()
    this.stats.totalCalls++
    
    try {
      const config = { ...this.defaultConfig, ...options }
      
      // 验证参数
      this._validateConfig(config)
      
      // 获取模型提供商
      const provider = this._getProvider(config.model)
      
      // 调用API
      const response = await provider.sendMessage(message, config)
      
      // 更新统计
      const responseTime = Date.now() - startTime
      this.stats.successfulCalls++
      this.stats.averageResponseTime = 
        (this.stats.averageResponseTime * (this.stats.successfulCalls - 1) + responseTime) / this.stats.successfulCalls
      
      return {
        success: true,
        content: response.content,
        model: config.model,
        responseTime,
        usage: response.usage || {}
      }
      
    } catch (error) {
      this.stats.failedCalls++
      
      return {
        success: false,
        error: error.message,
        errorCode: error.code || 'UNKNOWN_ERROR',
        model: options.model
      }
    }
  }

  /**
   * 流式发送消息（支持实时显示）
   * @param {string} message - 用户消息
   * @param {Object} options - 配置选项
   * @param {Function} onChunk - 收到数据块时的回调
   * @param {Function} onComplete - 完成时的回调
   */
  async sendMessageStream(message, options = {}, onChunk, onComplete) {
    try {
      const config = { ...this.defaultConfig, ...options }
      this._validateConfig(config)
      
      const provider = this._getProvider(config.model)
      
      await provider.sendMessageStream(message, config, onChunk, onComplete)
      
    } catch (error) {
      if (onComplete) {
        onComplete({
          success: false,
          error: error.message
        })
      }
    }
  }

  /**
   * 获取可用模型列表
   * @returns {Promise<Array>} 模型列表
   */
  async getAvailableModels() {
    const models = []
    
    // 从所有提供商获取模型
    for (const [providerName, provider] of Object.entries(this.providers)) {
      try {
        const providerModels = await provider.getModels()
        models.push(...providerModels.map(model => ({
          ...model,
          provider: providerName
        })))
      } catch (error) {
        console.warn(`获取${providerName}模型列表失败:`, error)
      }
    }
    
    return models
  }

  /**
   * 验证API配置
   * @param {Object} config - 配置对象
   */
  _validateConfig(config) {
    if (!config.model) {
      throw new Error('模型ID不能为空')
    }
    
    if (config.temperature < 0 || config.temperature > 2) {
      throw new Error('温度参数必须在0-2之间')
    }
    
    if (config.maxTokens < 1 || config.maxTokens > 4000) {
      throw new Error('最大token数必须在1-4000之间')
    }
  }

  /**
   * 根据模型ID获取提供商
   * @param {string} modelId - 模型ID
   * @returns {Object} 提供商实例
   */
  _getProvider(modelId) {
    // 根据模型ID前缀判断提供商
    if (modelId.startsWith('gpt-')) {
      return this.providers.openai
    } else if (modelId.startsWith('deepseek')) {
      return this.providers.deepseek
    } else if (modelId.startsWith('claude')) {
      return this.providers.claude
    } else if (modelId.startsWith('gemini')) {
      return this.providers.gemini
    } else if (modelId.startsWith('qwen')) {
      return this.providers.qwen
    } else if (modelId.startsWith('kimi')) {
      return this.providers.kimi
    } else if (modelId.startsWith('doubao')) {
      return this.providers.doubao
    }
    
    throw new Error(`不支持的模型: ${modelId}`)
  }

  /**
   * 获取API调用统计
   * @returns {Object} 统计信息
   */
  getStats() {
    return { ...this.stats }
  }

  /**
   * 重置统计信息
   */
  resetStats() {
    this.stats = {
      totalCalls: 0,
      successfulCalls: 0,
      failedCalls: 0,
      averageResponseTime: 0
    }
  }
}

/**
 * OpenAI API提供商
 */
class OpenAIProvider {
  constructor() {
    this.baseURL = 'https://api.openai.com/v1'
    this.name = 'OpenAI'
  }

  async sendMessage(message, config) {
    const apiKey = this._getApiKey('OPENAI_API_KEY')
    
    const response = await fetch(`${this.baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: config.model,
        messages: this._buildMessages(message, config.history),
        temperature: config.temperature,
        max_tokens: config.maxTokens,
        top_p: config.topP
      }),
      timeout: config.timeout
    })

    if (!response.ok) {
      throw new Error(`OpenAI API错误: ${response.status}`)
    }

    const data = await response.json()
    
    return {
      content: data.choices[0].message.content,
      usage: data.usage
    }
  }

  async sendMessageStream(message, config, onChunk, onComplete) {
    const apiKey = this._getApiKey('OPENAI_API_KEY')
    
    const response = await fetch(`${this.baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: config.model,
        messages: this._buildMessages(message, config.history),
        temperature: config.temperature,
        max_tokens: config.maxTokens,
        top_p: config.topP,
        stream: true
      })
    })

    if (!response.ok) {
      throw new Error(`OpenAI API错误: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let fullContent = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ') && line !== 'data: [DONE]') {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.choices[0].delta.content) {
                const content = data.choices[0].delta.content
                fullContent += content
                
                if (onChunk) {
                  onChunk(content)
                }
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
      
      if (onComplete) {
        onComplete({
          success: true,
          content: fullContent
        })
      }
      
    } catch (error) {
      throw new Error(`流式响应错误: ${error.message}`)
    } finally {
      reader.releaseLock()
    }
  }

  async getModels() {
    return [
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: '快速且经济实惠' },
      { id: 'gpt-4', name: 'GPT-4', description: '最先进的模型' },
      { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', description: '增强版GPT-4' }
    ]
  }

  _buildMessages(userMessage, history = []) {
    const messages = []
    
    // 添加历史消息
    if (history && history.length > 0) {
      messages.push(...history.slice(-8)) // 最多保留8条历史
    }
    
    // 添加当前用户消息
    messages.push({
      role: 'user',
      content: userMessage
    })
    
    return messages
  }

  _getApiKey(keyName) {
    const apiKey = localStorage.getItem(keyName)
    
    if (!apiKey) {
      throw new Error(`请配置${keyName}`)
    }
    
    return apiKey
  }
}

/**
 * DeepSeek API提供商
 */
class DeepSeekProvider {
  constructor() {
    this.baseURL = 'https://api.deepseek.com'
    this.name = 'DeepSeek'
  }

  async sendMessage(message, config) {
    const apiKey = this._getApiKey('DEEPSEEK_API_KEY')
    
    const response = await fetch(`${this.baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: config.model,
        messages: this._buildMessages(message, config.history),
        temperature: config.temperature,
        max_tokens: config.maxTokens,
        top_p: config.topP,
        stream: false
      }),
      timeout: config.timeout
    })

    if (!response.ok) {
      throw new Error(`DeepSeek API错误: ${response.status}`)
    }

    const data = await response.json()
    
    return {
      content: data.choices[0].message.content,
      usage: data.usage
    }
  }

  async getModels() {
    return [
      { id: 'deepseek-chat', name: 'DeepSeek Chat', description: '通用对话模型' },
      { id: 'deepseek-coder', name: 'DeepSeek Coder', description: '代码生成专用' }
    ]
  }

  _buildMessages(userMessage, history = []) {
    // DeepSeek的消息格式与OpenAI兼容
    const messages = []
    
    if (history && history.length > 0) {
      messages.push(...history.slice(-8))
    }
    
    messages.push({
      role: 'user',
      content: userMessage
    })
    
    return messages
  }

  _getApiKey(keyName) {
    const apiKey = localStorage.getItem(keyName)
    
    if (!apiKey) {
      throw new Error(`请配置${keyName}`)
    }
    
    return apiKey
  }
}

// 其他提供商类（简化实现）
class ClaudeProvider {
  async sendMessage(message, config) {
    throw new Error('Claude API暂未实现')
  }
  
  async getModels() {
    return [
      { id: 'claude-3-opus', name: 'Claude 3 Opus', description: '最强模型' },
      { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', description: '平衡模型' }
    ]
  }
}

class GeminiProvider {
  async sendMessage(message, config) {
    throw new Error('Gemini API暂未实现')
  }
  
  async getModels() {
    return [
      { id: 'gemini-pro', name: 'Gemini Pro', description: '通用模型' },
      { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', description: '增强版' }
    ]
  }
}

class QwenProvider {
  constructor() {
    this.baseURL = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    this.name = 'Qwen'
  }

  async sendMessage(message, config) {
    const apiKey = this._getApiKey('QWEN_API_KEY')
    
    const messages = this._buildMessages(message, config.history)
    
    const response = await fetch(`${this.baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: config.model,
        messages: messages,
        temperature: config.temperature || 0.6,
        max_tokens: config.maxTokens || 2000,
        top_p: config.topP || 0.7
      })
    })
    
    if (!response.ok) {
      throw new Error(`Qwen API请求失败: ${response.status} ${response.statusText}`)
    }
    
    const data = await response.json()
    
    if (data.error) {
      throw new Error(`Qwen API错误: ${data.error.message}`)
    }
    
    return {
      content: data.choices[0].message.content,
      usage: data.usage
    }
  }
  
  async sendMessageStream(message, config, onChunk, onComplete) {
    const apiKey = this._getApiKey('QWEN_API_KEY')
    
    const messages = this._buildMessages(message, config.history)
    
    const response = await fetch(`${this.baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: config.model,
        messages: messages,
        temperature: config.temperature || 0.6,
        max_tokens: config.maxTokens || 2000,
        top_p: config.topP || 0.7,
        stream: true
      })
    })
    
    if (!response.ok) {
      throw new Error(`Qwen API流式请求失败: ${response.status} ${response.statusText}`)
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    
    try {
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              if (onComplete) onComplete()
              return
            }
            
            try {
              const parsed = JSON.parse(data)
              if (parsed.choices && parsed.choices[0] && parsed.choices[0].delta && parsed.choices[0].delta.content) {
                if (onChunk) onChunk(parsed.choices[0].delta.content)
              }
            } catch (e) {
              console.warn('解析Qwen流式响应失败:', e)
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }
  
  _buildMessages(userMessage, history) {
    const messages = []
    
    if (history && history.length > 0) {
      messages.push(...history.slice(-8).map(msg => ({
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.content
      })))
    }
    
    messages.push({
      role: 'user',
      content: userMessage
    })
    
    return messages
  }
  
  _getApiKey(keyName) {
    const apiKey = localStorage.getItem(keyName) || process.env[keyName]
    
    if (!apiKey) {
      throw new Error(`请配置${keyName}`)
    }
    
    return apiKey
  }
  
  async getModels() {
    return [
      { id: 'qwen-max', name: 'Qwen Max', description: '最强模型', available: true },
      { id: 'qwen-plus', name: 'Qwen Plus', description: '增强版', available: true },
      { id: 'qwen-turbo', name: 'Qwen Turbo', description: '快速版', available: true }
    ]
  }
}

class KimiProvider {
  async sendMessage(message, config) {
    throw new Error('Kimi API暂未实现')
  }
  
  async getModels() {
    return [
      { id: 'kimi-large', name: 'Kimi Large', description: '大容量模型' }
    ]
  }
}

class DouBaoProvider {
  async sendMessage(message, config) {
    throw new Error('豆包API暂未实现')
  }
  
  async getModels() {
    return [
      { id: 'doubao-pro', name: '豆包Pro', description: '字节跳动模型' }
    ]
  }
}

class BaiLianProvider {
  async sendMessage(message, config) {
    throw new Error('阿里百炼API暂未实现')
  }
  
  async getModels() {
    return [
      { id: 'bailian-standard', name: '百炼标准版', description: '阿里百炼标准模型', available: true },
      { id: 'bailian-pro', name: '百炼专业版', description: '阿里百炼专业模型', available: true },
      { id: 'bailian-plus', name: '百炼增强版', description: '阿里百炼增强模型', available: true }
    ]
  }
}

// 创建全局实例
export const aiClient = new AIClient()

// Vue composable
export function useAIClient() {
  return {
    aiClient,
    
    // 发送消息
    async sendMessage(message, options) {
      return await aiClient.sendMessage(message, options)
    },
    
    // 流式发送消息
    async sendMessageStream(message, options, onChunk, onComplete) {
      return await aiClient.sendMessageStream(message, options, onChunk, onComplete)
    },
    
    // 获取模型列表
    async getModels() {
      return await aiClient.getAvailableModels()
    },
    
    // 获取统计信息
    getStats() {
      return aiClient.getStats()
    }
  }
}