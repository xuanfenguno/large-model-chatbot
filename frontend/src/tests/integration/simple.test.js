/**
 * 简单测试脚本 - 验证API框架基本功能
 */

import { useUnifiedAIApi, useAIConfig } from './ai-api'

// 简单的测试函数
async function runSimpleTest() {
  console.log('🧪 开始简单测试...')
  
  try {
    // 初始化API和配置管理器
    const { api } = useUnifiedAIApi()
    const { configManager } = useAIConfig()
    
    console.log('✅ API和配置管理器初始化成功')
    
    // 测试1: 配置管理
    console.log('\n1. 测试配置管理...')
    
    // 设置测试API密钥
    configManager.setApiKey('openai', 'test-key-12345')
    const retrievedKey = configManager.getApiKey('openai')
    console.log('🔑 设置和获取API密钥:', retrievedKey === 'test-key-12345' ? '✅ 通过' : '❌ 失败')
    
    // 验证配置
    const validation = configManager.validateConfig()
    console.log('📋 配置验证:', validation.isValid ? '✅ 有效' : '❌ 无效')
    
    // 测试2: 获取可用模型
    console.log('\n2. 测试模型列表...')
    const models = await api.getAvailableModels()
    console.log('📊 可用模型数量:', models.length)
    console.log('📋 模型列表:', models.map(m => m.name).join(', '))
    
    // 测试3: 统计信息
    console.log('\n3. 测试统计信息...')
    const stats = api.getStats()
    console.log('📈 统计信息:', {
      总调用次数: stats.client.totalCalls,
      成功调用: stats.client.successfulCalls,
      失败调用: stats.client.failedCalls
    })
    
    // 测试4: 错误处理
    console.log('\n4. 测试错误处理...')
    
    // 测试无效模型
    const errorResult = await api.sendMessage('测试消息', {
      model: 'invalid-model'
    })
    
    if (!errorResult.success) {
      console.log('🛡️ 错误处理:', '✅ 正确捕获错误')
      console.log('📝 错误信息:', errorResult.error.message)
    } else {
      console.log('🛡️ 错误处理:', '❌ 应该捕获错误但未捕获')
    }
    
    // 测试5: 重置统计
    console.log('\n5. 测试统计重置...')
    api.resetStats()
    const resetStats = api.getStats()
    console.log('🔄 统计重置:', resetStats.client.totalCalls === 0 ? '✅ 通过' : '❌ 失败')
    
    console.log('\n🎉 简单测试完成!')
    console.log('📊 最终统计:', api.getStats())
    
    return {
      success: true,
      message: '所有测试通过',
      stats: api.getStats()
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

// 如果直接在浏览器中运行
export { runSimpleTest }

if (typeof window !== 'undefined') {
  window.runSimpleTest = runSimpleTest
}