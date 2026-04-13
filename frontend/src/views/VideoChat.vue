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
      <div ref="conversationLogRef" class="conversation-log">
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
        <!-- 空状态提示 -->
        <div v-if="conversationHistory.length === 0" class="empty-log">
          <el-icon><ChatDotRound /></el-icon>
          <span>暂无对话记录，开始说话吧！</span>
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
          <el-tooltip content="点击开始语音识别，AI 会听到您说的话" placement="top">
            <el-button 
              :class="['voice-btn', 'speak-btn', { recording: isVoiceRecording }]"
              @click="toggleVoiceInput"
              :disabled="!isVoiceSupported || isAISpeaking"
              size="large"
            >
              <el-icon style="font-size: 1.5em; margin-right: 8px;"><Microphone /></el-icon>
              {{ isVoiceRecording ? '🔴 正在听您说话...' : '🎤 点击开始说话' }}
            </el-button>
          </el-tooltip>
          
          <div class="voice-visualizer" v-if="isVoiceRecording || isAISpeaking">
            <div 
              v-for="i in 10" 
              :key="i" 
              class="wave-bar"
              :style="waveStyle(i)"
            ></div>
          </div>
          
          <!-- 语音支持提示 -->
          <div class="voice-hint" v-if="!isVoiceSupported">
            <el-tag type="warning" size="small">
              <el-icon><Warning /></el-icon>
              您的浏览器不支持语音识别，请使用 Chrome 浏览器
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 未开始通话时的提示 -->
      <div class="voice-hint-before" v-if="!isCallActive">
        <el-alert
          title="💡 语音使用说明"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <p><strong>步骤 1：</strong>点击"开始视频通话"按钮</p>
            <p><strong>步骤 2：</strong>允许摄像头和麦克风权限</p>
            <p><strong>步骤 3：</strong>通话开始后，底部会出现 <strong style="color: #4facfe; font-size: 1.1em;">🎤 "开始说话"</strong> 按钮</p>
            <p><strong>步骤 4：</strong>点击该按钮即可开始语音识别，AI 会听到您说话</p>
          </template>
        </el-alert>
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
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
  VideoCameraFilled,
  Warning,
  ChatDotRound
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
const conversationLogRef = ref(null)  // 对话记录容器引用

// 滚动到最新消息
const scrollToBottom = () => {
  nextTick(() => {
    if (conversationLogRef.value) {
      conversationLogRef.value.scrollTop = conversationLogRef.value.scrollHeight
    }
  })
}

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
    
    // 模拟 AI 连接过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    isCallActive.value = true
    isStartingCall.value = false
    callStartTime.value = new Date()
    
    // 开始计时
    startCallTimer()
    
    ElMessage.success('视频通话已连接')
    
    // 显示语音识别引导提示
    setTimeout(() => {
      ElMessageBox.alert(
        `
        <div style="text-align: left; padding: 20px 0;">
          <p style="font-size: 16px; margin-bottom: 15px;">
            <strong style="color: #4facfe;">🎤 如何与 AI 语音对话：</strong>
          </p>
          <ol style="line-height: 2;">
            <li>找到页面<b style="color: #ff6b6b;">底部</b>的控制栏</li>
            <li>点击蓝色的 <strong style="color: #4facfe; font-size: 1.2em;">🎤 点击开始说话</strong> 按钮</li>
            <li>按钮变红后，对着麦克风说话</li>
            <li>AI 会听到您的话并回复</li>
          </ol>
          <p style="margin-top: 15px; color: #909399; font-size: 14px;">
            💡 提示：按钮在底部控制栏的最右边，很大很显眼！
          </p>
        </div>
        `,
        '语音使用说明',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '我知道了',
          type: 'info',
          customClass: 'voice-guide-messagebox'
        }
      )
    }, 1000)
    
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
  if (!isVoiceSupported.value) {
    console.warn('浏览器不支持语音识别')
    ElMessage.warning({
      message: '您的浏览器不支持语音识别，建议使用 Chrome 浏览器',
      duration: 5000
    })
    return
  }

  try {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition = new SpeechRecognition()
    
    // 配置语音识别
    recognition.continuous = true  // 持续识别
    recognition.interimResults = true  // 返回临时结果
    recognition.lang = 'zh-CN'  // 设置语言为中文
    recognition.maxAlternatives = 1  // 只返回一个最佳结果

    recognition.onstart = () => {
      console.log('语音识别已启动')
      isUserSpeaking.value = true
    }

    recognition.onresult = (event) => {
      console.log('语音识别结果事件:', event)
      let finalTranscript = ''
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        console.log(`识别结果 [${i}]:`, {
          transcript,
          isFinal: event.results[i].isFinal,
          confidence: event.results[i][0].confidence
        })
        
        if (event.results[i].isFinal) {
          finalTranscript += transcript
        } else {
          interimTranscript += transcript
        }
      }

      if (finalTranscript) {
        console.log('✅ 识别到完整语音:', finalTranscript)
        currentSpeechText.value = finalTranscript
        handleUserSpeech(finalTranscript)
      } else if (interimTranscript) {
        currentSpeechText.value = interimTranscript
        console.log('临时识别结果:', interimTranscript)
      } else {
        console.log('⚠️ 没有识别到任何内容')
      }
    }

    recognition.onerror = (event) => {
      console.error('语音识别错误:', event.error)
      
      // 处理不同类型的错误
      if (event.error === 'network') {
        console.warn('语音识别网络错误，可能是网络问题或浏览器不支持离线识别')
        // 不显示错误提示，避免频繁打扰用户
        console.log('将在 5 秒后尝试重新启动语音识别...')
      } else if (event.error === 'not-allowed') {
        console.warn('用户拒绝了麦克风权限')
        ElMessage.error({
          message: '需要麦克风权限才能进行语音识别，请在浏览器设置中允许',
          duration: 5000
        })
      } else if (event.error === 'no-speech') {
        console.log('没有检测到语音输入')
        // 这是正常情况，不需要显示错误
      } else if (event.error === 'aborted') {
        console.log('语音识别已中止')
        // 用户主动停止，不需要处理
      } else {
        console.warn(`语音识别错误：${event.error}`)
      }
      
      // 如果是网络错误，稍后尝试重启语音识别
      if (event.error === 'network' && isVoiceRecording.value) {
        console.log('5 秒后尝试重新启动语音识别...')
        setTimeout(() => {
          if (isVoiceRecording.value && recognition) {
            try {
              // @ts-ignore
              if (recognition.state !== 'running') {
                recognition.start()
                console.log('重新启动语音识别成功')
              }
            } catch (restartError) {
              console.error('重新启动语音识别失败:', restartError)
            }
          }
        }, 5000)
      } else if (event.error !== 'network') {
        // 非网络错误才停止
        stopVoiceRecording()
      }
    }

    recognition.onend = () => {
      console.log('语音识别已停止')
      if (isVoiceRecording.value) {
        // 如果是意外停止，尝试重启
        console.log('语音识别意外停止，尝试重启...')
        setTimeout(() => {
          if (isVoiceRecording.value && recognition) {
            try {
              recognition.start()
              console.log('自动重启语音识别成功')
            } catch (e) {
              console.log('自动重启失败:', e)
            }
          }
        }, 500)
      }
    }

    console.log('语音识别初始化成功')

  } catch (error) {
    console.error('语音识别初始化失败:', error)
    ElMessage.error({
      message: '语音识别初始化失败，请检查浏览器设置',
      duration: 5000
    })
  }
}

// 切换语音输入
const toggleVoiceInput = () => {
  console.log('切换语音输入，当前状态:', isVoiceRecording.value)
  
  if (isVoiceRecording.value) {
    stopVoiceRecording()
  } else {
    startVoiceRecording()
  }
}

// 开始语音录音
const startVoiceRecording = () => {
  console.log('开始语音录音，当前状态:', {
    isVoiceRecording: isVoiceRecording.value,
    hasRecognition: !!recognition
  })
  
  if (!isVoiceSupported.value) {
    ElMessage.warning('浏览器不支持语音识别，建议使用 Chrome 浏览器')
    return
  }

  // 如果已经在录音中，不要重复启动
  if (isVoiceRecording.value) {
    console.log('已经在录音中，无需重复启动')
    return
  }

  isVoiceRecording.value = true
  currentSpeechText.value = ''
  
  // 如果是第一次启动，先初始化
  if (!recognition) {
    console.log('第一次启动，初始化语音识别...')
    initSpeechRecognition()
  }
  
  // 延迟启动，确保初始化完成
  setTimeout(() => {
    if (recognition) {
      try {
        // 检查是否已经在运行
        // @ts-ignore
        if (recognition.start && recognition.state !== 'running') {
          recognition.start()
          console.log('语音识别已启动')
          ElMessage.success('语音识别已启动，请开始说话')
        } else {
          console.log('语音识别已经在运行中')
        }
      } catch (error) {
        console.error('启动语音识别失败:', error)
        // 如果是"已经启动"的错误，忽略它
        if (error.message.includes('already started')) {
          console.log('语音识别已经启动，忽略此错误')
          ElMessage.success('语音识别已启动，请开始说话')
        } else {
          ElMessage.error('启动语音识别失败，请检查麦克风权限')
        }
      }
    } else {
      console.error('语音识别未初始化')
      ElMessage.error('语音识别初始化失败')
    }
  }, 200)
}

// 停止语音录音
const stopVoiceRecording = () => {
  console.log('停止语音录音')
  isVoiceRecording.value = false
  isUserSpeaking.value = false
  
  if (recognition) {
    try {
      recognition.stop()
      console.log('语音识别已停止')
    } catch (error) {
      console.error('停止语音识别失败:', error)
    }
  }
}

// 处理用户语音
const handleUserSpeech = async (text) => {
  console.log('🎤 handleUserSpeech 被调用，输入文本:', text)
  
  // 忽略太短的语音（可能是误识别）
  if (!text || text.trim().length < 2) {
    console.log('⚠️ 语音太短，忽略')
    return
  }
  
  console.log('✅ 语音内容有效，开始处理...')
  
  // 添加到对话历史
  const userMessage = {
    type: 'user',
    text: text,
    time: new Date().toLocaleTimeString('zh-CN', { hour12: false })
  }
  conversationHistory.value.push(userMessage)
  scrollToBottom()  // 滚动到最新消息
  console.log('✅ 已添加到对话历史')

  // AI 开始思考
  isAIThinking.value = true
  aiStatusText.value = 'AI 正在思考...'
  console.log('🤖 AI 开始思考，状态:', {
    isAIThinking: isAIThinking.value,
    aiStatusText: aiStatusText.value
  })
  
  try {
    // 模拟 AI 处理时间（1-3 秒）
    const thinkingTime = Math.random() * 2000 + 1000
    console.log(`⏱️ AI 思考时间：${thinkingTime}ms`)
    await new Promise(resolve => setTimeout(resolve, thinkingTime))
    
    // AI 生成回复
    console.log('📝 开始生成 AI 回复...')
    const aiResponse = await generateAIResponse(text)
    console.log('✅ AI 生成回复:', aiResponse)
    
    // AI 开始说话
    isAIThinking.value = false
    isAISpeaking.value = true
    aiStatusText.value = 'AI 正在说话...'
    console.log('🔊 AI 开始说话，状态:', {
      isAISpeaking: isAISpeaking.value,
      aiStatusText: aiStatusText.value
    })
    
    // 播放 AI 语音回复
    console.log('🔊 开始播放 AI 语音...')
    await speakText(aiResponse)
    console.log('✅ AI 语音播放完成')
    
    // AI 说完
    isAISpeaking.value = false
    aiStatusText.value = 'AI 助手'
    console.log('✅ AI 完成回复，状态:', {
      isAISpeaking: isAISpeaking.value,
      aiStatusText: aiStatusText.value
    })
    
  } catch (error) {
    console.error('❌ AI 处理错误:', error)
    ElMessage.error('AI 处理失败')
    isAIThinking.value = false
    aiStatusText.value = 'AI 助手'
  }
}

// 生成 AI 回复
const generateAIResponse = async (userText) => {
  console.log('📡 开始调用后端 AI API...')
  
  try {
    // 调用实际的 AI API
    const response = await fetch('http://localhost:8080/api/v1/function-router/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        feature_name: 'chat',  // 使用聊天功能
        user_input: userText,
        model: 'qwen-turbo'  // 使用通义千问模型
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('✅ API 响应:', data)
    
    if (data.error) {
      throw new Error(data.error)
    }
    
    if (data.result) {
      console.log('✅ AI 回复:', data.result)
      return data.result
    } else {
      throw new Error('API 返回空结果')
    }
  } catch (error) {
    console.error('❌ 调用 AI API 失败:', error)
    
    // API 调用失败时使用模拟回复
    console.log('⚠️ 使用模拟回复作为备用方案')
    const responses = [
      `通过视频看到您了！您说的是："${userText}"。`, 
      `在视频通话中听到您说："${userText}"，让我来帮您分析。`,
      `您通过视频提到的"${userText}"很有意思！`,
      `在视频交流中，您提出的"${userText}"让我想到...`,
      `通过视频通话，我了解到您关心："${userText}"。`
    ]
    
    return responses[Math.floor(Math.random() * responses.length)]
  }
}

// 文字转语音
const speakText = (text) => {
  console.log('🔊 speakText 被调用，文本:', text)
  
  return new Promise((resolve) => {
    if ('speechSynthesis' in window) {
      console.log('✅ 浏览器支持语音合成')
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'zh-CN'
      utterance.volume = 0.8
      utterance.rate = 1.0
      utterance.pitch = 1.0

      utterance.onstart = () => {
        console.log('🔊 语音播放开始')
      }

      utterance.onend = () => {
        console.log('✅ 语音播放完成')
        // 添加到对话历史
        const aiMessage = {
          type: 'ai',
          text: text,
          time: new Date().toLocaleTimeString('zh-CN', { hour12: false })
        }
        conversationHistory.value.push(aiMessage)
        scrollToBottom()
        resolve()
      }

      utterance.onerror = (event) => {
        console.error('❌ 语音播放错误:', event)
        // 即使出错也 resolve，避免卡住
        const aiMessage = {
          type: 'ai',
          text: text,
          time: new Date().toLocaleTimeString('zh-CN', { hour12: false })
        }
        conversationHistory.value.push(aiMessage)
        scrollToBottom()
        resolve()
      }

      console.log('🔊 开始播放语音...')
      speechSynthesis.speak(utterance)
    } else {
      console.warn('⚠️ 浏览器不支持语音合成，只显示文字')
      // 如果不支持语音合成，直接显示文字
      const aiMessage = {
        type: 'ai',
        text: text,
        time: new Date().toLocaleTimeString('zh-CN', { hour12: false })
      }
      conversationHistory.value.push(aiMessage)
      scrollToBottom()
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
  height: 200px;  /* 增加高度 */
  background: #1a1a1a;
  border-radius: 10px;
  padding: 15px;
  overflow-y: auto;
  border: 1px solid #333;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3);
  margin-top: 15px;
  position: relative;
}

.conversation-log::-webkit-scrollbar {
  width: 6px;
}

.conversation-log::-webkit-scrollbar-track {
  background: #2d2d2d;
  border-radius: 3px;
}

.conversation-log::-webkit-scrollbar-thumb {
  background: #4facfe;
  border-radius: 3px;
}

.conversation-log::-webkit-scrollbar-thumb:hover {
  background: #00f2fe;
}

.empty-log {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  font-size: 0.9rem;
}

.empty-log .el-icon {
  font-size: 3rem;
  margin-bottom: 10px;
  opacity: 0.5;
}

.message {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
  animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  flex-direction: row-reverse;
}

.message:last-child {
  margin-bottom: 0;
}

.message-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin: 0 10px;
  font-size: 0.9rem;
  font-weight: bold;
  color: white;
}

.message.user .message-avatar {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
}

.message-avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin: 0 10px;
  font-size: 0.9rem;
  font-weight: bold;
  color: white;
}

.message.user .message-avatar {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
}

.message.ai .message-avatar {
  background: linear-gradient(45deg, #f093fb, #f5576c);
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
  padding: 10px 14px;
  max-width: 70%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.message.user .message-content {
  background: linear-gradient(45deg, #52c41a, #73d13d);
  color: white;
}

.message.ai .message-content {
  background: #404040;
  color: #fff;
  border: 1px solid #505050;
}

.message-text {
  font-size: 0.95rem;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.6;
  margin-top: 5px;
  text-align: right;
}

.video-controls {
  background: #2d2d2d;
  padding: 20px;
  border-top: 1px solid #404040;
}

.controls-container {
  display: flex;
  flex-direction: row;  /* 改为水平排列 */
  gap: 20px;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;  /* 允许换行 */
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
  align-items: center;
}

.voice-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 0;  /* 移除 padding，和其他按钮对齐 */
  background: transparent;  /* 移除背景，和其他按钮一致 */
  border-radius: 0;
}

.voice-btn {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-weight: bold;
  font-size: 1.1rem;
  padding: 15px 30px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.5);
  animation: glow 2s infinite;
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(79, 172, 254, 0.5);
  }
  50% {
    box-shadow: 0 4px 25px rgba(79, 172, 254, 0.8), 0 0 10px rgba(79, 172, 254, 0.6);
  }
}

.voice-btn:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 6px 25px rgba(79, 172, 254, 0.8);
  animation: none;
}

.voice-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  animation: none;
}

.voice-btn.recording {
  background: linear-gradient(45deg, #ff416c, #ff4b2b);
  animation: pulse 1s infinite, glow-red 2s infinite;
  box-shadow: 0 4px 15px rgba(255, 65, 108, 0.5);
  border-color: rgba(255, 255, 255, 0.5);
}

@keyframes glow-red {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(255, 65, 108, 0.5);
  }
  50% {
    box-shadow: 0 4px 25px rgba(255, 65, 108, 0.8), 0 0 10px rgba(255, 65, 108, 0.6);
  }
}

.voice-hint {
  margin-left: 10px;
}

.voice-hint-before {
  width: 100%;
  margin-top: 10px;
}

.voice-hint-before .el-alert {
  background: rgba(79, 172, 254, 0.1);
  border: 1px solid rgba(79, 172, 254, 0.3);
}

.voice-hint-before p {
  margin: 5px 0;
  font-size: 0.9rem;
  line-height: 1.6;
}

.voice-guide-messagebox .el-message-box__header {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  color: white;
  padding: 20px;
  border-radius: 10px 10px 0 0;
}

.voice-guide-messagebox .el-message-box__title {
  color: white;
  font-size: 18px;
}

.voice-guide-messagebox .el-message-box__content {
  padding: 30px 20px;
}

.voice-guide-messagebox .el-message-box__btns {
  padding: 20px;
}

.voice-guide-messagebox .el-button--primary {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  border: none;
  padding: 12px 30px;
  font-size: 16px;
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