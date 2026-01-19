<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from './stores/auth'
import { useChatStore } from './stores/chat'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const chatStore = useChatStore()

// 监听未读消息
const unreadCount = computed(() => chatStore.unreadCount)

if (unreadCount.value > 0) {
  ElMessage({
    message: `您有 ${unreadCount.value} 条未读消息`,
    type: 'info',
    duration: 3000
  })
}
</script>

<style>
#app {
  font-family: 'Arial', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>