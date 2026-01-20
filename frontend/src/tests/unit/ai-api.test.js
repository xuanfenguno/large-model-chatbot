/**
 * 大模型API框架测试脚本
 * 用于验证API框架的各个组件功能
 */

import { useUnifiedAIApi } from '@/utils/ai-api'
import { useAIConfig } from '@/utils/ai-config'

class AIAPITest {
  constructor() {
    this.api = useUnifiedAIApi().api
    this.configManager = useAIConfig().configManager
    this.testResults = []
  }

  // 测试配置管理
  async testConfigManagement() {
    console.log('🧪 开始测试配置管理...')
    
    const tests = [
      {
        name: '设置和获取API密钥',
        test: () => {
          const testKey = 'test-key-12345'
          this.configManager.setApiKey('openai', testKey)
          const retrievedKey = this.configManager.getApiKey('openai')
          return retrievedKey === testKey
        }
      },
      {
        name: '验证配置有效性',
        test: () => {
          const result = this.configManager.validateConfig()
          return typeof result.isValid === 'boolean' && 
                 Array.isArray(result.errors) && 
                 Array.isArray(result.warnings)
        }
      },
      {
        name: '模型配置管理',
        test: () => {
          const modelConfig = {
            temperature: 0.7,
            maxTokens: 2000,
            topP: 0.8
          }
          this.configManager.setModelConfig('gpt-4', modelConfig)
          const retrievedConfig = this.configManager.getModelConfig('gpt-4')
          return retrievedConfig.temperature === 0.7 &&
                 retrievedConfig.maxTokens === 2000
        }
      },
      {
        name: '全局配置管理',
        test: () => {
          const globalConfig = {
            timeout: 30000,
            maxRetries: 3,
            enableStreaming: true
          }
          this.configManager.setGlobalConfig(globalConfig)
          const retrievedConfig = this.configManager.getGlobalConfig()
          return retrievedConfig.timeout === 30000 &&
                 retrievedConfig.maxRetries === 3
        }
      }
    ]

    return this.runTests('配置管理', tests)
  }

  // 测试错误处理
  async testErrorHandling() {
    console.log('🧪 开始测试错误处理...')
    
    const tests = [
      {
        name: '网络错误处理',
        test: async () => {
          // 模拟网络错误
          const result = await this.api.sendMessage('测试消息', {
            model: 'invalid-model',
            simulateError: 'network'
          })
          return !result.success && result.error.type === 'network'
        }
      },
      {
        name: 'API错误处理',
        test: async () => {
          // 模拟API错误
          const result = await this.api.sendMessage('测试消息', {
            model: 'invalid-model',
            simulateError: 'api'
          })
          return !result.success && result.error.type === 'api'
        }
      },
      {
        name: '参数验证错误',
        test: async () => {
          // 测试无效参数
          const result = await this.api.sendMessage('', {
            model: ''
          })
          return !result.success && result.error.type === 'validation'
        }
      }
    ]

    return this.runTests('错误处理', tests)
  }

  // 测试API调用
  async testAPICalls() {
    console.log('🧪 开始测试API调用...')
    
    const tests = [
      {
        name: '基础消息发送',
        test: async () => {
          const result = await this.api.sendMessage('你好，这是一个测试消息', {
            model: 'deepseek-chat'
          })
          return result.success && typeof result.content === 'string'
        }
      },
      {
        name: '带参数的消息发送',
        test: async () => {
          const result = await this.api.sendMessage('测试温度参数', {
            model: 'deepseek-chat',
            temperature: 0.5,
            maxTokens: 100
          })
          return result.success && result.content.length > 0
        }
      },
      {
        name: '获取可用模型列表',
        test: async () => {
          const models = await this.api.getAvailableModels()
          return Array.isArray(models) && models.length > 0
        }
      },
      {
        name: '统计信息获取',
        test: async () => {
          const stats = this.api.getStats()
          return typeof stats === 'object' && 
                 typeof stats.client.totalCalls === 'number'
        }
      }
    ]

    return this.runTests('API调用', tests)
  }

  // 测试流式响应
  async testStreaming() {
    console.log('🧪 开始测试流式响应...')
    
    const tests = [
      {
        name: '流式消息发送',
        test: async () => {
          return new Promise((resolve) => {
            let receivedChunks = 0
            
            this.api.sendMessageStream('流式测试消息', {
              model: 'deepseek-chat'
            }, (chunk) => {
              receivedChunks++
              console.log('收到流式数据块:', chunk)
            }).then((result) => {
              resolve(result.success && receivedChunks > 0)
            }).catch(() => {
              resolve(false)
            })
          })
        }
      }
    ]

    return this.runTests('流式响应', tests)
  }

  // 测试性能监控
  async testPerformanceMonitoring() {
    console.log('🧪 开始测试性能监控...')
    
    const tests = [
      {
        name: '统计信息更新',
        test: async () => {
          const initialStats = this.api.getStats()
          const initialCalls = initialStats.client.totalCalls
          
          // 发送测试消息
          await this.api.sendMessage('性能测试消息', {
            model: 'deepseek-chat'
          })
          
          const updatedStats = this.api.getStats()
          return updatedStats.client.totalCalls === initialCalls + 1
        }
      },
      {
        name: '统计重置功能',
        test: async () => {
          this.api.resetStats()
          const stats = this.api.getStats()
          return stats.client.totalCalls === 0
        }
      },
      {
        name: '缓存清除功能',
        test: () => {
          this.api.clearCache()
          // 缓存清除没有返回值，主要检查是否抛出错误
          return true
        }
      }
    ]

    return this.runTests('性能监控', tests)
  }

  // 运行测试套件
  async runTests(category, tests) {
    const results = []
    
    for (const test of tests) {
      try {
        const startTime = Date.now()
        const passed = await test.test()
        const duration = Date.now() - startTime
        
        results.push({
          category,
          name: test.name,
          passed,
          duration,
          error: null
        })
        
        console.log(`  ${passed ? '✅' : '❌'} ${test.name} (${duration}ms)`)
        
      } catch (error) {
        results.push({
          category,
          name: test.name,
          passed: false,
          duration: 0,
          error: error.message
        })
        
        console.log(`  ❌ ${test.name} - 错误: ${error.message}`)
      }
    }
    
    return results
  }

  // 运行所有测试
  async runAllTests() {
    console.log('🚀 开始运行大模型API框架测试...\n')
    
    const testSuites = [
      this.testConfigManagement.bind(this),
      this.testErrorHandling.bind(this),
      this.testAPICalls.bind(this),
      this.testStreaming.bind(this),
      this.testPerformanceMonitoring.bind(this)
    ]
    
    for (const testSuite of testSuites) {
      const results = await testSuite()
      this.testResults.push(...results)
      console.log('')
    }
    
    this.generateReport()
  }

  // 生成测试报告
  generateReport() {
    console.log('📊 测试报告')
    console.log('='.repeat(50))
    
    const totalTests = this.testResults.length
    const passedTests = this.testResults.filter(r => r.passed).length
    const failedTests = totalTests - passedTests
    
    // 按类别统计
    const categories = [...new Set(this.testResults.map(r => r.category))]
    
    categories.forEach(category => {
      const categoryTests = this.testResults.filter(r => r.category === category)
      const categoryPassed = categoryTests.filter(r => r.passed).length
      
      console.log(`\n${category}: ${categoryPassed}/${categoryTests.length} 通过`)
      
      categoryTests.forEach(test => {
        const status = test.passed ? '✅' : '❌'
        console.log(`  ${status} ${test.name} (${test.duration}ms)`)
        if (test.error) {
          console.log(`     错误: ${test.error}`)
        }
      })
    })
    
    console.log('\n' + '='.repeat(50))
    console.log(`总计: ${passedTests}/${totalTests} 测试通过 (${Math.round((passedTests/totalTests)*100)}%)`)
    
    if (failedTests > 0) {
      console.log('\n❌ 失败的测试:')
      this.testResults
        .filter(r => !r.passed)
        .forEach(test => {
          console.log(`  - ${test.category}: ${test.name}`)
          if (test.error) {
            console.log(`    错误: ${test.error}`)
          }
        })
    }
    
    // 性能统计
    const avgDuration = this.testResults.reduce((sum, test) => sum + test.duration, 0) / totalTests
    console.log(`\n⏱️  平均测试时间: ${Math.round(avgDuration)}ms`)
    
    return {
      totalTests,
      passedTests,
      failedTests,
      successRate: (passedTests / totalTests) * 100,
      avgDuration
    }
  }
}

// 导出测试类
export { AIAPITest }

// 如果直接运行此文件，则执行测试
if (typeof window !== 'undefined' && window.location.pathname.includes('test')) {
  const testRunner = new AIAPITest()
  testRunner.runAllTests().catch(console.error)
}