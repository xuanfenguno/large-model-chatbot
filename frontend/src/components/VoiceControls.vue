<template>
  <div class="voice-controls">
    <div class="voice-buttons">
      <button 
        :class="['voice-btn', { recording: isRecording }]"
        @click="toggleRecording"
        :disabled="!isVoiceSupported"
      >
        <el-icon v-if="!isRecording"><Microphone /></el-icon>
        <el-icon v-else><VideoPause /></el-icon>
        {{ isRecording ? '停止录音' : '开始说话' }}
      </button>
      
      <button 
        class="voice-btn" 
        @click="playLastResponse"
        :disabled="!hasAudioResponse"
      >
        <el-icon><Headset /></el-icon>
        播放回复
      </button>
    </div>
    
    <!-- 语音波形显示 -->
    <div class="voice-visualizer" v-if="isRecording">
      <div class="wave-bar" v-for="i in 20" :key="i" :style="waveStyle(i)"></div>
    </div>
    
    <!-- 语音转文字实时显示 -->
    <div class="speech-to-text" v-if="transcribedText">
      <span>识别中: {{ transcribedText }}</span>
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
import { ref, onMounted, computed } from 'vue'
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
const transcribedText = ref('')
const isVoiceSupported = ref(false)

// 检查浏览器是否支持语音识别
const checkVoiceSupport = () => {
  isVoiceSupported.value = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
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
const startRecording = () => {
  isRecording.value = true
  transcribedText.value = ''
  
  // 模拟语音识别过程（实际项目中需要集成Web Speech API）
  setTimeout(() => {
    transcribedText.value = '正在识别您的语音...'
    
    // 模拟识别结果
    setTimeout(() => {
      transcribedText.value = '你好，我想了解一下这个功能'
      emit('transcription', transcribedText.value)
    }, 2000)
  }, 500)
  
  ElMessage.success('开始录音，请说话...')
}

// 停止录音
const stopRecording = () => {
  isRecording.value = false
  
  if (transcribedText.value) {
    // 发送识别结果
    emit('voice-data', {
      text: transcribedText.value,
      audio: null, // 实际项目中这里应该是录音数据
      duration: 3.5
    })
  }
  
  ElMessage.info('录音已停止')
}

// 播放回复
const playLastResponse = () => {
  if (!props.hasAudioResponse) {
    ElMessage.warning('暂无语音回复可播放')
    return
  }
  
  // 模拟播放语音回复
  ElMessage.success('播放语音回复...')
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
})

// 暴露方法给父组件
const stopRecordingExternal = () => {
  if (isRecording.value) {
    stopRecording()
  }
}

defineExpose({
  stopRecordingExternal
})
</script>

<style scoped>
.voice-controls {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.95);
  border-top: 1px solid #ebeef5;
  backdrop-filter: blur(10px);
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
  animation: recording-pulse 1s infinite;
}

@keyframes recording-pulse {
  0% { 
    background: #f56c6c;
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.7);
  }
  70% { 
    box-shadow: 0 0 0 10px rgba(245, 108, 108, 0);
  }
  100% { 
    background: #f56c6c;
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0);
  }
}

.voice-visualizer {
  display: flex;
  justify-content: center;
  gap: 2px;
  margin: 1rem 0;
  height: 40px;
  align-items: flex-end;
}

.wave-bar {
  width: 3px;
  background: #667eea;
  border-radius: 2px;
  animation: wave 1s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% { 
    transform: scaleY(0.5);
    opacity: 0.7;
  }
  50% { 
    transform: scaleY(1);
    opacity: 1;
  }
}

.speech-to-text {
  text-align: center;
  padding: 0.5rem;
  background: #f0f9ff;
  border-radius: 4px;
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.voice-not-supported {
  margin-top: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .voice-buttons {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .voice-btn {
    padding: 0.75rem 1.5rem;
    font-size: 0.85rem;
  }
}
</style>