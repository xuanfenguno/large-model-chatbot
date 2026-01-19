<template>
  <div class="voice-call-container" v-if="isCallActive || isIncomingCall">
    <!-- 通话中界面 -->
    <div v-if="isCallActive" class="call-active">
      <div class="call-header">
        <h3>{{ callStatus }}</h3>
        <div class="call-timer">{{ formatTime(callDuration) }}</div>
      </div>
      
      <div class="call-content">
        <!-- 音频可视化 -->
        <div class="audio-visualizer">
          <div class="local-audio">
            <div class="audio-label">我</div>
            <AudioVisualizer :stream="localStream" :is-local="true" />
          </div>
          <div class="remote-audio">
            <div class="audio-label">对方</div>
            <AudioVisualizer :stream="remoteStream" :is-local="false" />
          </div>
        </div>
        
        <!-- 通话控制 -->
        <CallControls 
          :is-muted="isMuted"
          :is-speaker="isSpeaker"
          @toggle-mute="toggleMute"
          @toggle-speaker="toggleSpeaker"
          @end-call="endCall"
        />
      </div>
    </div>
    
    <!-- 来电界面 -->
    <div v-else-if="isIncomingCall" class="incoming-call">
      <div class="call-alert">
        <div class="call-icon">
          <el-icon><Phone /></el-icon>
        </div>
        <div class="call-info">
          <h3>来电</h3>
          <p>语音通话请求</p>
        </div>
        <div class="call-actions">
          <el-button type="success" size="large" @click="answerCall">
            <el-icon><VideoPlay /></el-icon>
            接听
          </el-button>
          <el-button type="danger" size="large" @click="rejectCall">
            <el-icon><Close /></el-icon>
            拒绝
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Phone, VideoPlay, Close } from '@element-plus/icons-vue'
import { VoiceCallManager, checkWebRTCSupport } from '@/utils/webrtc'
import AudioVisualizer from './AudioVisualizer.vue'
import CallControls from './CallControls.vue'

const props = defineProps({
  socket: {
    type: Object,
    required: true
  },
  targetUserId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['call-ended'])

// 状态管理
const isCallActive = ref(false)
const isIncomingCall = ref(false)
const isMuted = ref(false)
const isSpeaker = ref(false)
const callDuration = ref(0)
const callStatus = ref('通话中')
const localStream = ref(null)
const remoteStream = ref(null)

// WebRTC管理器
const callManager = ref(null)
const callTimer = ref(null)
const currentCallId = ref(null)

// 计算属性
const isWebRTCSupported = computed(() => checkWebRTCSupport())

// 格式化通话时间
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 初始化通话管理器
const initializeCallManager = () => {
  if (!isWebRTCSupported.value) {
    ElMessage.warning('您的浏览器不支持WebRTC功能')
    return false
  }

  callManager.value = new VoiceCallManager()
  
  // 设置回调函数
  callManager.value.onRemoteStreamAdded = (stream) => {
    remoteStream.value = stream
  }
  
  callManager.value.onCallConnected = () => {
    isCallActive.value = true
    isIncomingCall.value = false
    startCallTimer()
    ElMessage.success('通话已连接')
  }
  
  callManager.value.onCallDisconnected = () => {
    ElMessage.warning('通话已断开')
    endCall()
  }
  
  callManager.value.onCallEnded = () => {
    endCall()
  }
  
  return true
}

// 发起通话
const initiateCall = async () => {
  if (!initializeCallManager()) return
  
  currentCallId.value = generateCallId()
  
  try {
    const success = await callManager.value.initialize(
      props.socket, 
      currentCallId.value, 
      true
    )
    
    if (success) {
      localStream.value = callManager.value.getLocalStream()
      
      // 发送通话请求
      props.socket.emit('initiate-call', {
        callId: currentCallId.value,
        targetUserId: props.targetUserId
      })
      
      // 创建offer
      await callManager.value.createOffer()
      
      callStatus.value = '等待接听...'
    }
  } catch (error) {
    console.error('发起通话失败:', error)
    ElMessage.error('发起通话失败')
  }
}

// 接听来电
const answerCall = async () => {
  if (!initializeCallManager()) return
  
  try {
    const success = await callManager.value.initialize(
      props.socket, 
      currentCallId.value, 
      false
    )
    
    if (success) {
      localStream.value = callManager.value.getLocalStream()
      
      // 发送接听响应
      props.socket.emit('answer-call', {
        callId: currentCallId.value
      })
      
      isIncomingCall.value = false
      callStatus.value = '通话中'
    }
  } catch (error) {
    console.error('接听通话失败:', error)
    ElMessage.error('接听通话失败')
  }
}

// 拒绝来电
const rejectCall = () => {
  props.socket.emit('reject-call', {
    callId: currentCallId.value
  })
  
  isIncomingCall.value = false
  currentCallId.value = null
}

// 结束通话
const endCall = () => {
  if (callManager.value) {
    callManager.value.endCall()
  }
  
  // 清理状态
  isCallActive.value = false
  isIncomingCall.value = false
  stopCallTimer()
  callDuration.value = 0
  localStream.value = null
  remoteStream.value = null
  currentCallId.value = null
  
  emit('call-ended')
}

// 静音切换
const toggleMute = () => {
  if (callManager.value) {
    isMuted.value = callManager.value.toggleMute()
  }
}

// 扬声器切换
const toggleSpeaker = () => {
  isSpeaker.value = !isSpeaker.value
  // 这里可以添加扬声器控制逻辑
}

// 通话计时器
const startCallTimer = () => {
  callTimer.value = setInterval(() => {
    callDuration.value++
  }, 1000)
}

const stopCallTimer = () => {
  if (callTimer.value) {
    clearInterval(callTimer.value)
    callTimer.value = null
  }
}

// 生成通话ID
const generateCallId = () => {
  return `call_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 监听Socket事件
const setupSocketListeners = () => {
  // 来电通知
  props.socket.on('incoming-call', (data) => {
    currentCallId.value = data.callId
    isIncomingCall.value = true
  })
  
  // 对方接听
  props.socket.on('call-accepted', (data) => {
    callStatus.value = '通话中'
  })
  
  // 对方拒绝
  props.socket.on('call-rejected', (data) => {
    ElMessage.info('对方拒绝了通话')
    endCall()
  })
  
  // 对方挂断
  props.socket.on('call-ended', (data) => {
    ElMessage.info('对方已挂断')
    endCall()
  })
  
  // WebRTC信令
  props.socket.on('offer', async (data) => {
    if (callManager.value) {
      await callManager.value.handleOffer(data.offer)
    }
  })
  
  props.socket.on('answer', async (data) => {
    if (callManager.value) {
      await callManager.value.handleAnswer(data.answer)
    }
  })
  
  props.socket.on('ice-candidate', async (data) => {
    if (callManager.value) {
      await callManager.value.handleIceCandidate(data.candidate)
    }
  })
}

// 生命周期
onMounted(() => {
  setupSocketListeners()
})

onUnmounted(() => {
  endCall()
  
  // 移除Socket监听器
  if (props.socket) {
    props.socket.off('incoming-call')
    props.socket.off('call-accepted')
    props.socket.off('call-rejected')
    props.socket.off('call-ended')
    props.socket.off('offer')
    props.socket.off('answer')
    props.socket.off('ice-candidate')
  }
})

// 暴露方法给父组件
defineExpose({
  initiateCall,
  endCall
})
</script>

<style scoped>
.voice-call-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.call-active {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  min-width: 400px;
  max-width: 500px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.call-header {
  text-align: center;
  margin-bottom: 2rem;
}

.call-header h3 {
  margin: 0 0 0.5rem 0;
  color: #303133;
  font-size: 1.2rem;
}

.call-timer {
  font-size: 1.5rem;
  font-weight: 600;
  color: #667eea;
}

.audio-visualizer {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  justify-content: center;
}

.local-audio, .remote-audio {
  text-align: center;
}

.audio-label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #606266;
}

.incoming-call {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  min-width: 300px;
}

.call-icon {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.call-info h3 {
  margin: 0 0 0.5rem 0;
  color: #303133;
}

.call-info p {
  margin: 0 0 1.5rem 0;
  color: #909399;
}

.call-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}
</style>