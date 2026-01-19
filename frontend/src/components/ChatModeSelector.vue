<template>
  <div class="chat-mode-selector">
    <div class="mode-tabs">
      <button 
        :class="['mode-tab', { active: currentMode === 'text' }]"
        @click="switchMode('text')"
      >
        <el-icon><ChatLineRound /></el-icon>
        文字聊天
      </button>
      <button 
        :class="['mode-tab', { active: currentMode === 'voice' }]"
        @click="switchMode('voice')"
      >
        <el-icon><Microphone /></el-icon>
        语音通话
      </button>
      <button 
        :class="['mode-tab', { active: currentMode === 'video' }]"
        @click="switchMode('video')"
      >
        <el-icon><VideoCamera /></el-icon>
        视频通话
      </button>
    </div>
    
    <!-- 模式状态指示器 -->
    <div class="mode-status">
      <span v-if="currentMode === 'text'" class="status-text">📝 文字聊天模式</span>
      <span v-if="currentMode === 'voice'" class="status-voice">
        🎤 语音通话模式
        <span class="recording-indicator" v-if="isRecording">● 录音中</span>
      </span>
      <span v-if="currentMode === 'video'" class="status-video">📹 视频通话模式</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ChatLineRound, Microphone, VideoCamera } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'text'
  }
})

const emit = defineEmits(['update:modelValue', 'modeChange'])

const currentMode = ref(props.modelValue)
const isRecording = ref(false)

// 切换模式
const switchMode = (mode) => {
  if (currentMode.value === mode) return
  
  currentMode.value = mode
  emit('update:modelValue', mode)
  emit('modeChange', mode)
  
  // 重置录音状态
  if (mode !== 'voice') {
    isRecording.value = false
  }
}

// 监听外部模式变化
watch(() => props.modelValue, (newMode) => {
  if (currentMode.value !== newMode) {
    currentMode.value = newMode
  }
})

// 暴露方法给父组件
const setRecording = (recording) => {
  isRecording.value = recording
}

defineExpose({
  setRecording
})
</script>

<style scoped>
.chat-mode-selector {
  background: rgba(255, 255, 255, 0.95);
  padding: 1rem;
  border-bottom: 1px solid #ebeef5;
  backdrop-filter: blur(10px);
}

.mode-tabs {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.mode-tab {
  padding: 0.75rem 1.5rem;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.mode-tab:hover {
  border-color: #667eea;
  transform: translateY(-1px);
}

.mode-tab.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.mode-status {
  text-align: center;
  font-size: 0.85rem;
  color: #606266;
  font-weight: 500;
}

.status-voice .recording-indicator {
  color: #f56c6c;
  animation: pulse 1s infinite;
  margin-left: 0.5rem;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .mode-tabs {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .mode-tab {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
}
</style>