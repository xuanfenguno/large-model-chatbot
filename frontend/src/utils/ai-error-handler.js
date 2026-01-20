/**
 * AI API错误处理和重试机制
 */

import { ElMessage } from 'element-plus'

class AIErrorHandler {
  constructor() {
    this.maxRetries = 3
    this.retryDelay = 1000 // 1秒
    this.errorMessages = {
      // 网络错误
      'NETWORK_ERROR': '网络连接失败，请检查网络设置',
      'TIMEOUT_ERROR': '请求超时，请稍后重试',
      
      // API错误
      'INVALID_API_KEY': 'API密钥无效，请检查配置',
      'QUOTA_EXCEEDED': 'API调用额度已用完',
      'RATE_LIMIT_EXCEEDED': '请求频率过高，请稍后重试',
      'MODEL_NOT_FOUND': '模型不存在或不可用',
      
      // 参数错误
      'INVALID_PARAMETERS': '请求参数无效',
      'CONTENT_FILTERED': '内容被过滤，请调整输入',
      
      // 提供商错误
      'PROVIDER_UNAVAILABLE': '服务暂时不可用',
      'AUTHENTICATION_FAILED': '身份验证失败',
      
      // 未知错误
      'UNKNOWN_ERROR': '发生未知错误，请稍后重试'
    }
  }

  /**
   * 处理API错误
   * @param {Error} error - 错误对象
   * @param {Object} context - 错误上下文
   * @returns {Object} 处理结果
   */
  handleError(error, context = {}) {
    const errorInfo = this._parseError(error)
    
    // 记录错误日志
    this._logError(errorInfo, context)
    
    // 显示用户友好的错误消息
    this._showUserMessage(errorInfo)
    
    // 返回错误信息
    return {
      success: false,
      error: errorInfo.message,
      errorCode: errorInfo.code,
      retryable: errorInfo.retryable,
      context
    }
  }

  /**
   * 带重试机制的API调用
   * @param {Function} apiCall - API调用函数
   * @param {Object} options - 重试选项
   * @returns {Promise} API调用结果
   */
  async withRetry(apiCall, options = {}) {
    const maxRetries = options.maxRetries || this.maxRetries
    const retryDelay = options.retryDelay || this.retryDelay
    
    let lastError
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const result = await apiCall()
        
        // 如果成功，返回结果
        if (result.success !== false) {
          return result
        }
        
        // 检查是否可重试
        if (!this._isRetryable(result.errorCode)) {
          return result
        }
        
        lastError = result
        
      } catch (error) {
        const errorInfo = this._parseError(error)
        
        // 检查是否可重试
        if (!errorInfo.retryable || attempt === maxRetries) {
          throw error
        }
        
        lastError = errorInfo
      }
      
      // 等待一段时间后重试
      if (attempt < maxRetries) {
        const delay = retryDelay * Math.pow(2, attempt - 1) // 指数退避
        await this._sleep(delay)
        
        console.log(`第${attempt}次重试，等待${delay}ms...`)
      }
    }
    
    throw lastError || new Error('重试次数用尽')
  }

  /**
   * 解析错误信息
   * @param {Error} error - 错误对象
   * @returns {Object} 解析后的错误信息
   */
  _parseError(error) {
    const errorString = error.message || error.toString()
    
    // 网络错误
    if (errorString.includes('Network Error') || errorString.includes('Failed to fetch')) {
      return {
        code: 'NETWORK_ERROR',
        message: this.errorMessages.NETWORK_ERROR,
        retryable: true
      }
    }
    
    // 超时错误
    if (errorString.includes('timeout') || errorString.includes('Timeout')) {
      return {
        code: 'TIMEOUT_ERROR',
        message: this.errorMessages.TIMEOUT_ERROR,
        retryable: true
      }
    }
    
    // API密钥错误
    if (errorString.includes('API key') || errorString.includes('401') || errorString.includes('403')) {
      return {
        code: 'INVALID_API_KEY',
        message: this.errorMessages.INVALID_API_KEY,
        retryable: false
      }
    }
    
    // 额度限制
    if (errorString.includes('quota') || errorString.includes('429')) {
      return {
        code: 'RATE_LIMIT_EXCEEDED',
        message: this.errorMessages.RATE_LIMIT_EXCEEDED,
        retryable: true
      }
    }
    
    // 模型不存在
    if (errorString.includes('model') && errorString.includes('not found')) {
      return {
        code: 'MODEL_NOT_FOUND',
        message: this.errorMessages.MODEL_NOT_FOUND,
        retryable: false
      }
    }
    
    // 默认错误
    return {
      code: 'UNKNOWN_ERROR',
      message: this.errorMessages.UNKNOWN_ERROR,
      retryable: false
    }
  }

  /**
   * 检查错误是否可重试
   * @param {string} errorCode - 错误代码
   * @returns {boolean} 是否可重试
   */
  _isRetryable(errorCode) {
    const retryableErrors = [
      'NETWORK_ERROR',
      'TIMEOUT_ERROR',
      'RATE_LIMIT_EXCEEDED',
      'PROVIDER_UNAVAILABLE'
    ]
    
    return retryableErrors.includes(errorCode)
  }

  /**
   * 显示用户友好的错误消息
   * @param {Object} errorInfo - 错误信息
   */
  _showUserMessage(errorInfo) {
    const { code, message } = errorInfo
    
    switch (code) {
      case 'INVALID_API_KEY':
        ElMessage.error({
          message: message,
          duration: 5000,
          showClose: true
        })
        break
        
      case 'QUOTA_EXCEEDED':
        ElMessage.warning({
          message: message,
          duration: 5000,
          showClose: true
        })
        break
        
      case 'RATE_LIMIT_EXCEEDED':
        ElMessage.warning({
          message: message,
          duration: 3000
        })
        break
        
      default:
        ElMessage.error({
          message: message,
          duration: 3000
        })
    }
  }

  /**
   * 记录错误日志
   * @param {Object} errorInfo - 错误信息
   * @param {Object} context - 错误上下文
   */
  _logError(errorInfo, context) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      errorCode: errorInfo.code,
      errorMessage: errorInfo.message,
      context: {
        model: context.model,
        provider: context.provider,
        messageLength: context.messageLength
      }
    }
    
    console.error('AI API错误:', logEntry)
    
    // 在实际项目中，这里可以发送到错误监控服务
    // this._sendToMonitoringService(logEntry)
  }

  /**
   * 等待指定时间
   * @param {number} ms - 等待毫秒数
   * @returns {Promise} 
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * 创建错误监控
   */
  createErrorMonitor() {
    return {
      // 错误统计
      errors: [],
      
      // 添加错误
      addError(errorInfo, context) {
        this.errors.push({
          ...errorInfo,
          timestamp: Date.now(),
          context
        })
        
        // 只保留最近100个错误
        if (this.errors.length > 100) {
          this.errors = this.errors.slice(-100)
        }
      },
      
      // 获取错误统计
      getStats() {
        const errorCounts = {}
        
        this.errors.forEach(error => {
          errorCounts[error.code] = (errorCounts[error.code] || 0) + 1
        })
        
        return {
          totalErrors: this.errors.length,
          errorCounts,
          recentErrors: this.errors.slice(-10)
        }
      },
      
      // 清除错误记录
      clear() {
        this.errors = []
      }
    }
  }
}

// 创建全局错误处理器实例
export const aiErrorHandler = new AIErrorHandler()

// Vue composable
export function useAIErrorHandler() {
  return {
    errorHandler: aiErrorHandler,
    
    // 处理错误
    handleError(error, context) {
      return aiErrorHandler.handleError(error, context)
    },
    
    // 带重试的API调用
    async withRetry(apiCall, options) {
      return await aiErrorHandler.withRetry(apiCall, options)
    },
    
    // 创建错误监控
    createErrorMonitor() {
      return aiErrorHandler.createErrorMonitor()
    }
  }
}