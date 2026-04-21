<template>
  <div class="voice-controls">
    <div class="voice-buttons">
      <button 
        :class="['voice-btn', { recording: isRecording }]"
        @click="toggleRecording"
        :disabled="!isVoiceSupported || isSpeaking"
      >
        <el-icon v-if="!isRecording"><Microphone /></el-icon>
        <el-icon v-else><VideoPause /></el-icon>
        {{ isRecording ? '停止录音' : '开始说话' }}
      </button>
      
      <button 
        v-if="lastResponseText"
        :class="['voice-btn', 'play-btn', { speaking: isSpeaking }]"
        @click="toggleSpeakResponse"
        :disabled="isRecording"
      >
        <el-icon v-if="!isSpeaking"><Headset /></el-icon>
        <el-icon v-else><VideoPause /></el-icon>
        {{ isSpeaking ? '停止播放' : '播放回复' }}
      </button>
    </div>
    
    <!-- 语音波形显示 -->
    <div class="voice-visualizer" v-if="isRecording || isSpeaking">
      <div class="wave-bar" v-for="i in 20" :key="i" :style="waveStyle(i)"></div>
    </div>
    
    <!-- 语音转文字实时显示 -->
    <div class="speech-to-text" v-if="transcribedText && isRecording">
      <span>识别中: {{ transcribedText }}</span>
    </div>
    
    <!-- AI 回复文字显示 -->
    <div class="ai-response-text" v-if="lastResponseText && !isRecording">
      <span>AI回复: {{ lastResponseText }}</span>
    </div>
    
    <!-- 不支持语音提示 -->
    <div v-if="!isVoiceSupported" class="voice-not-supported">
      <el-alert 
        title="浏览器不支持语音功能" 
        type="warning" 
        :closable="false"
        show-icon
      >
        请使用Chrome、Edge等现代浏览器
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Microphone, VideoPause, Headset } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  hasAudioResponse: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['voice-data', 'transcription'])

const isRecording = ref(false)
const isSpeaking = ref(false)
const transcribedText = ref('')
const lastResponseText = ref('')
const isVoiceSupported = ref(false)

// 语音识别和语音合成实例
let recognition = null
let speechSynthesis = window.speechSynthesis
let currentUtterance = null

// 检查浏览器是否支持语音功能
const checkVoiceSupport = () => {
  const hasSpeechRecognition = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
  const hasSpeechSynthesis = 'speechSynthesis' in window
  isVoiceSupported.value = hasSpeechRecognition && hasSpeechSynthesis
  return isVoiceSupported.value
}

// 切换录音状态
const toggleRecording = async () => {
  if (!isVoiceSupported.value) {
    ElMessage.warning('您的浏览器不支持语音功能')
    return
  }
  
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

// 开始录音
const startRecording = async () => {
  // 停止正在播放的语音
  stopSpeaking()
  
  isRecording.value = true
  transcribedText.value = ''
  
  // 检查浏览器是否支持真实的语音识别
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    // 使用真实的Web Speech API
    await startRealSpeechRecognition()
  } else {
    // 降级到模拟语音识别
    startSimulatedRecognition()
  }
  
  ElMessage.success('开始录音，请说话...')
}

// 使用真实的Web Speech API进行语音识别
const startRealSpeechRecognition = () => {
  return new Promise((resolve) => {
    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognition = new SpeechRecognition()
      
      recognition.continuous = false
      recognition.interimResults = true
      recognition.lang = 'zh-CN'
      
      recognition.onstart = () => {
        console.log('语音识别已开始')
        transcribedText.value = '正在识别您的语音...'
        emit('voice-data', { type: 'recording-started' })
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
          transcribedText.value = finalTranscript
          emit('transcription', finalTranscript)
          // 用户说完，自动触发AI回复
          emit('voice-data', { 
            type: 'speech-completed', 
            text: finalTranscript 
          })
          // 停止录音
          stopRecording()
        } else if (interimTranscript) {
          transcribedText.value = interimTranscript
        }
      }
      
      recognition.onerror = (event) => {
        console.error('语音识别错误:', event.error)
        if (event.error !== 'no-speech' && event.error !== 'aborted') {
          emit('voice-data', { type: 'recording-error', error: event.error })
          ElMessage.error(`语音识别错误: ${event.error}`)
        }
        stopRecording()
      }
      
      recognition.onend = () => {
        console.log('语音识别已结束')
        emit('voice-data', { type: 'recording-ended' })
        if (isRecording.value) {
          // 如果仍在录音状态，说明是异常结束
          stopRecording()
        }
      }
      
      recognition.start()
      resolve()
    } catch (error) {
      console.error('语音识别初始化失败:', error)
      emit('voice-data', { type: 'recording-error', error: error.message })
      ElMessage.error('语音识别初始化失败')
      stopRecording()
      resolve()
    }
  })
}

// 模拟语音识别（兼容性降级）
const startSimulatedRecognition = () => {
  setTimeout(() => {
    transcribedText.value = '正在识别您的语音...'
    
    // 模拟识别结果
    setTimeout(() => {
      transcribedText.value = '你好，我想了解一下这个功能'
      emit('transcription', transcribedText.value)
      emit('voice-data', { 
        type: 'speech-completed', 
        text: transcribedText.value 
      })
      stopRecording()
    }, 2000)
  }, 500)
}

// 停止录音
const stopRecording = () => {
  isRecording.value = false
  
  // 停止语音识别
  if (recognition) {
    try {
      recognition.stop()
    } catch (error) {
      console.error('停止语音识别失败:', error)
    }
    recognition = null
  }
  
  ElMessage.info('录音已停止')
}

// ==================== 文字转语音功能 ====================

// 播放/停止 AI 回复语音
const toggleSpeakResponse = () => {
  if (isSpeaking.value) {
    stopSpeaking()
  } else {
    speakResponse(lastResponseText.value)
  }
}

// 文字转语音
const speakResponse = (text) => {
  if (!text) {
    ElMessage.warning('暂无回复内容可播放')
    return
  }
  
  if (!speechSynthesis) {
    ElMessage.warning('您的浏览器不支持语音播放')
    return
  }
  
  // 停止之前的语音
  stopSpeaking()
  
  // 创建新的语音实例
  currentUtterance = new SpeechSynthesisUtterance(text)
  currentUtterance.lang = 'zh-CN'
  currentUtterance.rate = 1.0  // 语速
  currentUtterance.pitch = 1.0  // 音调
  currentUtterance.volume = 1.0  // 音量
  
  // 选择中文语音
  const voices = speechSynthesis.getVoices()
  const chineseVoice = voices.find(voice => 
    voice.lang.includes('zh') || voice.lang.includes('cmn')
  )
  if (chineseVoice) {
    currentUtterance.voice = chineseVoice
  }
  
  // 开始播放
  currentUtterance.onstart = () => {
    isSpeaking.value = true
    console.log('开始播放语音回复')
  }
  
  // 播放结束
  currentUtterance.onend = () => {
    isSpeaking.value = false
    currentUtterance = null
    console.log('语音回复播放结束')
  }
  
  // 播放错误
  currentUtterance.onerror = (event) => {
    console.error('语音播放错误:', event.error)
    isSpeaking.value = false
    currentUtterance = null
    if (event.error !== 'canceled' && event.error !== 'interrupted') {
      ElMessage.error('语音播放失败')
    }
  }
  
  speechSynthesis.speak(currentUtterance)
}

// 停止语音播放
const stopSpeaking = () => {
  if (speechSynthesis) {
    speechSynthesis.cancel()
  }
  isSpeaking.value = false
  currentUtterance = null
}

// 设置 AI 回复文本（由父组件调用）
const setAIResponse = (text) => {
  lastResponseText.value = text
  // 自动播放 AI 回复
  speakResponse(text)
}

// 波形动画样式
const waveStyle = (index) => {
  const height = Math.random() * 30 + 10
  const delay = index * 0.1
  return {
    height: `${height}px`,
    animationDelay: `${delay}s`
  }
}

// 组件挂载时检查语音支持
onMounted(() => {
  checkVoiceSupport()
  
  // 预加载语音列表
  if (speechSynthesis) {
    speechSynthesis.getVoices()
  }
})

// 组件卸载时清理
onUnmounted(() => {
  stopRecording()
  stopSpeaking()
})

// 暴露方法给父组件
defineExpose({
  stopRecordingExternal: stopRecording,
  setAIResponse,
  stopSpeaking
})
</script>

<style scoped>
.voice-controls {
  padding: 1rem;
  background: #ffffff;
  border-top: 1px solid #ebeef5;
}

.voice-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.voice-btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 50px;
  background: #667eea;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
}

.voice-btn:hover:not(:disabled) {
  background: #5a6fd8;
  transform: translateY(-1px);
}

.voice-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
  transform: none;
}

.voice-btn.recording {
  background: #f56c6c;
  animation: recording-pulse 1.5s infinite;
}

.voice-btn.play-btn {
  background: #10b981;
}

.voice-btn.play-btn:hover:not(:disabled) {
  background: #059669;
}

.voice-btn.speaking {
  background: #8b5cf6;
  animation: speaking-pulse 1s infinite;
}

@keyframes recording-pulse {
  0% { 
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.7);
  }
  70% { 
    box-shadow: 0 0 0 15px rgba(245, 108, 108, 0);
  }
  100% { 
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0);
  }
}

@keyframes speaking-pulse {
  0% { 
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.7);
  }
  50% { 
    box-shadow: 0 0 0 10px rgba(139, 92, 246, 0.3);
  }
  100% { 
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0);
  }
}

.voice-visualizer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  height: 50px;
  margin-bottom: 1rem;
}

.wave-bar {
  width: 4px;
  background: linear-gradient(to top, #667eea, #764ba2);
  border-radius: 2px;
  animation: wave-animation 1s ease-in-out infinite;
}

@keyframes wave-animation {
  0%, 100% {
    transform: scaleY(0.5);
  }
  50% {
    transform: scaleY(1);
  }
}

.speech-to-text,
.ai-response-text {
  text-align: center;
  padding: 0.75rem;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.speech-to-text span {
  color: #667eea;
  font-size: 0.9rem;
}

.ai-response-text span {
  color: #10b981;
  font-size: 0.9rem;
}

.voice-not-supported {
  margin-top: 1rem;
}

/* 深色模式适配 */
:global(.dark) .voice-controls {
  background: #1e1e28;
  border-color: #333;
}

:global(.dark) .speech-to-text,
:global(.dark) .ai-response-text {
  background: #2a2a3a;
}
</style>
