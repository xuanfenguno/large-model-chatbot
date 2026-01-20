import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  // 默认设置
  const defaultSettings = {
    // 个人资料设置
    profile: {
      nickname: '',
      avatar: '',
      bio: '',
      email: ''
    },
    
    // AI模型设置
    ai: {
      defaultModel: 'deepseek-v3',
      apiKey: '',
      temperature: 0.7,
      maxTokens: 1000,
      // 各模型的API密钥
      apiKeys: {
        'deepseek-v3': '',
        'gpt-4': '',
        'gpt-3.5': '',
        'claude': '',
        'wenxin': '',
        'qwen': '',
        'llama': ''
      }
    },
    
    // 偏好设置
    preferences: {
      theme: 'light', // light, dark, auto
      language: 'zh', // zh, en
      notifications: true,
      sound: true,
      autoSave: true,
      fontSize: 'medium', // small, medium, large
      compactMode: false
    },
    
    // 聊天设置
    chat: {
      autoScroll: true,
      showTimestamps: true,
      markdownRendering: true,
      typingIndicator: true,
      messageBubbles: true
    },
    
    // 隐私设置
    privacy: {
      saveConversations: true,
      analytics: false,
      dataCollection: false,
      deleteAfter: '30d' // 7d, 30d, 90d, never
    }
  }

  // 响应式状态
  const settings = ref({ ...defaultSettings })

  // 计算属性
  const currentTheme = computed(() => {
    const theme = settings.value.preferences.theme
    if (theme === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return theme
  })

  const currentLanguage = computed(() => settings.value.preferences.language)

  const currentModel = computed(() => settings.value.ai.defaultModel)

  const currentApiKey = computed(() => {
    const model = settings.value.ai.defaultModel
    return settings.value.ai.apiKeys[model] || settings.value.ai.apiKey
  })

  // 初始化设置
  const initSettings = () => {
    const savedSettings = localStorage.getItem('userSettings')
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings)
        // 合并保存的设置和默认设置
        settings.value = {
          ...defaultSettings,
          ...parsedSettings,
          // 确保嵌套对象也被正确合并
          profile: { ...defaultSettings.profile, ...(parsedSettings.profile || {}) },
          ai: { ...defaultSettings.ai, ...(parsedSettings.ai || {}) },
          preferences: { ...defaultSettings.preferences, ...(parsedSettings.preferences || {}) },
          chat: { ...defaultSettings.chat, ...(parsedSettings.chat || {}) },
          privacy: { ...defaultSettings.privacy, ...(parsedSettings.privacy || {}) }
        }
      } catch (error) {
        console.error('加载设置失败:', error)
        // 如果加载失败，使用默认设置
        settings.value = { ...defaultSettings }
      }
    }
    
    // 应用主题
    applyTheme()
    // 应用字体大小
    applyFontSize()
    // 应用语言设置
    applyLanguage()
  }

  // 保存设置
  const saveSettings = () => {
    try {
      localStorage.setItem('userSettings', JSON.stringify(settings.value))
      applyTheme()
      applyFontSize()
      applyLanguage()
      return true
    } catch (error) {
      console.error('保存设置失败:', error)
      return false
    }
  }

  // 重置设置
  const resetSettings = (category = null) => {
    if (category && defaultSettings[category]) {
      settings.value[category] = { ...defaultSettings[category] }
    } else {
      settings.value = { ...defaultSettings }
    }
    saveSettings()
  }

  // 应用主题
  const applyTheme = () => {
    const theme = currentTheme.value
    const html = document.documentElement
    
    // 移除所有主题类
    html.classList.remove('light-theme', 'dark-theme', 'light', 'dark')
    
    if (theme === 'dark') {
      html.classList.add('dark-theme', 'dark')
    } else {
      html.classList.add('light-theme', 'light')
    }
    
    console.log(`[主题] 应用主题: ${theme}`)
  }

  // 应用字体大小
  const applyFontSize = () => {
    const fontSize = settings.value.preferences.fontSize
    const html = document.documentElement
    
    // 移除现有的字体大小类
    html.classList.remove('font-size-small', 'font-size-medium', 'font-size-large')
    
    // 添加新的字体大小类
    html.classList.add(`font-size-${fontSize}`)
  }

  // 应用语言设置（预留接口，等待i18n实现）
  const applyLanguage = () => {
    const language = settings.value.preferences.language
    const html = document.documentElement
    
    // 移除现有的语言类
    html.classList.remove('lang-zh', 'lang-en', 'lang-ja', 'lang-ko')
    
    // 添加新的语言类
    html.classList.add(`lang-${language}`)
    
    // 设置文档语言属性
    html.setAttribute('lang', language)
    
    // TODO: 等待i18n语言包系统实现后，替换为完整的语言切换逻辑
    console.log(`[设置] 语言设置已保存: ${language} (等待i18n实现)`)
  }

  // 更新设置
  const updateSettings = (updates) => {
    Object.keys(updates).forEach(key => {
      if (settings.value[key] !== undefined) {
        if (typeof updates[key] === 'object' && !Array.isArray(updates[key])) {
          settings.value[key] = { ...settings.value[key], ...updates[key] }
        } else {
          settings.value[key] = updates[key]
        }
      }
    })
    saveSettings()
  }

  // 更新个人资料
  const updateProfile = (profileUpdates) => {
    settings.value.profile = { ...settings.value.profile, ...profileUpdates }
    saveSettings()
  }

  // 更新AI设置
  const updateAISettings = (aiUpdates) => {
    settings.value.ai = { ...settings.value.ai, ...aiUpdates }
    saveSettings()
  }

  // 更新偏好设置
  const updatePreferences = (preferenceUpdates) => {
    settings.value.preferences = { ...settings.value.preferences, ...preferenceUpdates }
    saveSettings()
  }

  // 获取特定模型的API密钥
  const getApiKeyForModel = (model) => {
    return settings.value.ai.apiKeys[model] || settings.value.ai.apiKey
  }

  // 设置特定模型的API密钥
  const setApiKeyForModel = (model, apiKey) => {
    settings.value.ai.apiKeys[model] = apiKey
    saveSettings()
  }

  // 导出设置
  const exportSettings = () => {
    const dataStr = JSON.stringify(settings.value, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    
    const link = document.createElement('a')
    link.href = URL.createObjectURL(dataBlob)
    link.download = `chat-settings-${new Date().toISOString().split('T')[0]}.json`
    link.click()
  }

  // 导入设置
  const importSettings = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target.result)
          settings.value = { ...defaultSettings, ...importedSettings }
          saveSettings()
          resolve(true)
        } catch (error) {
          reject(new Error('导入失败：文件格式不正确'))
        }
      }
      reader.onerror = () => reject(new Error('读取文件失败'))
      reader.readAsText(file)
    })
  }

  // 验证设置
  const validateSettings = () => {
    const errors = []
    
    // 验证邮箱格式
    if (settings.value.profile.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(settings.value.profile.email)) {
      errors.push('邮箱格式不正确')
    }
    
    // 验证API密钥格式（如果存在）
    if (settings.value.ai.apiKey && settings.value.ai.apiKey.length < 10) {
      errors.push('API密钥格式不正确')
    }
    
    return errors
  }

  return {
    // 状态
    settings,
    
    // 计算属性
    currentTheme,
    currentLanguage,
    currentModel,
    currentApiKey,
    
    // 方法
    initSettings,
    saveSettings,
    resetSettings,
    updateSettings,
    updateProfile,
    updateAISettings,
    updatePreferences,
    getApiKeyForModel,
    setApiKeyForModel,
    exportSettings,
    importSettings,
    validateSettings,
    applyTheme
  }
})