/**
 * 统一的大模型API调用接口
 * 整合客户端、错误处理、配置管理
 */

import { aiClient } from './ai-client.js'
import { aiErrorHandler } from './ai-error-handler.js'
import { aiConfigManager } from './ai-config.js'

class UnifiedAIApi {
  constructor() {
    this.client = aiClient
    this.errorHandler = aiErrorHandler
    this.configManager = aiConfigManager
    
    // 错误监控
    this.errorMonitor = this.errorHandler.createErrorMonitor()
    
    // 缓存机制
    this.cache = new Map()
    this.cacheDuration = 5 * 60 * 1000 // 5分钟
  }

  /**
   * 发送消息到AI模型（统一接口）
   * @param {string} message - 用户消息
   * @param {Object} options - 配置选项
   * @returns {Promise<Object>} AI回复
   */
  async sendMessage(message, options = {}) {
    // 验证配置
    const configValidation = this.configManager.validateConfig()
    if (!configValidation.isValid && configValidation.errors.length > 0) {
      throw new Error('配置验证失败: ' + configValidation.errors.join(', '))
    }
    
    // 构建完整配置
    const fullOptions = this._buildFullOptions(options)
    
    // 检查缓存
    const cacheKey = this._getCacheKey(message, fullOptions)
    if (this._isCacheValid(cacheKey)) {
      return this.cache.get(cacheKey)
    }
    
    try {
      // 使用错误处理器的重试机制
      const result = await this.errorHandler.withRetry(
        () => this.client.sendMessage(message, fullOptions),
        {
          maxRetries: fullOptions.maxRetries,
          retryDelay: 1000
        }
      )
      
      // 缓存结果
      if (result.success && fullOptions.enableCache) {
        this.cache.set(cacheKey, result)
        setTimeout(() => {
          this.cache.delete(cacheKey)
        }, this.cacheDuration)
      }
      
      return result
      
    } catch (error) {
      // 处理错误
      const errorContext = {
        model: fullOptions.model,
        provider: this._getProviderFromModel(fullOptions.model),
        messageLength: message.length
      }
      
      const errorResult = this.errorHandler.handleError(error, errorContext)
      
      // 记录错误
      this.errorMonitor.addError({
        code: errorResult.errorCode,
        message: errorResult.error
      }, errorContext)
      
      return errorResult
    }
  }

  /**
   * 流式发送消息
   * @param {string} message - 用户消息
   * @param {Object} options - 配置选项
   * @param {Function} onChunk - 数据块回调
   * @param {Function} onComplete - 完成回调
   */
  async sendMessageStream(message, options = {}, onChunk, onComplete) {
    const fullOptions = this._buildFullOptions(options)
    
    try {
      await this.client.sendMessageStream(
        message,
        fullOptions,
        onChunk,
        (result) => {
          if (onComplete) {
            onComplete(result)
          }
        }
      )
      
    } catch (error) {
      const errorContext = {
        model: fullOptions.model,
        provider: this._getProviderFromModel(fullOptions.model),
        messageLength: message.length
      }
      
      const errorResult = this.errorHandler.handleError(error, errorContext)
      
      if (onComplete) {
        onComplete(errorResult)
      }
    }
  }

  /**
   * 获取可用模型列表
   * @returns {Promise<Array>} 模型列表
   */
  async getAvailableModels() {
    try {
      return await this.client.getAvailableModels()
    } catch (error) {
      console.error('获取模型列表失败:', error)
      return []
    }
  }

  /**
   * 获取API统计信息
   * @returns {Object} 统计信息
   */
  getStats() {
    const clientStats = this.client.getStats()
    const errorStats = this.errorMonitor.getStats()
    
    return {
      client: clientStats,
      errors: errorStats,
      config: this.configManager.getConfigSummary()
    }
  }

  /**
   * 构建完整配置选项
   * @param {Object} options - 用户提供的选项
   * @returns {Object} 完整配置
   */
  _buildFullOptions(options) {
    const globalConfig = this.configManager.getGlobalConfig()
    const modelConfig = this.configManager.getModelConfig(options.model)
    
    return {
      model: options.model || this.configManager.getDefaultModel(),
      temperature: options.temperature !== undefined ? options.temperature : modelConfig.temperature,
      maxTokens: options.maxTokens !== undefined ? options.maxTokens : modelConfig.maxTokens,
      topP: options.topP !== undefined ? options.topP : modelConfig.topP,
      history: options.history || [],
      timeout: options.timeout || globalConfig.timeout,
      maxRetries: options.maxRetries || globalConfig.maxRetries,
      enableCache: options.enableCache !== undefined ? options.enableCache : globalConfig.enableCache,
      ...options
    }
  }

  /**
   * 生成缓存键
   * @param {string} message - 用户消息
   * @param {Object} options - 配置选项
   * @returns {string} 缓存键
   */
  _getCacheKey(message, options) {
    const keyData = {
      message: message.substring(0, 100), // 只取前100字符
      model: options.model,
      temperature: options.temperature,
      maxTokens: options.maxTokens
    }
    
    return JSON.stringify(keyData)
  }

  /**
   * 检查缓存是否有效
   * @param {string} cacheKey - 缓存键
   * @returns {boolean} 是否有效
   */
  _isCacheValid(cacheKey) {
    return this.cache.has(cacheKey)
  }

  /**
   * 根据模型ID获取提供商
   * @param {string} modelId - 模型ID
   * @returns {string} 提供商名称
   */
  _getProviderFromModel(modelId) {
    if (modelId.startsWith('gpt-')) return 'openai'
    if (modelId.startsWith('deepseek')) return 'deepseek'
    if (modelId.startsWith('claude')) return 'claude'
    if (modelId.startsWith('gemini')) return 'gemini'
    if (modelId.startsWith('qwen')) return 'qwen'
    if (modelId.startsWith('kimi')) return 'kimi'
    if (modelId.startsWith('doubao')) return 'doubao'
    return 'unknown'
  }

  /**
   * 清除缓存
   */
  clearCache() {
    this.cache.clear()
  }

  /**
   * 重置统计信息
   */
  resetStats() {
    this.client.resetStats()
    this.errorMonitor.clear()
  }

  /**
   * 获取配置管理器
   * @returns {AIConfigManager} 配置管理器实例
   */
  getConfigManager() {
    return this.configManager
  }

  /**
   * 获取错误处理器
   * @returns {AIErrorHandler} 错误处理器实例
   */
  getErrorHandler() {
    return this.errorHandler
  }
}

// 创建全局API实例
export const unifiedAIApi = new UnifiedAIApi()

// Vue composable
export function useUnifiedAIApi() {
  return {
    api: unifiedAIApi,
    
    // 发送消息
    async sendMessage(message, options) {
      return await unifiedAIApi.sendMessage(message, options)
    },
    
    // 流式发送消息
    async sendMessageStream(message, options, onChunk, onComplete) {
      return await unifiedAIApi.sendMessageStream(message, options, onChunk, onComplete)
    },
    
    // 获取模型列表
    async getModels() {
      return await unifiedAIApi.getAvailableModels()
    },
    
    // 获取统计信息
    getStats() {
      return unifiedAIApi.getStats()
    },
    
    // 获取配置管理器
    getConfigManager() {
      return unifiedAIApi.getConfigManager()
    },
    
    // 获取错误处理器
    getErrorHandler() {
      return unifiedAIApi.getErrorHandler()
    },
    
    // 清除缓存
    clearCache() {
      unifiedAIApi.clearCache()
    },
    
    // 重置统计
    resetStats() {
      unifiedAIApi.resetStats()
    }
  }
}

// 默认导出
export default unifiedAIApi