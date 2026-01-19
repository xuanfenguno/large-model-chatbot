<template>
  <div class="audio-visualizer">
    <canvas ref="canvas" :class="['visualizer-canvas', { local: isLocal }]" />
    <div class="audio-status">
      <el-icon v-if="isLocal && isMuted" class="muted-icon">
        <Mute />
      </el-icon>
      <div v-else class="audio-level">{{ audioLevel }}%</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Mute } from '@element-plus/icons-vue'

const props = defineProps({
  stream: {
    type: MediaStream,
    default: null
  },
  isLocal: {
    type: Boolean,
    default: false
  }
})

const canvas = ref(null)
const audioContext = ref(null)
const analyser = ref(null)
const dataArray = ref(null)
const animationId = ref(null)
const audioLevel = ref(0)
const isMuted = ref(false)

// 初始化音频分析器
const initializeAnalyser = async () => {
  if (!props.stream) return

  try {
    // 创建音频上下文
    audioContext.value = new (window.AudioContext || window.webkitAudioContext)()
    
    // 创建分析器
    analyser.value = audioContext.value.createAnalyser()
    analyser.value.fftSize = 256
    
    // 创建数据数组
    const bufferLength = analyser.value.frequencyBinCount
    dataArray.value = new Uint8Array(bufferLength)
    
    // 连接音频源
    const source = audioContext.value.createMediaStreamSource(props.stream)
    source.connect(analyser.value)
    
    // 检查是否静音
    checkMuteStatus()
    
    // 开始动画
    startVisualization()
  } catch (error) {
    console.error('初始化音频分析器失败:', error)
  }
}

// 检查静音状态
const checkMuteStatus = () => {
  if (props.stream && props.isLocal) {
    const audioTracks = props.stream.getAudioTracks()
    isMuted.value = audioTracks.length > 0 && !audioTracks[0].enabled
  }
}

// 开始可视化
const startVisualization = () => {
  if (!canvas.value || !analyser.value) return
  
  const ctx = canvas.value.getContext('2d')
  const width = canvas.value.width
  const height = canvas.value.height
  
  const draw = () => {
    animationId.value = requestAnimationFrame(draw)
    
    if (!analyser.value || !dataArray.value) return
    
    analyser.value.getByteFrequencyData(dataArray.value)
    
    // 计算平均音量
    let sum = 0
    for (let i = 0; i < dataArray.value.length; i++) {
      sum += dataArray.value[i]
    }
    const average = sum / dataArray.value.length
    audioLevel.value = Math.min(100, Math.round((average / 255) * 100))
    
    // 清除画布
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'
    ctx.fillRect(0, 0, width, height)
    
    // 绘制波形
    const barWidth = (width / dataArray.value.length) * 2.5
    let barHeight
    let x = 0
    
    for (let i = 0; i < dataArray.value.length; i++) {
      barHeight = (dataArray.value[i] / 255) * height
      
      // 根据音量设置颜色
      const hue = props.isLocal ? 200 : 0 // 本地蓝色，对方红色
      const saturation = 70
      const lightness = 50 + (barHeight / height) * 30
      
      ctx.fillStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`
      ctx.fillRect(x, height - barHeight, barWidth, barHeight)
      
      x += barWidth + 1
    }
  }
  
  draw()
}

// 停止可视化
const stopVisualization = () => {
  if (animationId.value) {
    cancelAnimationFrame(animationId.value)
    animationId.value = null
  }
  
  if (audioContext.value) {
    audioContext.value.close()
    audioContext.value = null
  }
  
  analyser.value = null
  dataArray.value = null
  audioLevel.value = 0
}

// 监听流变化
watch(() => props.stream, (newStream, oldStream) => {
  if (oldStream) {
    stopVisualization()
  }
  
  if (newStream) {
    initializeAnalyser()
  }
})

// 监听静音状态变化
watch(() => props.stream, (newStream) => {
  if (newStream && props.isLocal) {
    const audioTracks = newStream.getAudioTracks()
    if (audioTracks.length > 0) {
      // 监听静音状态变化
      audioTracks[0].addEventListener('enabled', () => {
        isMuted.value = !audioTracks[0].enabled
      })
    }
  }
})

// 生命周期
onMounted(() => {
  if (props.stream) {
    initializeAnalyser()
  }
})

onUnmounted(() => {
  stopVisualization()
})
</script>

<style scoped>
.audio-visualizer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.visualizer-canvas {
  width: 150px;
  height: 60px;
  border-radius: 8px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
}

.visualizer-canvas.local {
  border-color: #667eea;
}

.audio-status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #606266;
}

.muted-icon {
  color: #f56c6c;
  font-size: 1rem;
}

.audio-level {
  font-weight: 500;
  min-width: 30px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .visualizer-canvas {
    width: 120px;
    height: 50px;
  }
  
  .audio-status {
    font-size: 0.75rem;
  }
}
</style>