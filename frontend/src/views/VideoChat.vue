<template>
  <div class="video-chat-container">
    <!-- 头部导航 -->
    <header class="video-header">
      <el-button type="primary" @click="goBack" icon="el-icon-arrow-left">
        返回文字聊天
      </el-button>
      <div class="header-title">
        <h1>视频通话</h1>
        <p>与AI智能体进行视频交流</p>
      </div>
      <div class="header-status">
        <el-tag :type="connectionStatus.type">
          {{ connectionStatus.text }}
        </el-tag>
        <el-tooltip content="通话时长">
          <span class="call-duration">{{ callDuration }}</span>
        </el-tooltip>
      </div>
    </header>

    <!-- 主视频区域 -->
    <main class="video-main">
      <!-- 视频布局 -->
      <div class="video-layout" :class="{ 'ai-speaking': isAISpeaking, 'user-speaking': isUserSpeaking }">
        <!-- 本地视频 -->
        <div class="video-panel local-video">
          <div class="video-header">
            <span class="video-title">我的视频</span>
            <div class="video-controls">
              <el-tooltip :content="isVideoEnabled ? '关闭摄像头' : '开启摄像头'">
                <el-button 
                  :type="isVideoEnabled ? 'success' : 'danger'" 
                  size="small" 
                  circle
                  @click="toggleVideo"
                >
                  <el-icon><VideoCamera /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip :content="isAudioEnabled ? '静音' : '取消静音'">
                <el-button 
                  :type="isAudioEnabled ? 'success' : 'danger'" 
                  size="small" 
                  circle
                  @click="toggleAudio"
                >
                  <el-icon><Microphone /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
          
          <div class="video-content">
            <video 
              ref="localVideo" 
              :muted="true" 
              autoplay 
              playsinline
              class="video-element"
              :class="{ 'video-disabled': !isVideoEnabled }"
            ></video>
            
            <!-- 视频禁用时的占位符 -->
            <div v-if="!isVideoEnabled" class="video-placeholder">
              <el-icon><User /></el-icon>
              <span>摄像头已关闭</span>
            </div>
            
            <!-- 音频可视化 -->
            <AudioVisualizer 
              v-if="localStream && isAudioEnabled"
              :stream="localStream"
              :isLocal="true"
              class="audio-visualizer"
            />
          </div>
        </div>

        <!-- AI视频 -->
        <div class="video-panel ai-video">
          <div class="video-header">
            <span class="video-title">AI助手</span>
            <div class="ai-status">
              <el-tag :type="aiStatus.type" size="small">
                {{ aiStatus.text }}
              </el-tag>
            </div>
          </div>
          
          <div class="video-content">
            <!-- AI虚拟形象 -->
            <div class="ai-avatar" :class="{ speaking: isAISpeaking, listening: isUserSpeaking }">
              <div class="ai-face">
                <div class="ai-eyes">
                  <div class="eye left-eye" :class="{ blink: isBlinking }"></div>
                  <div class="eye right-eye" :class="{ blink: isBlinking }"></div>
                </div>
                <div class="ai-mouth" :class="{ speaking: isAISpeaking }"></div>
              </div>
            </div>
            
            <!-- AI状态显示 -->
            <div class="ai-status-display">
              <div class="status-text">{{ aiStatusText }}</div>
              <div class="thinking-dots" v-if="isAIThinking">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
            
            <!-- AI音频可视化 -->
            <AudioVisualizer 
              v-if="isAISpeaking"
              :stream="aiAudioStream"
              :isLocal="false"
              class="audio-visualizer ai-audio"
            />
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
            <div v-else class="ai-avatar-small">AI</div>
          </div>
          <div class="message-content">
            <div class="message-text">{{ message.text }}</div>
            <div class="message-time">{{ message.time }}</div>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部控制区域 -->
    <footer class="video-controls">
      <div class="controls-container">
        <!-- 主控制按钮 -->
        <div class="main-controls">
          <el-button 
            v-if="!isCallActive"
            type="success" 
            size="large"
            @click="startVideoCall"
            :loading="isStartingCall"
            class="call-btn"
          >
            <el-icon><VideoCamera /></el-icon>
            开始视频通话
          </el-button>
          
          <el-button 
            v-else
            type="danger" 
            size="large"
            @click="endVideoCall"
            class="end-call-btn"
          >
            <el-icon><Phone /></el-icon>
            结束通话
          </el-button>
        </div>

        <!-- 辅助控制 -->
        <div class="secondary-controls" v-if="isCallActive">
          <el-tooltip content="切换摄像头">
            <el-button 
              type="info" 
              size="small" 
              circle
              @click="switchCamera"
            >
              <el-icon><Switch /></el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip content="屏幕共享">
            <el-button 
              type="warning" 
              size="small" 
              circle
              @click="toggleScreenShare"
              :disabled="isScreenSharing"
            >
              <el-icon><Monitor /></el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip content="录制通话">
            <el-button 
              type="success" 
              size="small" 
              circle
              @click="toggleRecording"
              :class="{ recording: isRecording }"
            >
              <el-icon><VideoCameraFilled /></el-icon>
            </el-button>
          </el-tooltip>
        </div>

        <!-- 语音输入控制 -->
        <div class="voice-controls" v-if="isCallActive">
          <el-button 
            :class="['voice-btn', { recording: isVoiceRecording }]"
            @click="toggleVoiceInput"
            :disabled="!isVoiceSupported || isAISpeaking"
            size="small"
          >
            <el-icon><Microphone /></el-icon>
            {{ isVoiceRecording ? '停止说话' : '语音输入' }}
          </el-button>
          
          <div class="voice-visualizer" v-if="isVoiceRecording || isAISpeaking">
            <div 
              v-for="i in 10" 
              :key="i" 
              class="wave-bar"
              :style="waveStyle(i)"
            ></div>
          </div>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import AudioVisualizer from '@/components/AudioVisualizer.vue'
import { 
  VideoCamera, 
  Microphone, 
  User, 
  Phone, 
  Switch, 
  Monitor, 
  VideoCameraFilled 
} from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const isCallActive = ref(false)
const isStartingCall = ref(false)
const isVideoEnabled = ref(true)
const isAudioEnabled = ref(true)
const isScreenSharing = ref(false)
const isRecording = ref(false)
const isVoiceRecording = ref(false)
const isAISpeaking = ref(false)
const isAIThinking = ref(false)
const isUserSpeaking = ref(false)
const isBlinking = ref(false)
const currentSpeechText = ref('')
const callStartTime = ref(null)
const callDuration = ref('00:00')

// 媒体流
const localVideo = ref(null)
const localStream = ref(null)
const aiAudioStream = ref(null)

// 对话历史
const conversationHistory = ref([])

// 连接状态
const connectionStatus = computed(() => {
  if (!isCallActive.value) {
    return { type: 'info', text: '准备通话' }
  }
  if (isStartingCall.value) {
    return { type: 'warning', text: '连接中...' }
  }
  return { type: 'success', text: '通话中' }
})

// AI状态
const aiStatus = computed(() => {
  if (isAIThinking.value) return { type: 'warning', text: '思考中' }
  if (isAISpeaking.value) return { type: 'success', text: '回复中' }
  if (isUserSpeaking.value) return { type: 'info', text: '聆听中' }
  return { type: 'info', text: '在线' }
})

// AI状态文本
const aiStatusText = computed(() => {
  if (isAIThinking.value) return '正在思考您的问题...'
  if (isAISpeaking.value) return '正在回复...'
  if (isUserSpeaking.value) return '正在聆听...'
  return '等待您的发言'
})

// 检查语音支持
const isVoiceSupported = computed(() => {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
})

// 波形样式
const waveStyle = (index) => {
  const baseHeight = 3
  const amplitude = isVoiceRecording.value || isAISpeaking.value ? Math.random() * 15 + 5 : baseHeight
  return {
    height: `${baseHeight + amplitude}px`,
    animationDelay: `${index * 0.1}s`
  }
}

// 初始化媒体流
const initializeMediaStream = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { ideal: 30 }
      },
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    })
    
    localStream.value = stream
    if (localVideo.value) {
      localVideo.value.srcObject = stream
    }
    
    return true
  } catch (error) {
    console.error('获取媒体流失败:', error)
    ElMessage.error('无法访问摄像头和麦克风，请检查权限设置')
    return false
  }
}

// 开始视频通话
const startVideoCall = async () => {
  isStartingCall.value = true
  
  try {
    // 检查媒体权限
    const hasPermission = await initializeMediaStream()
    if (!hasPermission) {
      isStartingCall.value = false
      return
    }
    
    // 模拟AI连接过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    isCallActive.value = true
    isStartingCall.value = false
    callStartTime.value = new Date()
    
    // 开始计时
    startCallTimer()
    
    ElMessage.success('视频通话已连接')
    
  } catch (error) {
    console.error('开始视频通话失败:', error)
    ElMessage.error('开始视频通话失败')
    isStartingCall.value = false
  }
}

// 结束视频通话
const endVideoCall = () => {
  ElMessageBox.confirm(
    '确定要结束视频通话吗？',
    '结束通话确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 停止所有媒体流
    if (localStream.value) {
      localStream.value.getTracks().forEach(track => track.stop())
      localStream.value = null
    }
    
    // 重置状态
    isCallActive.value = false
    isScreenSharing.value = false
    isRecording.value = false
    isVoiceRecording.value = false
    isAISpeaking.value = false
    isAIThinking.value = false
    
    // 停止计时
    stopCallTimer()
    
    ElMessage.info('视频通话已结束')
  })
}

// 切换视频
const toggleVideo = () => {
  if (localStream.value) {
    const videoTrack = localStream.value.getVideoTracks()[0]
    if (videoTrack) {
      videoTrack.enabled = !videoTrack.enabled
      isVideoEnabled.value = videoTrack.enabled
      ElMessage.info(isVideoEnabled.value ? '摄像头已开启' : '摄像头已关闭')
    }
  }
}

// 切换音频
const toggleAudio = () => {
  if (localStream.value) {
    const audioTrack = localStream.value.getAudioTracks()[0]
    if (audioTrack) {
      audioTrack.enabled = !audioTrack.enabled
      isAudioEnabled.value = audioTrack.enabled
      ElMessage.info(isAudioEnabled.value ? '麦克风已开启' : '麦克风已关闭')
    }
  }
}

// 切换摄像头
const switchCamera = async () => {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoDevices = devices.filter(device => device.kind === 'videoinput')
    
    if (videoDevices.length > 1) {
      ElMessage.info('正在切换摄像头...')
      // 这里可以实现摄像头切换逻辑
    } else {
      ElMessage.warning('未检测到多个摄像头')
    }
  } catch (error) {
    console.error('切换摄像头失败:', error)
    ElMessage.error('切换摄像头失败')
  }
}

// 切换屏幕共享
const toggleScreenShare = async () => {
  try {
    if (!isScreenSharing.value) {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true
      })
      
      isScreenSharing.value = true
      ElMessage.success('屏幕共享已开始')
      
      // 处理屏幕共享结束
      stream.getVideoTracks()[0].onended = () => {
        isScreenSharing.value = false
        ElMessage.info('屏幕共享已结束')
      }
    } else {
      isScreenSharing.value = false
      ElMessage.info('屏幕共享已结束')
    }
  } catch (error) {
    console.error('屏幕共享失败:', error)
    ElMessage.error('屏幕共享失败')
  }
}

// 切换录制
const toggleRecording = () => {
  isRecording.value = !isRecording.value
  ElMessage.info(isRecording.value ? '开始录制通话' : '停止录制通话')
}

// 语音识别相关
let recognition = null

// 初始化语音识别
const initSpeechRecognition = () => {
  if (!isVoiceSupported.value) return

  try {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition = new SpeechRecognition()
    
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'zh-CN'

    recognition.onstart = () => {
      isUserSpeaking.value = true
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
        handleUserSpeech(finalTranscript)
      } else if (interimTranscript) {
        currentSpeechText.value = interimTranscript
      }
    }

    recognition.onerror = (event) => {
      console.error('语音识别错误:', event.error)
      stopVoiceRecording()
    }

    recognition.onend = () => {
      if (isVoiceRecording.value) {
        recognition.start()
      }
    }

  } catch (error) {
    console.error('语音识别初始化失败:', error)
  }
}

// 切换语音输入
const toggleVoiceInput = () => {
  if (isVoiceRecording.value) {
    stopVoiceRecording()
  } else {
    startVoiceRecording()
  }
}

// 开始语音录音
const startVoiceRecording = () => {
  if (!isVoiceSupported.value) {
    ElMessage.warning('浏览器不支持语音识别')
    return
  }

  isVoiceRecording.value = true
  currentSpeechText.value = ''
  
  if (recognition) {
    recognition.start()
  } else {
    initSpeechRecognition()
  }
}

// 停止语音录音
const stopVoiceRecording = () => {
  isVoiceRecording.value = false
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
    `通过视频看到您了！您说的是："${userText}"。`, 
    `在视频通话中听到您说："${userText}"，让我来帮您分析。`,
    `您通过视频提到的"${userText}"很有意思！`,
    `在视频交流中，您提出的"${userText}"让我想到...`,
    `通过视频通话，我了解到您关心："${userText}"。`
  ]
  
  return responses[Math.floor(Math.random() * responses.length)]
}

// 文字转语音
const speakText = (text) => {
  return new Promise((resolve) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'zh-CN'
      utterance.volume = 0.8
      utterance.rate = 1.0
      utterance.pitch = 1.0

      utterance.onend = () => {
        // 添加到对话历史
        const aiMessage = {
          type: 'ai',
          text: text,
          time: new Date().toLocaleTimeString('zh-CN', { hour12: false })
        }
        conversationHistory.value.push(aiMessage)
        resolve()
      }

      utterance.onerror = () => {
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

// 通话计时器
let callTimer = null
const startCallTimer = () => {
  callTimer = setInterval(() => {
    if (callStartTime.value) {
      const now = new Date()
      const diff = Math.floor((now - callStartTime.value) / 1000)
      const minutes = Math.floor(diff / 60).toString().padStart(2, '0')
      const seconds = (diff % 60).toString().padStart(2, '0')
      callDuration.value = `${minutes}:${seconds}`
    }
  }, 1000)
}

const stopCallTimer = () => {
  if (callTimer) {
    clearInterval(callTimer)
    callTimer = null
  }
  callDuration.value = '00:00'
}

// 返回文字聊天
const goBack = () => {
  // 停止所有活动
  if (isCallActive.value) {
    endVideoCall()
  }
  
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
  ElMessage.info('欢迎使用视频通话功能！点击"开始视频通话"按钮开始')
})

// 组件卸载
onUnmounted(() => {
  if (blinkInterval) clearInterval(blinkInterval)
  if (recognition) recognition.stop()
  if (localStream.value) {
    localStream.value.getTracks().forEach(track => track.stop())
  }
  speechSynthesis.cancel()
  stopCallTimer()
})
</script>

<style scoped>
.video-chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1a1a1a;
  color: white;
}

.video-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: #2d2d2d;
  border-bottom: 1px solid #404040;
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

.header-status {
  display: flex;
  align-items: center;
  gap: 15px;
}

.call-duration {
  font-family: 'Courier New', monospace;
  font-size: 1.1rem;
  font-weight: 600;
  color: #4facfe;
}

.video-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 20px;
}

.video-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  height: 60vh;
}

.video-layout.ai-speaking .ai-video {
  border: 2px solid #4facfe;
}

.video-layout.user-speaking .local-video {
  border: 2px solid #52c41a;
}

.video-panel {
  background: #2d2d2d;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.video-header {
  padding: 10px 15px;
  background: #404040;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.video-title {
  font-weight: 600;
  font-size: 1rem;
}

.video-controls {
  display: flex;
  gap: 5px;
}

.video-content {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-element.video-disabled {
  display: none;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #666;
}

.video-placeholder .el-icon {
  font-size: 3rem;
}

.ai-avatar {
  width: 200px;
  height: 200px;
  background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s ease;
}

.ai-avatar.speaking {
  transform: scale(1.05);
  animation: pulse 1s infinite;
}

.ai-avatar.listening {
  animation: listening 2s infinite;
}

.ai-face {
  position: relative;
  width: 80%;
  height: 80%;
}

.ai-eyes {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.eye {
  width: 25px;
  height: 25px;
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
  width: 12px;
  height: 12px;
  background: #333;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.ai-mouth {
  width: 30px;
  height: 8px;
  background: #ff6b6b;
  border-radius: 4px;
  margin: 0 auto;
  transition: all 0.3s ease;
}

.ai-mouth.speaking {
  animation: mouth-speak 0.5s infinite alternate;
}

.ai-status-display {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
}

.status-text {
  font-size: 1rem;
  margin-bottom: 10px;
}

.thinking-dots {
  display: flex;
  justify-content: center;
  gap: 4px;
}

.thinking-dots span {
  width: 6px;
  height: 6px;
  background: #ffd93d;
  border-radius: 50%;
  animation: thinking 1.4s infinite ease-in-out;
}

.thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots span:nth-child(2) { animation-delay: -0.16s; }

.audio-visualizer {
  position: absolute;
  bottom: 10px;
  left: 10px;
  right: 10px;
}

.ai-audio {
  bottom: 60px;
}

.conversation-log {
  height: 150px;
  background: #2d2d2d;
  border-radius: 10px;
  padding: 15px;
  overflow-y: auto;
}

.message {
  display: flex;
  margin-bottom: 10px;
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #404040;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 10px;
}

.ai-avatar-small {
  width: 20px;
  height: 20px;
  background: #4facfe;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.7rem;
}

.message-content {
  flex: 1;
  background: #404040;
  border-radius: 10px;
  padding: 8px 12px;
  max-width: 70%;
}

.message.user .message-content {
  background: #52c41a;
}

.message-text {
  font-size: 0.9rem;
  line-height: 1.3;
}

.message-time {
  font-size: 0.7rem;
  opacity: 0.7;
  margin-top: 3px;
}

.video-controls {
  background: #2d2d2d;
  padding: 20px;
  border-top: 1px solid #404040;
}

.controls-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}

.main-controls {
  display: flex;
  gap: 15px;
}

.call-btn, .end-call-btn {
  padding: 12px 24px;
  font-size: 1.1rem;
  font-weight: 600;
}

.secondary-controls {
  display: flex;
  gap: 10px;
}

.voice-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.voice-btn {
  background: linear-gradient(45deg, #ff6b6b, #ffd93d);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.voice-btn.recording {
  background: linear-gradient(45deg, #ff416c, #ff4b2b);
  animation: pulse 1s infinite;
}

.voice-visualizer {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 20px;
}

.wave-bar {
  width: 2px;
  background: #4facfe;
  border-radius: 1px;
  animation: wave 1s infinite ease-in-out;
}

.speech-preview {
  text-align: center;
  background: #404040;
  border-radius: 5px;
  padding: 8px;
  margin-top: 10px;
}

.preview-label {
  font-size: 0.8rem;
  opacity: 0.8;
  margin-bottom: 3px;
}

.preview-text {
  font-size: 0.9rem;
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
  .video-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .video-panel {
    height: 200px;
  }
  
  .ai-avatar {
    width: 120px;
    height: 120px;
  }
  
  .controls-container {
    gap: 10px;
  }
  
  .main-controls {
    flex-direction: column;
  }
}
</style>