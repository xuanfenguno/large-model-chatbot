<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">欢迎来到AI聊天机器人</h1>
        <p class="hero-subtitle">体验智能对话，探索无限可能</p>
        <div class="hero-buttons">
          <el-button 
            type="primary" 
            size="large" 
            @click="goToLogin"
            class="btn-primary"
          >
            <el-icon><User /></el-icon>
            登录
          </el-button>
          <el-button 
            type="default" 
            size="large" 
            @click="goToRegister"
            class="btn-outline"
          >
            <el-icon><EditPen /></el-icon>
            注册
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="features-section">
      <div class="container">
        <h2 class="section-title">我们的特色</h2>
        <div class="features-grid">
          <div class="feature-card card">
            <div class="feature-icon">
              <el-icon><Lightning /></el-icon>
            </div>
            <h3 class="feature-title">智能对话</h3>
            <p class="feature-desc">基于先进AI技术，提供流畅自然的对话体验</p>
          </div>
          <div class="feature-card card">
            <div class="feature-icon">
              <el-icon><ChatLineRound /></el-icon>
            </div>
            <h3 class="feature-title">实时交流</h3>
            <p class="feature-desc">即时响应，让您的问题得到快速解答</p>
          </div>
          <div class="feature-card card">
            <div class="feature-icon">
              <el-icon><Lock /></el-icon>
            </div>
            <h3 class="feature-title">安全可靠</h3>
            <p class="feature-desc">严格的数据加密，保障您的隐私安全</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { 
  User, 
  EditPen, 
  Lightning, 
  ChatLineRound, 
  Lock 
} from '@element-plus/icons-vue'

const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow-x: hidden;
}

.hero-section {
  padding: 80px 20px 40px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  color: white;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.features-section {
  padding: 80px 20px;
  background: transparent;
  margin-top: -2px;
  position: relative;
  z-index: 1;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 3rem;
  color: white;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.feature-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #333;
}

.feature-desc {
  color: #666;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-primary, .btn-outline {
    width: 100%;
    max-width: 200px;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>