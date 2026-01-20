<template>
  <div class="ai-test-page">
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <h2>大模型API框架测试</h2>
          <div class="header-actions">
            <el-button 
              type="primary" 
              :loading="isRunning" 
              @click="runTests"
            >
              {{ isRunning ? '测试中...' : '运行完整测试' }}
            </el-button>
            <el-button 
              type="success" 
              @click="runSimpleTest"
            >
              运行简单测试
            </el-button>
            <el-button 
              type="warning" 
              @click="runBasicTest"
            >
              运行基础测试
            </el-button>
          </div>
        </div>
      </template>

      <!-- 测试结果 -->
      <div v-if="testResults.length > 0" class="test-results">
        <el-divider>测试报告</el-divider>
        
        <div class="summary">
          <el-statistic 
            title="总测试数" 
            :value="summary.totalTests" 
            class="statistic-item"
          />
          <el-statistic 
            title="通过测试" 
            :value="summary.passedTests" 
            class="statistic-item"
          />
          <el-statistic 
            title="失败测试" 
            :value="summary.failedTests" 
            class="statistic-item"
          />
          <el-statistic 
            title="成功率" 
            :value="summary.successRate" 
            suffix="%"
            class="statistic-item"
          />
        </div>

        <!-- 详细结果 -->
        <div class="detailed-results">
          <el-collapse v-model="activeNames">
            <el-collapse-item 
              v-for="category in categories" 
              :key="category"
              :title="category"
              :name="category"
            >
              <el-table :data="getTestsByCategory(category)" size="small">
                <el-table-column prop="name" label="测试名称" width="300" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.passed ? 'success' : 'danger'">
                      {{ row.passed ? '通过' : '失败' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="duration" label="耗时(ms)" width="100" />
                <el-table-column prop="error" label="错误信息" />
              </el-table>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <!-- 控制台输出 -->
      <div class="console-output">
        <el-divider>控制台输出</el-divider>
        <div class="console-content">
          <pre>{{ consoleOutput }}</pre>
        </div>
      </div>
    </el-card>

    <!-- API配置面板 -->
    <AIConfigPanel />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { AIAPITest } from '@/tests/unit/ai-api.test'
import AIConfigPanel from '@/components/AIConfigPanel.vue'

const isRunning = ref(false)
const testResults = ref([])
const consoleOutput = ref('')
const activeNames = ref([])

// 计算属性
const summary = computed(() => {
  const totalTests = testResults.value.length
  const passedTests = testResults.value.filter(r => r.passed).length
  const failedTests = totalTests - passedTests
  const successRate = totalTests > 0 ? (passedTests / totalTests) * 100 : 0
  
  return {
    totalTests,
    passedTests,
    failedTests,
    successRate: Math.round(successRate)
  }
})

const categories = computed(() => {
  return [...new Set(testResults.value.map(r => r.category))]
})

// 方法
const getTestsByCategory = (category) => {
  return testResults.value
    .filter(r => r.category === category)
    .map(test => ({
      ...test,
      status: test.passed ? '通过' : '失败'
    }))
}

const runTests = async () => {
  isRunning.value = true
  testResults.value = []
  consoleOutput.value = ''
  
  // 重写console.log来捕获输出
  const originalConsoleLog = console.log
  console.log = (...args) => {
    originalConsoleLog(...args)
    consoleOutput.value += args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ') + '\n'
  }
  
  try {
    const testRunner = new AIAPITest()
    await testRunner.runAllTests()
    
    // 收集测试结果
    testResults.value = testRunner.testResults
    
    // 展开所有分类
    activeNames.value = categories.value
    
    ElMessage.success(`测试完成！${summary.value.passedTests}/${summary.value.totalTests} 通过`)
    
  } catch (error) {
    console.error('测试运行错误:', error)
    ElMessage.error('测试运行失败: ' + error.message)
  } finally {
    // 恢复原始console.log
    console.log = originalConsoleLog
    isRunning.value = false
  }
}

// 运行简单测试
const runSimpleTest = async () => {
  const originalConsoleLog = console.log
  consoleOutput.value = ''
  
  console.log = (...args) => {
    originalConsoleLog(...args)
    consoleOutput.value += args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ') + '\n'
  }
  
  try {
    console.log('🚀 开始运行简单测试...\n')
    const result = await window.runSimpleTest()
    
    if (result.success) {
      ElMessage.success('简单测试完成！')
    } else {
      ElMessage.error('简单测试失败: ' + result.message)
    }
    
  } catch (error) {
    console.error('测试运行错误:', error)
    ElMessage.error('简单测试运行失败: ' + error.message)
  } finally {
    console.log = originalConsoleLog
  }
}

// 运行基础测试
const runBasicTest = async () => {
  const originalConsoleLog = console.log
  consoleOutput.value = ''
  
  console.log = (...args) => {
    originalConsoleLog(...args)
    consoleOutput.value += args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ') + '\n'
  }
  
  try {
    console.log('🚀 开始运行基础测试...\n')
    const result = await window.runBasicTest()
    
    if (result.success) {
      ElMessage.success('基础测试完成！')
    } else {
      ElMessage.error('基础测试失败: ' + result.message)
    }
    
  } catch (error) {
    console.error('测试运行错误:', error)
    ElMessage.error('基础测试运行失败: ' + error.message)
  } finally {
    console.log = originalConsoleLog
  }
}

// 页面加载时自动运行测试
onMounted(() => {
  // 可以在这里添加自动测试逻辑
  console.log('AI测试页面已加载')
})
</script>

<style scoped>
.ai-test-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.statistic-item {
  text-align: center;
}

.detailed-results {
  margin-bottom: 20px;
}

.console-output {
  margin-top: 20px;
}

.console-content {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.console-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

@media (max-width: 768px) {
  .summary {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>