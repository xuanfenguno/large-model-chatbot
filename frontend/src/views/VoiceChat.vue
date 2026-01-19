<template>
  <div class="voice-chat-container">
    <!-- 头部导航 -->
    <header class="voice-header">
      <el-button type="primary" @click="goBack" icon="el-icon-arrow-left">
        返回文字聊天
      </el-button>
      <div class="header-title">
        <h1>语音助手</h1>
        <p>与AI智能体实时语音对话</p>
      </div>
      <div class="header-status">
        <el-tag :type="connectionStatus.type">
          {{ connectionStatus.text }}
        </el-tag>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="voice-main">
      <!-- AI助手2D形象 -->
      <div class="ai-assistant">
        <div class="assistant-avatar" :class="{ speaking: isAISpeaking, listening: isUserSpeaking }">
          <!-- 冰墩墩风格的AI助手形象 -->
          <div class="assistant-body">
            <div class="assistant-face">
              <div class="assistant-eyes">
                <div class="eye left-eye" :class="{ blink: isBlinking }"></div>
                <div class="eye right-eye" :class="{ blink: isBlinking }"></div>
              </div>
              <div class="assistant-mouth" :class="{ speaking: isAISpeaking }"></div>
            </div>
          </div>
        </div>
        
        <!-- AI助手状态显示 -->
        <div class="assistant-status">
          <div class="status-text" :class="{ thinking: isAIThinking }">
            {{ statusText }}
          </div>
          <div class="thinking-dots" v-if="isAIThinking">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      <!-- 对话记录 -->
      <div class="conversation-log">
        <div 
          v-for="(message, index) in conversationHistory" 
          :key="index"
          :class="['message', message.type]"
        >
          <div class="message-avatar">
            <el-icon v-if="message.type === 'user'"><User /></el-icon>
            <div v-else class="ai-avatar">AI</div>
          </div>
          <div class="message-content">
            <div class="message-text">{{ message.text }}</div>
            <div class="message-time">{{ message.time }}</div>
          </div>
        </div>
      </div>
    </main>

    <!-- 语音控制区域 -->
    <footer class="voice-controls">
      <div class="controls-container">
        <!-- 语音输入按钮 -->
        <button 
          :class="['voice-input-btn', { recording: isRecording, listening: isUserSpeaking }]"
          @click="toggleVoiceInput"
          :disabled="!isVoiceSupported || isAISpeaking"
        >
          <el-icon v-if="!isRecording"><Microphone /></el-icon>
          <el-icon v-else><VideoPause /></el-icon>
          <span>{{ voiceButtonText }}</span>
        </button>

        <!-- 语音波形可视化 -->
        <div class="voice-visualizer" v-if="isRecording || isAISpeaking">
          <div 
            v-for="i in 20" 
            :key="i" 
            class="wave-bar"
            :style="waveStyle(i)"
          ></div>
        </div>

        <!-- 语音设置 -->
        <div class="voice-settings">
          <el-tooltip content="调整语音音量">
            <el-slider
              v-model="voiceVolume"
              :min="0"
              :max="100"
              :step="10"
              show-stops
              size="small"
              style="width: 100px;"
            />
          </el-tooltip>
          
          <el-tooltip content="语音识别语言">
            <el-select v-model="speechLanguage" size="small" style="width: 120px;">
              <el-option label="中文" value="zh-CN"></el-option>
              <el-option label="English" value="en-US"></el-option>
              <el-option label="日本語" value="ja-JP"></el-option>
            </el-select>
          </el-tooltip>
        </div>
      </div>

      <!-- 语音转文字实时显示 -->
      <div class="speech-preview" v-if="currentSpeechText">
        <div class="preview-label">正在识别:</div>
        <div class="preview-text">{{ currentSpeechText }}</div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Microphone, VideoPause, User } from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const isRecording = ref(false)
const isAISpeaking = ref(false)
const isAIThinking = ref(false)
const isUserSpeaking = ref(false)
const isBlinking = ref(false)
const currentSpeechText = ref('')
const voiceVolume = ref(80)
const speechLanguage = ref('zh-CN')

// 对话历史
const conversationHistory = ref([])

// 连接状态
const connectionStatus = computed(() => {
  if (!isVoiceSupported.value) {
    return { type: 'danger', text: '不支持语音' }
  }
  if (isRecording.value) {
    return { type: 'warning', text: '录音中' }
  }
  if (isAISpeaking.value) {
    return { type: 'success', text: 'AI回复中' }
  }
  return { type: 'info', text: '准备就绪' }
})

// 状态文本
const statusText = computed(() => {
  if (isAIThinking.value) return '思考中...'
  if (isAISpeaking.value) return '正在回复...'
  if (isRecording.value) return '聆听中...'
  return '等待语音输入'
})

// 语音按钮文本
const voiceButtonText = computed(() => {
  if (isRecording.value) return '停止说话'
  if (isAISpeaking.value) return 'AI回复中'
  return '开始说话'
})

// 检查语音支持
const isVoiceSupported = computed(() => {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
})

// 波形样式
const waveStyle = (index) => {
  const baseHeight = 4
  const amplitude = isRecording.value || isAISpeaking.value ? Math.random() * 20 + 10 : baseHeight
  return {
    height: `${baseHeight + amplitude}px`,
    animationDelay: `${index * 0.1}s`
  }
}

// 语音识别实例
let recognition = null

// 初始化语音识别
const initSpeechRecognition = () => {
  if (!isVoiceSupported.value) {
    ElMessage.warning('您的浏览器不支持语音识别功能')
    return
  }

  try {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition = new SpeechRecognition()
    
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = speechLanguage.value

    recognition.onstart = () => {
      isUserSpeaking.value = true
      ElMessage.success('语音识别已开始，请说话...')
    }

    recognition.onresult = (event) => {
      let finalTranscript = ''
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += transcript
        } else {
          interimTranscript += transcript
        }
      }

      if (finalTranscript) {
        currentSpeechText.value = finalTranscript
        // 用户说完，开始AI处理
        handleUserSpeech(finalTranscript)
      } else if (interimTranscript) {
        currentSpeechText.value = interimTranscript
      }
    }

    recognition.onerror = (event) => {
      console.error('语音识别错误:', event.error)
      ElMessage.error(`语音识别错误: ${event.error}`)
      stopRecording()
    }

    recognition.onend = () => {
      if (isRecording.value) {
        // 如果仍在录音状态，重新开始识别
        recognition.start()
      }
    }

  } catch (error) {
    console.error('语音识别初始化失败:', error)
    ElMessage.error('语音识别初始化失败')
  }
}

// 切换语音输入
const toggleVoiceInput = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

// 开始录音
const startRecording = () => {
  if (!isVoiceSupported.value) {
    ElMessage.warning('浏览器不支持语音识别')
    return
  }

  isRecording.value = true
  currentSpeechText.value = ''
  
  if (recognition) {
    recognition.start()
  } else {
    initSpeechRecognition()
  }
}

// 停止录音
const stopRecording = () => {
  isRecording.value = false
  isUserSpeaking.value = false
  
  if (recognition) {
    recognition.stop()
  }
}

// 处理用户语音
const handleUserSpeech = async (text) => {
  // 添加到对话历史
  const userMessage = {
    type: 'user',
    text: text,
    time: new Date().toLocaleTimeString('zh-CN', { hour12: false })
  }
  conversationHistory.value.push(userMessage)

  // AI开始思考
  isAIThinking.value = true
  
  try {
    // 模拟AI处理时间（2-5秒）
    const thinkingTime = Math.random() * 3000 + 2000
    await new Promise(resolve => setTimeout(resolve, thinkingTime))
    
    // AI生成回复
    const aiResponse = await generateAIResponse(text)
    
    // AI开始说话
    isAIThinking.value = false
    isAISpeaking.value = true
    
    // 播放AI语音回复
    await speakText(aiResponse)
    
    // AI说完
    isAISpeaking.value = false
    
  } catch (error) {
    console.error('AI处理错误:', error)
    ElMessage.error('AI处理失败')
    isAIThinking.value = false
  }
}

// 生成AI回复
const generateAIResponse = async (userText) => {
  // 这里应该调用实际的AI API
  // 暂时使用模拟回复
  const responses = [
    `我理解您说的是："${userText}"。这是一个很有趣的话题！`,
    `关于"${userText}"，我可以为您提供更多信息。`,
    `您提到的"${userText}"让我想到了相关的知识。`,
    `对于"${userText}"，我的看法是...`,
    `感谢您分享"${userText}"，让我来帮您分析一下。`
  ]
  
  return responses[Math.floor(Math.random() * responses.length)]
}

// 文字转语音
const speakText = (text) => {
  return new Promise((resolve) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = speechLanguage.value
      utterance.volume = voiceVolume.value / 100
      utterance.rate = 1.0
      utterance.pitch = 1.0

      utterance.onstart = () => {
        console.log('开始播放语音回复')
      }

      utterance.onend = () => {
        console.log('语音播放结束')
        // 添加到对话历史
        const aiMessage = {
          type: 'ai',
          text: text,
          time: new Date().toLocaleTimeString('zh-CN', { hour12: false })
        }
        conversationHistory.value.push(aiMessage)
        resolve()
      }

      utterance.onerror = (event) => {
        console.error('语音合成错误:', event)
        resolve()
      }

      speechSynthesis.speak(utterance)
    } else {
      // 如果不支持语音合成，直接显示文字
      const aiMessage = {
        type: 'ai',
        text: text,
        time: new Date().toLocaleTimeString('zh-CN', { hour12: false })
      }
      conversationHistory.value.push(aiMessage)
      resolve()
    }
  })
}

// 返回文字聊天
const goBack = () => {
  // 停止所有语音活动
  if (isRecording.value) stopRecording()
  if (isAISpeaking.value) speechSynthesis.cancel()
  
  router.push('/chat')
}

// 眨眼动画
let blinkInterval = null
const startBlinkAnimation = () => {
  blinkInterval = setInterval(() => {
    isBlinking.value = true
    setTimeout(() => {
      isBlinking.value = false
    }, 200)
  }, 3000 + Math.random() * 2000)
}

// 组件挂载
onMounted(() => {
  startBlinkAnimation()
  ElMessage.info('欢迎使用语音助手！点击"开始说话"按钮开始对话')
})

// 组件卸载
onUnmounted(() => {
  if (blinkInterval) clearInterval(blinkInterval)
  if (recognition) recognition.stop()
  speechSynthesis.cancel()
})
</script>

<style scoped>
.voice-chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.voice-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.header-title {
  text-align: center;
}

.header-title h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-title p {
  margin: 5px 0 0 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

.voice-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  gap: 30px;
}

.ai-assistant {
  text-align: center;
}

.assistant-avatar {
  width: 200px;
  height: 200px;
  margin: 0 auto 20px;
  position: relative;
  transition: all 0.3s ease;
}

.assistant-avatar.speaking {
  transform: scale(1.05);
  animation: pulse 1s infinite;
}

.assistant-avatar.listening {
  animation: listening 2s infinite;
}

.assistant-body {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.assistant-face {
  position: relative;
  width: 80%;
  height: 80%;
}

.assistant-eyes {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.eye {
  width: 30px;
  height: 30px;
  background: white;
  border-radius: 50%;
  position: relative;
  transition: all 0.3s ease;
}

.eye.blink {
  height: 5px;
}

.eye::after {
  content: '';
  position: absolute;
  width: 15px;
  height: 15px;
  background: #333;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.assistant-mouth {
  width: 40px;
  height: 10px;
  background: #ff6b6b;
  border-radius: 5px;
  margin: 0 auto;
  transition: all 0.3s ease;
}

.assistant-mouth.speaking {
  animation: mouth-speak 0.5s infinite alternate;
}

.assistant-status {
  margin-top: 20px;
}

.status-text {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 10px;
}

.status-text.thinking {
  color: #ffd93d;
}

.thinking-dots {
  display: flex;
  justify-content: center;
  gap: 5px;
}

.thinking-dots span {
  width: 8px;
  height: 8px;
  background: #ffd93d;
  border-radius: 50%;
  animation: thinking 1.4s infinite ease-in-out;
}

.thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots span:nth-child(2) { animation-delay: -0.16s; }

.conversation-log {
  width: 100%;
  max-width: 600px;
  max-height: 200px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 15px;
  backdrop-filter: blur(10px);
}

.message {
  display: flex;
  margin-bottom: 15px;
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 10px;
}

.ai-avatar {
  width: 30px;
  height: 30px;
  background: #4facfe;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.8rem;
}

.message-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 10px 15px;
  max-width: 70%;
}

.message.user .message-content {
  background: rgba(76, 175, 80, 0.3);
}

.message-text {
  font-size: 0.95rem;
  line-height: 1.4;
}

.message-time {
  font-size: 0.7rem;
  opacity: 0.7;
  margin-top: 5px;
}

.voice-controls {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 20px;
}

.controls-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 15px;
}

.voice-input-btn {
  width: 120px;
  height: 120px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(45deg, #ff6b6b, #ffd93d);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.voice-input-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.voice-input-btn.recording {
  background: linear-gradient(45deg, #ff416c, #ff4b2b);
  animation: pulse 1s infinite;
}

.voice-input-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.voice-visualizer {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 30px;
}

.wave-bar {
  width: 3px;
  background: #4facfe;
  border-radius: 2px;
  animation: wave 1s infinite ease-in-out;
}

.voice-settings {
  display: flex;
  align-items: center;
  gap: 15px;
}

.speech-preview {
  text-align: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px;
  margin-top: 10px;
}

.preview-label {
  font-size: 0.8rem;
  opacity: 0.8;
  margin-bottom: 5px;
}

.preview-text {
  font-size: 1rem;
  font-weight: 500;
}

/* 动画定义 */
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes listening {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

@keyframes mouth-speak {
  0% { height: 5px; }
  100% { height: 15px; }
}

@keyframes thinking {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

@keyframes wave {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(2); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .voice-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .controls-container {
    flex-direction: column;
    gap: 15px;
  }
  
  .voice-input-btn {
    width: 100px;
    height: 100px;
  }
  
  .assistant-avatar {
    width: 150px;
    height: 150px;
  }
}
</style>