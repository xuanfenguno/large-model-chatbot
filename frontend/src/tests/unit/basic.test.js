/**
 * 基础功能测试 - 验证API框架核心功能
 */

// 模拟的AI客户端类
class MockAIClient {
  constructor() {
    this.stats = {
      totalCalls: 0,
      successfulCalls: 0,
      failedCalls: 0,
      averageResponseTime: 0
    }
  }

  async sendMessage(message, options = {}) {
    const startTime = Date.now()
    this.stats.totalCalls++
    
    try {
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // 模拟成功响应
      const responseTime = Date.now() - startTime
      this.stats.successfulCalls++
      
      return {
        success: true,
        content: `这是对"${message}"的模拟回复 (使用模型: ${options.model || 'default'})`,
        model: options.model || 'default',
        responseTime
      }
      
    } catch (error) {
      this.stats.failedCalls++
      
      return {
        success: false,
        error: error.message,
        errorCode: 'MOCK_ERROR'
      }
    }
  }

  getStats() {
    return {
      client: this.stats,
      config: {
        configuredProviders: 3,
        totalProviders: 7,
        defaultModel: 'deepseek-chat'
      }
    }
  }

  resetStats() {
    this.stats = {
      totalCalls: 0,
      successfulCalls: 0,
      failedCalls: 0,
      averageResponseTime: 0
    }
  }

  clearCache() {
    console.log('缓存已清除')
  }
}

// 模拟的配置管理器
class MockConfigManager {
  constructor() {
    this.apiKeys = {}
    this.modelConfigs = {}
    this.globalConfig = {
      timeout: 30000,
      maxRetries: 3,
      enableStreaming: true,
      enableCache: true,
      cacheDuration: 300000
    }
  }

  setApiKey(provider, key) {
    this.apiKeys[provider] = key
  }

  getApiKey(provider) {
    return this.apiKeys[provider] || null
  }

  setAllApiKeys(keys) {
    this.apiKeys = { ...keys }
  }

  getAllApiKeys() {
    return { ...this.apiKeys }
  }

  setDefaultModel(model) {
    this.defaultModel = model
  }

  getDefaultModel() {
    return this.defaultModel || 'deepseek-chat'
  }

  setModelConfig(model, config) {
    this.modelConfigs[model] = { ...config }
  }

  getModelConfig(model) {
    return this.modelConfigs[model] || {
      temperature: 0.6,
      maxTokens: 2000,
      topP: 0.7
    }
  }

  setGlobalConfig(config) {
    this.globalConfig = { ...config }
  }

  getGlobalConfig() {
    return { ...this.globalConfig }
  }

  validateConfig() {
    const errors = []
    const warnings = []
    
    // 检查是否有配置的API密钥
    const configuredKeys = Object.keys(this.apiKeys).filter(key => this.apiKeys[key])
    
    if (configuredKeys.length === 0) {
      warnings.push('未配置任何API密钥')
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      configuredProviders: configuredKeys.length
    }
  }

  getSupportedProviders() {
    return [
      { id: 'openai', name: 'OpenAI', apiKeyName: 'openaiApiKey', description: 'GPT系列模型' },
      { id: 'deepseek', name: 'DeepSeek', apiKeyName: 'deepseekApiKey', description: '深度求索模型' },
      { id: 'claude', name: 'Claude', apiKeyName: 'claudeApiKey', description: 'Anthropic模型' }
    ]
  }

  resetConfig() {
    this.apiKeys = {}
    this.modelConfigs = {}
    this.globalConfig = {
      timeout: 30000,
      maxRetries: 3,
      enableStreaming: true,
      enableCache: true,
      cacheDuration: 300000
    }
  }
}

// 基础测试函数
async function runBasicTest() {
  console.log('🧪 开始基础功能测试...\n')
  
  try {
    // 创建模拟客户端和配置管理器
    const mockApi = new MockAIClient()
    const mockConfig = new MockConfigManager()
    
    console.log('✅ 模拟组件初始化成功')
    
    // 测试1: 配置管理
    console.log('\n1. 测试配置管理...')
    
    mockConfig.setApiKey('openai', 'test-key-12345')
    const retrievedKey = mockConfig.getApiKey('openai')
    console.log('🔑 API密钥管理:', retrievedKey === 'test-key-12345' ? '✅ 通过' : '❌ 失败')
    
    const validation = mockConfig.validateConfig()
    console.log('📋 配置验证:', validation.isValid ? '✅ 有效' : '❌ 无效')
    
    // 测试2: API调用
    console.log('\n2. 测试API调用...')
    
    const result = await mockApi.sendMessage('你好，这是一个测试消息', {
      model: 'deepseek-chat',
      temperature: 0.7
    })
    
    console.log('📡 API调用:', result.success ? '✅ 成功' : '❌ 失败')
    console.log('💬 回复内容:', result.content)
    
    // 测试3: 统计信息
    console.log('\n3. 测试统计信息...')
    
    const stats = mockApi.getStats()
    console.log('📈 调用统计:', {
      总调用次数: stats.client.totalCalls,
      成功调用: stats.client.successfulCalls,
      失败调用: stats.client.failedCalls
    })
    
    // 测试4: 统计重置
    console.log('\n4. 测试统计重置...')
    
    mockApi.resetStats()
    const resetStats = mockApi.getStats()
    console.log('🔄 统计重置:', resetStats.client.totalCalls === 0 ? '✅ 通过' : '❌ 失败')
    
    // 测试5: 模型配置
    console.log('\n5. 测试模型配置...')
    
    mockConfig.setModelConfig('gpt-4', { temperature: 0.8, maxTokens: 3000 })
    const modelConfig = mockConfig.getModelConfig('gpt-4')
    console.log('⚙️ 模型配置:', modelConfig.temperature === 0.8 ? '✅ 通过' : '❌ 失败')
    
    // 测试6: 全局配置
    console.log('\n6. 测试全局配置...')
    
    mockConfig.setGlobalConfig({ timeout: 45000, maxRetries: 5 })
    const globalConfig = mockConfig.getGlobalConfig()
    console.log('🌐 全局配置:', globalConfig.timeout === 45000 ? '✅ 通过' : '❌ 失败')
    
    // 测试7: 支持的提供商
    console.log('\n7. 测试提供商列表...')
    
    const providers = mockConfig.getSupportedProviders()
    console.log('🏢 支持的提供商:', providers.length, '个')
    providers.forEach(provider => {
      console.log(`   - ${provider.name}: ${provider.description}`)
    })
    
    console.log('\n🎉 基础功能测试完成!')
    console.log('📊 最终统计:', mockApi.getStats())
    
    return {
      success: true,
      message: '所有基础测试通过',
      stats: mockApi.getStats(),
      config: mockConfig.validateConfig()
    }
    
  } catch (error) {
    console.error('❌ 测试失败:', error)
    return {
      success: false,
      message: error.message,
      error: error
    }
  }
}

// 导出测试函数
export { runBasicTest, MockAIClient, MockConfigManager }

// 如果直接在浏览器中运行
if (typeof window !== 'undefined') {
  window.runBasicTest = runBasicTest
  window.MockAIClient = MockAIClient
  window.MockConfigManager = MockConfigManager
}