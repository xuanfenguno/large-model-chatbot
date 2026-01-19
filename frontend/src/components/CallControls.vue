<template>
  <div class="call-controls">
    <!-- 静音控制 -->
    <button 
      :class="['control-btn', 'mute-btn', { active: isMuted }]"
      @click="$emit('toggle-mute')"
      :title="isMuted ? '取消静音' : '静音'"
    >
      <el-icon v-if="isMuted">
        <Mute />
      </el-icon>
      <el-icon v-else>
        <Microphone />
      </el-icon>
    </button>
    
    <!-- 扬声器控制 -->
    <button 
      :class="['control-btn', 'speaker-btn', { active: isSpeaker }]"
      @click="$emit('toggle-speaker')"
      :title="isSpeaker ? '关闭扬声器' : '开启扬声器'"
    >
      <el-icon v-if="isSpeaker">
        <Headset />
      </el-icon>
      <el-icon v-else>
        <Headset />
      </el-icon>
    </button>
    
    <!-- 挂断按钮 -->
    <button 
      class="control-btn end-call-btn"
      @click="$emit('end-call')"
      title="挂断"
    >
      <el-icon>
        <Phone />
      </el-icon>
    </button>
  </div>
</template>

<script setup>
import { Microphone, Mute, Headset, Phone } from '@element-plus/icons-vue'

defineProps({
  isMuted: {
    type: Boolean,
    default: false
  },
  isSpeaker: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle-mute', 'toggle-speaker', 'end-call'])
</script>

<style scoped>
.call-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
  padding: 1rem 0;
}

.control-btn {
  width: 60px;
  height: 60px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1.5rem;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.control-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.control-btn:active {
  transform: translateY(0);
}

.mute-btn {
  background: #909399;
}

.mute-btn.active {
  background: #f56c6c;
}

.mute-btn:hover {
  background: #a6a9ad;
}

.mute-btn.active:hover {
  background: #f78989;
}

.speaker-btn {
  background: #909399;
}

.speaker-btn.active {
  background: #67c23a;
}

.speaker-btn:hover {
  background: #a6a9ad;
}

.speaker-btn.active:hover {
  background: #85ce61;
}

.end-call-btn {
  background: #f56c6c;
}

.end-call-btn:hover {
  background: #f78989;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .call-controls {
    gap: 0.75rem;
  }
  
  .control-btn {
    width: 50px;
    height: 50px;
    font-size: 1.2rem;
  }
}
</style>