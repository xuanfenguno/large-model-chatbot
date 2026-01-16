<template>
  <div class="redirect-container">
    <div class="redirect-content">
      <div class="spinner"></div>
      <h2>正在跳转到注册页面...</h2>
      <p>您将很快被重定向到登录/注册页面</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { onMounted } from 'vue'

const router = useRouter()
const route = useRoute()

onMounted(() => {
  // 延迟一小段时间后重定向到登录页面并切换到注册表单
  setTimeout(() => {
    router.push({ path: '/login', query: { tab: 'register' } })
  }, 1500)
})
</script>

<style scoped>
.redirect-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.redirect-content {
  text-align: center;
  color: white;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

h2 {
  font-size: 18px;
  margin-bottom: 10px;
}

p {
  font-size: 14px;
  opacity: 0.8;
}
</style>