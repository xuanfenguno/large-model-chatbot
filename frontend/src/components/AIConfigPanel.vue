<template>
  <div class="ai-config-panel">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>大模型API配置</span>
          <el-button type="primary" size="small" @click="showStats = !showStats">
            {{ showStats ? '隐藏统计' : '显示统计' }}
          </el-button>
        </div>
      </template>

      <!-- 统计信息 -->
      <div v-if="showStats" class="stats-section">
        <el-descriptions title="API调用统计" :column="2" border>
          <el-descriptions-item label="总调用次数">{{ stats.client.totalCalls }}</el-descriptions-item>
          <el-descriptions-item label="成功调用">{{ stats.client.successfulCalls }}</el-descriptions-item>
          <el-descriptions-item label="失败调用">{{ stats.client.failedCalls }}</el-descriptions-item>
          <el-descriptions-item label="平均响应时间">{{ Math.round(stats.client.averageResponseTime) }}ms</el-descriptions-item>
          <el-descriptions-item label="配置的提供商">{{ stats.config.configuredProviders }}/{{ stats.config.totalProviders }}</el-descriptions-item>
          <el-descriptions-item label="默认模型">{{ stats.config.defaultModel }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="stats-actions">
          <el-button size="small" @click="resetStats">重置统计</el-button>
          <el-button size="small" @click="clearCache">清除缓存</el-button>
        </div>
      </div>

      <!-- API密钥配置 -->
      <div class="api-keys-section">
        <h3>API密钥配置</h3>
        
        <el-form :model="apiKeys" label-width="120px">
          <el-form-item 
            v-for="provider in supportedProviders" 
            :key="provider.id"
            :label="provider.name"
            :prop="provider.apiKeyName"
          >
            <el-input
              v-model="apiKeys[provider.apiKeyName]"
              :placeholder="`请输入${provider.name} API密钥`"
              show-password
              clearable
            >
              <template #append>
                <el-button 
                  type="primary" 
                  link 
                  @click="openWebsite(provider.website)"
                  v-if="provider.website"
                >
                  获取密钥
                </el-button>
              </template>
            </el-input>
            <div class="provider-description">{{ provider.description }}</div>
          </el-form-item>
        </el-form>

        <div class="form-actions">
          <el-button type="primary" @click="saveApiKeys">保存配置</el-button>
          <el-button @click="resetApiKeys">重置配置</el-button>
          <el-button @click="validateConfig">验证配置</el-button>
        </div>
      </div>

      <!-- 模型配置 -->
      <div class="model-config-section">
        <h3>模型配置</h3>
        
        <el-form :model="modelConfig" label-width="120px">
          <el-form-item label="默认模型">
            <el-select v-model="modelConfig.defaultModel" placeholder="请选择默认模型" filterable>
              <el-option-group
                v-for="group in groupedModels"
                :key="group.label"
                :label="group.label"
              >
                <el-option
                  v-for="model in group.options"
                  :key="model.id"
                  :label="model.name"
                  :value="model.id"
                  :disabled="!model.available"
                >
                  <div class="model-option">
                    <div class="model-info">
                      <span class="model-name">{{ model.name }}</span>
                      <span class="model-provider">({{ model.provider }})</span>
                    </div>
                    <div class="model-meta">
                      <el-tag 
                        v-for="capability in (model.capabilities ? model.capabilities.slice(0, 3) : [])" 
                        :key="capability" 
                        size="small" 
                        type="info" 
                        class="capability-tag"
                      >
                        {{ capability }}
                      </el-tag>
                      <el-tag 
                        v-if="model.pricing" 
                        size="small" 
                        type="warning" 
                        class="pricing-tag"
                      >
                        ¥{{ (model.pricing.input + model.pricing.output).toFixed(2) }}/1M tokens
                      </el-tag>
                      <el-tag 
                        v-if="model.performance" 
                        size="small" 
                        :type="getPerformanceTagType(model.performance.speed)"
                        class="performance-tag"
                      >
                        {{ model.performance.speed }}
                      </el-tag>
                    </div>
                  </div>
                </el-option>
              </el-option-group>
            </el-select>
          </el-form-item>

          <el-form-item label="温度参数">
            <el-slider
              v-model="modelConfig.temperature"
              :min="0"
              :max="2"
              :step="0.1"
              show-stops
            />
            <span class="slider-value">{{ modelConfig.temperature }}</span>
          </el-form-item>

          <el-form-item label="最大Token数">
            <el-input-number
              v-model="modelConfig.maxTokens"
              :min="100"
              :max="4000"
              :step="100"
            />
          </el-form-item>

          <el-form-item label="Top P">
            <el-slider
              v-model="modelConfig.topP"
              :min="0"
              :max="1"
              :step="0.1"
              show-stops
            />
            <span class="slider-value">{{ modelConfig.topP }}</span>
          </el-form-item>
          
          <el-form-item label="模型偏好">
            <div class="preference-section">
              <el-checkbox-group v-model="modelConfig.preferredCapabilities">
                <el-checkbox label="text" border>文本处理</el-checkbox>
                <el-checkbox label="vision" border>视觉理解</el-checkbox>
                <el-checkbox label="audio" border>音频处理</el-checkbox>
                <el-checkbox label="coding" border>代码生成</el-checkbox>
                <el-checkbox label="reasoning" border>逻辑推理</el-checkbox>
                <el-checkbox label="multimodal" border>多模态</el-checkbox>
              </el-checkbox-group>
            </div>
          </el-form-item>
        </el-form>

        <div class="form-actions">
          <el-button type="primary" @click="saveModelConfig">保存模型配置</el-button>
        </div>
      </div>

      <!-- 全局配置 -->
      <div class="global-config-section">
        <h3>全局配置</h3>
        
        <el-form :model="globalConfig" label-width="120px">
          <el-form-item label="请求超时">
            <el-input-number
              v-model="globalConfig.timeout"
              :min="5000"
              :max="60000"
              :step="5000"
            />
            <span class="unit">毫秒</span>
          </el-form-item>

          <el-form-item label="最大重试次数">
            <el-input-number
              v-model="globalConfig.maxRetries"
              :min="0"
              :max="5"
            />
          </el-form-item>

          <el-form-item label="启用流式响应">
            <el-switch v-model="globalConfig.enableStreaming" />
          </el-form-item>

          <el-form-item label="启用缓存">
            <el-switch v-model="globalConfig.enableCache" />
          </el-form-item>

          <el-form-item label="缓存时长" v-if="globalConfig.enableCache">
            <el-input-number
              v-model="globalConfig.cacheDuration"
              :min="60000"
              :max="3600000"
              :step="60000"
            />
            <span class="unit">毫秒</span>
          </el-form-item>
        </el-form>

        <div class="form-actions">
          <el-button type="primary" @click="saveGlobalConfig">保存全局配置</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUnifiedAIApi } from '@/utils/ai-api'
import { useAIConfig } from '@/utils/ai-config'

const { api: aiApi } = useUnifiedAIApi()
const { configManager } = useAIConfig()

// 响应式数据
const showStats = ref(false)
const stats = ref({})
const supportedProviders = ref([])
const availableModels = ref([])

const apiKeys = reactive({})
const modelConfig = reactive({
  defaultModel: '',
  temperature: 0.6,
  maxTokens: 2000,
  topP: 0.7,
  preferredCapabilities: []  // 新增：模型偏好设置
})

const globalConfig = reactive({
  timeout: 30000,
  maxRetries: 3,
  enableStreaming: true,
  enableCache: true,
  cacheDuration: 300000
})

// 生命周期
onMounted(async () => {
  await loadConfig()
  await loadModels()
  updateStats()
})

// 加载配置
const loadConfig = async () => {
  // 加载API密钥
  const keys = configManager.getAllApiKeys()
  Object.assign(apiKeys, keys)
  
  // 加载模型配置
  const defaultModel = configManager.getDefaultModel()
  const modelCfg = configManager.getModelConfig(defaultModel)
  Object.assign(modelConfig, { defaultModel, ...modelCfg })
  
  // 加载模型偏好设置
  const preferences = configManager.getPreferences()
  if (preferences.preferredCapabilities) {
    modelConfig.preferredCapabilities = preferences.preferredCapabilities
  }
  
  // 加载全局配置
  const globalCfg = configManager.getGlobalConfig()
  Object.assign(globalConfig, globalCfg)
  
  // 获取支持的提供商
  supportedProviders.value = configManager.getSupportedProviders()
}

// 加载模型列表
const loadModels = async () => {
  try {
    availableModels.value = await aiApi.getAvailableModels()
    groupModelsByProvider()
  } catch (error) {
    console.error('加载模型列表失败:', error)
    availableModels.value = []
    groupModelsByProvider()
  }
}

// 按提供商分组模型
const groupedModels = ref([])

const groupModelsByProvider = () => {
  // 按组分组模型
  const groups = {}
  availableModels.value.forEach(model => {
    const groupName = model.group || 'Other'
    if (!groups[groupName]) {
      groups[groupName] = []
    }
    groups[groupName].push(model)
  })

  // 转换为选项组格式
  groupedModels.value = Object.keys(groups).map(groupName => ({
    label: groupName,
    options: groups[groupName]
  }))
}

// 根据性能速度获取标签类型
const getPerformanceTagType = (speed) => {
  if (speed === 'very_fast') return 'success'
  if (speed === 'fast') return 'success'
  if (speed === 'medium') return 'warning'
  if (speed === 'slow') return 'danger'
  return 'info'
}

// 更新统计信息
const updateStats = () => {
  stats.value = aiApi.getStats()
}

// 保存API密钥
const saveApiKeys = async () => {
  try {
    configManager.setAllApiKeys(apiKeys)
    ElMessage.success('API密钥保存成功')
    updateStats()
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

// 重置API密钥
const resetApiKeys = async () => {
  try {
    await ElMessageBox.confirm('确定要重置所有API密钥吗？', '确认重置', {
      type: 'warning'
    })
    
    configManager.resetConfig()
    await loadConfig()
    ElMessage.success('API密钥已重置')
    updateStats()
  } catch (error) {
    // 用户取消操作
  }
}

// 验证配置
const validateConfig = () => {
  const result = configManager.validateConfig()
  
  if (result.isValid) {
    if (result.hasWarnings) {
      ElMessage.warning(`配置验证通过，但有警告: ${result.warnings.join('; ')}`)
    } else {
      ElMessage.success('配置验证通过')
    }
  } else {
    ElMessage.error(`配置验证失败: ${result.errors.join('; ')}`)
  }
}

// 保存模型配置
const saveModelConfig = () => {
  try {
    configManager.setDefaultModel(modelConfig.defaultModel)
    configManager.setModelConfig(modelConfig.defaultModel, {
      temperature: modelConfig.temperature,
      maxTokens: modelConfig.maxTokens,
      topP: modelConfig.topP
    })
    
    // 保存模型偏好设置
    configManager.setPreferences({
      preferredCapabilities: modelConfig.preferredCapabilities
    })
    
    ElMessage.success('模型配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

// 保存全局配置
const saveGlobalConfig = () => {
  try {
    configManager.setGlobalConfig(globalConfig)
    ElMessage.success('全局配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

// 重置统计
const resetStats = () => {
  aiApi.resetStats()
  updateStats()
  ElMessage.success('统计信息已重置')
}

// 清除缓存
const clearCache = () => {
  aiApi.clearCache()
  ElMessage.success('缓存已清除')
}

// 打开网站
const openWebsite = (url) => {
  window.open(url, '_blank')
}
</script>

<style scoped>
.ai-config-panel {
  padding: 20px;
}

.config-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-section {
  margin-bottom: 20px;
}

.stats-actions {
  margin-top: 10px;
  text-align: center;
}

.api-keys-section,
.model-config-section,
.global-config-section {
  margin-bottom: 30px;
}

.provider-description {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.slider-value {
  margin-left: 10px;
  color: #409eff;
  font-weight: bold;
}

.unit {
  margin-left: 10px;
  color: #909399;
}

.form-actions {
  text-align: center;
  margin-top: 20px;
}

h3 {
  color: #303133;
  margin-bottom: 15px;
}

/* 模型选择器样式 */
.model-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.model-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.model-name {
  font-weight: bold;
  margin-bottom: 2px;
}

.model-provider {
  font-size: 12px;
  color: #909399;
}

.model-meta {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: flex-end;
  min-width: 150px;
}

.capability-tag,
.pricing-tag,
.performance-tag {
  margin-left: 4px;
  font-size: 10px;
}

.preference-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>