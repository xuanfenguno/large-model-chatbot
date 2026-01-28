/**
 * AI API配置管理系统
 * 统一管理API密钥和模型配置
 */

class AIConfigManager {
  constructor() {
    this.storageKey = 'ai_api_config'
    this.defaultConfig = this._getDefaultConfig()
    this.loadConfig()
  }

  /**
   * 获取默认配置
   */
  _getDefaultConfig() {
    return {
      // API密钥配置（只保留国内模型）
      apiKeys: {
        DEEPSEEK_API_KEY: '',
        QWEN_API_KEY: 'sk-f3fa5090eb8547ce8a7aa2236c9d1997',
        KIMI_API_KEY: '',
        DOUBAO_API_KEY: '',
        BAILIAN_API_KEY: ''
      },
      
      // 模型默认配置
      defaultModel: 'qwen-plus',
      
      // 模型参数配置（只保留国内模型）
      modelConfigs: {
        'deepseek-chat': {
          temperature: 0.6,
          maxTokens: 2000,
          topP: 0.7
        },
        'qwen-turbo': {
          temperature: 0.6,
          maxTokens: 2000,
          topP: 0.7
        },
        'qwen-plus': {
          temperature: 0.6,
          maxTokens: 2000,
          topP: 0.7
        },
        'qwen-max': {
          temperature: 0.6,
          maxTokens: 2000,
          topP: 0.7
        },
        'kimi-chat': {
          temperature: 0.6,
          maxTokens: 2000,
          topP: 0.7
        },
        'doubao-chat': {
          temperature: 0.6,
          maxTokens: 2000,
          topP: 0.7
        },
        'bailian-chat': {
          temperature: 0.6,
          maxTokens: 2000,
          topP: 0.7
        }
      },
      
      // 全局配置
      globalConfig: {
        timeout: 30000,
        maxRetries: 3,
        enableStreaming: true,
        enableCache: true,
        cacheDuration: 300000 // 5分钟
      }
    }
  }

  /**
   * 加载配置
   */
  loadConfig() {
    try {
      const storedConfig = localStorage.getItem(this.storageKey)
      if (storedConfig) {
        const parsedConfig = JSON.parse(storedConfig)
        this.config = { ...this.defaultConfig, ...parsedConfig }
      } else {
        this.config = { ...this.defaultConfig }
        this.saveConfig()
      }
    } catch (error) {
      console.error('加载配置失败:', error)
      this.config = { ...this.defaultConfig }
    }
  }

  /**
   * 保存配置
   */
  saveConfig() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.config))
    } catch (error) {
      console.error('保存配置失败:', error)
    }
  }

  /**
   * 获取API密钥
   * @param {string} provider - 提供商名称
   * @returns {string} API密钥
   */
  getApiKey(provider) {
    const keyName = this._getApiKeyName(provider)
    return this.config.apiKeys[keyName] || ''
  }

  /**
   * 设置API密钥
   * @param {string} provider - 提供商名称
   * @param {string} apiKey - API密钥
   */
  setApiKey(provider, apiKey) {
    const keyName = this._getApiKeyName(provider)
    this.config.apiKeys[keyName] = apiKey
    this.saveConfig()
  }

  /**
   * 获取所有API密钥
   * @returns {Object} API密钥对象
   */
  getAllApiKeys() {
    return { ...this.config.apiKeys }
  }

  /**
   * 设置所有API密钥
   * @param {Object} apiKeys - API密钥对象
   */
  setAllApiKeys(apiKeys) {
    this.config.apiKeys = { ...this.config.apiKeys, ...apiKeys }
    this.saveConfig()
  }

  /**
   * 获取模型配置
   * @param {string} modelId - 模型ID
   * @returns {Object} 模型配置
   */
  getModelConfig(modelId) {
    return this.config.modelConfigs[modelId] || {
      temperature: 0.6,
      maxTokens: 2000,
      topP: 0.7
    }
  }

  /**
   * 设置模型配置
   * @param {string} modelId - 模型ID
   * @param {Object} config - 模型配置
   */
  setModelConfig(modelId, config) {
    this.config.modelConfigs[modelId] = { ...config }
    this.saveConfig()
  }

  /**
   * 获取默认模型
   * @returns {string} 默认模型ID
   */
  getDefaultModel() {
    return this.config.defaultModel
  }

  /**
   * 设置默认模型
   * @param {string} modelId - 模型ID
   */
  setDefaultModel(modelId) {
    this.config.defaultModel = modelId
    this.saveConfig()
  }

  /**
   * 获取全局配置
   * @returns {Object} 全局配置
   */
  getGlobalConfig() {
    return { ...this.config.globalConfig }
  }

  /**
   * 设置全局配置
   * @param {Object} config - 全局配置
   */
  setGlobalConfig(config) {
    this.config.globalConfig = { ...this.config.globalConfig, ...config }
    this.saveConfig()
  }

  /**
   * 验证配置完整性
   * @returns {Object} 验证结果
   */
  validateConfig() {
    const errors = []
    const warnings = []
    
    // 检查API密钥
    Object.entries(this.config.apiKeys).forEach(([key, value]) => {
      if (!value) {
        warnings.push(`未配置${key}`)
      } else if (value.length < 10) {
        errors.push(`${key}格式不正确`)
      }
    })
    
    // 检查默认模型
    if (!this.config.defaultModel) {
      errors.push('未设置默认模型')
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      hasWarnings: warnings.length > 0
    }
  }

  /**
   * 导出配置
   * @returns {string} 配置JSON字符串
   */
  exportConfig() {
    return JSON.stringify(this.config, null, 2)
  }

  /**
   * 导入配置
   * @param {string} configJson - 配置JSON字符串
   * @returns {boolean} 是否导入成功
   */
  importConfig(configJson) {
    try {
      const newConfig = JSON.parse(configJson)
      this.config = { ...this.defaultConfig, ...newConfig }
      this.saveConfig()
      return true
    } catch (error) {
      console.error('导入配置失败:', error)
      return false
    }
  }

  /**
   * 重置配置
   */
  resetConfig() {
    this.config = { ...this.defaultConfig }
    this.saveConfig()
  }

  /**
   * 获取提供商对应的API密钥名称
   * @param {string} provider - 提供商名称
   * @returns {string} API密钥名称
   */
  _getApiKeyName(provider) {
    const keyMap = {
      'deepseek': 'DEEPSEEK_API_KEY',
      'qwen': 'QWEN_API_KEY',
      'kimi': 'KIMI_API_KEY',
      'doubao': 'DOUBAO_API_KEY',
      'bailian': 'BAILIAN_API_KEY'
    }
    
    return keyMap[provider.toLowerCase()] || `${provider.toUpperCase()}_API_KEY`
  }

  /**
   * 获取支持的提供商列表
   * @returns {Array} 提供商列表
   */
  getSupportedProviders() {
    return [
      {
        id: 'deepseek',
        name: 'DeepSeek',
        description: '深度求索AI模型',
        website: 'https://deepseek.com',
        apiKeyName: 'DEEPSEEK_API_KEY'
      },
      {
        id: 'qwen',
        name: '通义千问',
        description: '阿里云AI模型',
        website: 'https://qwen.com',
        apiKeyName: 'QWEN_API_KEY'
      },
      {
        id: 'kimi',
        name: 'Kimi',
        description: '月之暗面AI助手',
        website: 'https://kimi.com',
        apiKeyName: 'KIMI_API_KEY'
      },
      {
        id: 'doubao',
        name: '豆包',
        description: '字节跳动AI助手',
        website: 'https://doubao.com',
        apiKeyName: 'DOUBAO_API_KEY'
      },
      {
        id: 'bailian',
        name: '百炼',
        description: '阿里云百炼平台',
        website: 'https://bailian.aliyun.com',
        apiKeyName: 'BAILIAN_API_KEY'
      }
    ]
  }

  /**
   * 获取模型偏好设置
   * @returns {Object} 偏好设置
   */
  getPreferences() {
    // 默认偏好设置
    const defaultPreferences = {
      preferredCapabilities: [],
      preferredProviders: [],
      preferredModels: []
    };
    
    // 从配置中获取偏好设置，如果没有则使用默认值
    const preferences = this.config.preferences || defaultPreferences;
    
    return { ...defaultPreferences, ...preferences };
  }

  /**
   * 设置模型偏好设置
   * @param {Object} preferences - 偏好设置
   */
  setPreferences(preferences) {
    this.config.preferences = { ...this.config.preferences, ...preferences };
    this.saveConfig();
  }

  /**
   * 获取配置摘要
   * @returns {Object} 配置摘要
   */
  getConfigSummary() {
    const apiKeys = this.config.apiKeys
    const configuredProviders = Object.entries(apiKeys)
      .filter(([_, value]) => value && value.length > 10)
      .map(([key]) => key.replace('_API_KEY', ''))
    
    return {
      totalProviders: Object.keys(apiKeys).length,
      configuredProviders: configuredProviders.length,
      defaultModel: this.config.defaultModel,
      hasValidConfig: configuredProviders.length > 0
    }
  }
}

// 创建全局配置管理器实例
export const aiConfigManager = new AIConfigManager()

// Vue composable
export function useAIConfig() {
  return {
    configManager: aiConfigManager,
    
    // 获取API密钥
    getApiKey(provider) {
      return aiConfigManager.getApiKey(provider)
    },
    
    // 设置API密钥
    setApiKey(provider, apiKey) {
      aiConfigManager.setApiKey(provider, apiKey)
    },
    
    // 获取所有API密钥
    getAllApiKeys() {
      return aiConfigManager.getAllApiKeys()
    },
    
    // 设置所有API密钥
    setAllApiKeys(apiKeys) {
      aiConfigManager.setAllApiKeys(apiKeys)
    },
    
    // 获取模型配置
    getModelConfig(modelId) {
      return aiConfigManager.getModelConfig(modelId)
    },
    
    // 获取默认模型
    getDefaultModel() {
      return aiConfigManager.getDefaultModel()
    },
    
    // 设置默认模型
    setDefaultModel(modelId) {
      aiConfigManager.setDefaultModel(modelId)
    },
    
    // 验证配置
    validateConfig() {
      return aiConfigManager.validateConfig()
    },
    
    // 获取配置摘要
    getConfigSummary() {
      return aiConfigManager.getConfigSummary()
    },
    
    // 获取支持的提供商
    getSupportedProviders() {
      return aiConfigManager.getSupportedProviders()
    },
    
    // 获取偏好设置
    getPreferences() {
      return aiConfigManager.getPreferences()
    },
    
    // 设置偏好设置
    setPreferences(preferences) {
      aiConfigManager.setPreferences(preferences)
    }
  }
}