<template>
  <div class="function-router">
    <!-- 顶部导航栏 - 最高层级 -->
    <div class="top-navbar">
      <div class="navbar-content">
        <!-- 返回按钮 - 次层级 -->
        <el-button 
          type="text" 
          icon="ArrowLeft" 
          @click="goBack"
          class="nav-back-button"
        >
          返回聊天
        </el-button>
        
        <!-- AI多功能助手标题 - 与返回按钮同一水平线 -->
        <div class="navbar-title">
          <div class="title-container">
            <div class="title-icon">✨</div>
            <div class="title-content">
              <h1 class="main-title">AI多功能助手</h1>
              <p class="subtitle">18种智能功能，为您提供个性化AI体验</p>
            </div>
            <div class="title-badge">
              <span class="badge-text">智能</span>
            </div>
          </div>
        </div>
        
        <!-- 右侧占位，保持平衡 -->
        <div class="navbar-actions"></div>
      </div>
    </div>
    
    <!-- 主内容区域 -->
    <div class="main-layout">
      
      <!-- 主内容区主体部分 -->
      <div class="main-content-body">
        <!-- 左侧菜单 - 辅助导航 -->
        <aside class="sidebar-nav">
        <div class="menu-header">
          <h3 class="menu-title">功能菜单</h3>
        </div>
        
        <el-menu
          :default-active="activeFunction"
          class="function-menu"
          @select="handleFunctionSelect"
        >
          <el-menu-item index="auto" class="menu-item">
            <span>自动识别</span>
          </el-menu-item>
          <el-menu-item index="chat" class="menu-item">
            <span>聊天</span>
          </el-menu-item>
          <el-menu-item index="joke" class="menu-item">
            <span>笑话</span>
          </el-menu-item>
          <el-menu-item index="story" class="menu-item">
            <span>故事</span>
          </el-menu-item>
          <el-menu-item index="chengyu" class="menu-item">
            <span>成语接龙</span>
          </el-menu-item>
          <el-menu-item index="encyclopedia" class="menu-item">
            <span>百科全书</span>
          </el-menu-item>
          <el-menu-item index="poetry" class="menu-item">
            <span>诗词创作</span>
          </el-menu-item>
          <el-menu-item index="translate" class="menu-item">
            <span>翻译</span>
          </el-menu-item>
          <el-menu-item index="math" class="menu-item">
            <span>数学问题</span>
          </el-menu-item>
          <el-menu-item index="programming" class="menu-item">
            <span>编程帮助</span>
          </el-menu-item>
          <el-menu-item index="weather" class="menu-item">
            <span>天气查询</span>
          </el-menu-item>
          <el-menu-item index="calculator" class="menu-item">
            <span>计算器</span>
          </el-menu-item>
          <el-menu-item index="life_advice" class="menu-item">
            <span>生活建议</span>
          </el-menu-item>
          <el-menu-item index="news" class="menu-item">
            <span>新闻</span>
          </el-menu-item>
          <el-menu-item index="emotion" class="menu-item">
            <span>情感支持</span>
          </el-menu-item>
          <el-menu-item index="game" class="menu-item">
            <span>游戏</span>
          </el-menu-item>
          <el-menu-item index="education" class="menu-item">
            <span>教育</span>
          </el-menu-item>
          <el-menu-item index="health" class="menu-item">
            <span>健康</span>
          </el-menu-item>
          <el-menu-item index="finance" class="menu-item">
            <span>金融</span>
          </el-menu-item>
        </el-menu>
      </aside>
      
      <!-- 右侧内容区域 -->
      <main class="content-area apple-glass-content">
        <div class="function-container">
          <!-- 功能控制栏 -->
          <div class="function-control-bar">
            <div class="function-info">
              <div class="function-title-line">
                <h2 class="function-title">{{ getFunctionName(activeFunction) }}</h2>
                <p class="function-description">{{ getFunctionDescription(activeFunction) }}</p>
              </div>
            </div>
            
            <div class="model-selector-wrapper">
              <el-select v-model="selectedModel" placeholder="选择AI模型" class="model-selector apple-glass-select">
                <el-option
                  v-for="model in availableModels"
                  :key="model.value"
                  :label="model.label"
                  :value="model.value"
                />
              </el-select>
            </div>
          </div>
          
          <!-- 聊天消息区域 -->
          <div class="messages-container apple-glass-messages" ref="messagesAreaRef">
            <div 
              v-for="(msg, index) in messages" 
              :key="index" 
              :class="['message-bubble', msg.role]"
            >
              <div class="message-avatar apple-glass-avatar">
                {{ msg.role === 'user' ? '👤' : '🤖' }}
              </div>
              <div class="message-content apple-glass-message">
                <div class="message-text">{{ msg.content }}</div>
                <div class="message-time">{{ formatDate(msg.timestamp) }}</div>
              </div>
            </div>
          </div>
          
          <!-- 输入区域 -->
          <div class="input-container apple-glass-input">
            <div class="input-wrapper">
              <el-input
                v-model="inputMessage"
                :placeholder="getInputPlaceholder(activeFunction)"
                @keyup.enter="sendMessage"
                :disabled="loading"
                size="large"
                class="message-input apple-glass-field"
              >
                <template #append>
                  <el-button 
                    @click="sendMessage" 
                    :loading="loading" 
                    type="primary"
                    size="large"
                    class="send-button apple-glass-button"
                  >
                    发送
                  </el-button>
                </template>
              </el-input>
            </div>
          </div>
        </div>
      </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const activeFunction = ref('auto');
const inputMessage = ref('');
const messages = ref([]);
const loading = ref(false);
const selectedModel = ref('qwen-max');
const availableModels = ref([]);
const messagesAreaRef = ref(null);

// 获取可用模型列表
const fetchAvailableModels = async () => {
  try {
    const response = await axios.get('/api/v1/models/');
    availableModels.value = response.data.map(model => ({
      value: model.name,
      label: model.label || model.name
    }));
  } catch (error) {
    console.error('获取模型列表失败:', error);
    // 默认模型列表
    availableModels.value = [
      { value: 'kimi-large', label: 'Kimi Large' },
      { value: 'qwen-max', label: 'Qwen Max' },
      { value: 'qwen-plus', label: 'Qwen Plus' },
      { value: 'qwen-turbo', label: 'Qwen Turbo' },
    ];
  }
};

onMounted(() => {
  fetchAvailableModels();
});

// 格式化时间
const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 返回聊天界面
const goBack = () => {
  router.push('/chat');
};

// 获取功能名称
const getFunctionName = (funcType) => {
  const funcNames = {
    auto: '自动识别',
    chat: '聊天',
    joke: '笑话',
    story: '故事',
    chengyu: '成语接龙',
    encyclopedia: '百科全书',
    poetry: '诗词创作',
    translate: '翻译',
    math: '数学问题',
    programming: '编程帮助',
    weather: '天气查询',
    calculator: '计算器',
    life_advice: '生活建议',
    news: '新闻',
    emotion: '情感支持',
    game: '游戏',
    education: '教育',
    health: '健康',
    finance: '金融'
  };
  return funcNames[funcType] || '未知功能';
};

// 获取功能描述
const getFunctionDescription = (funcType) => {
  const descriptions = {
    auto: 'AI自动识别您的需求并选择最适合的功能',
    chat: '与AI进行自然对话，获取智能回答',
    joke: '获取有趣的笑话，放松心情',
    story: '生成精彩的故事，激发想象力',
    chengyu: '参与成语接龙游戏，学习传统文化',
    encyclopedia: '查询各类知识，获取准确信息',
    poetry: '创作优美的诗词，体验文学魅力',
    translate: '多语言翻译，打破沟通障碍',
    math: '解决数学问题，提供详细解答',
    programming: '编程问题解答和代码帮助',
    weather: '查询天气信息，规划出行',
    calculator: '进行各种数学计算',
    life_advice: '获取生活建议，解决日常问题',
    news: '了解最新新闻资讯',
    emotion: '情感支持和心理辅导',
    game: '游戏相关问题和娱乐',
    education: '学习辅导和教育资源',
    health: '健康咨询和医疗建议',
    finance: '金融知识和投资建议'
  };
  return descriptions[funcType] || 'AI多功能助手为您服务';
};

// 获取输入框占位符
const getInputPlaceholder = (funcType) => {
  const placeholders = {
    auto: '请描述您的需求，AI将自动识别功能...',
    chat: '请输入您想聊的内容...',
    joke: '请输入主题或直接获取笑话...',
    story: '请输入故事主题或要求...',
    chengyu: '请输入成语或开始接龙...',
    encyclopedia: '请输入您想查询的知识...',
    poetry: '请输入诗词主题或要求...',
    translate: '请输入需要翻译的内容...',
    math: '请输入数学问题...',
    programming: '请输入编程问题或代码...',
    weather: '请输入城市名称查询天气...',
    calculator: '请输入计算表达式...',
    life_advice: '请输入您的生活问题...',
    news: '请输入新闻关键词...',
    emotion: '请分享您的情感问题...',
    game: '请输入游戏相关问题...',
    education: '请输入学习问题...',
    health: '请输入健康问题...',
    finance: '请输入金融问题...'
  };
  return placeholders[funcType] || '请输入内容...';
};

// 处理功能选择
const handleFunctionSelect = (index) => {
  activeFunction.value = index;
};

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return;
  
  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    timestamp: new Date().toISOString()
  };
  
  messages.value.push(userMessage);
  inputMessage.value = '';
  loading.value = true;
  
  try {
    const response = await axios.post('/api/v1/function-router/', {
      input: userMessage.content,
      model: selectedModel.value
    });
    
    const aiMessage = {
      role: 'assistant',
      content: response.data.result,
      timestamp: new Date().toISOString()
    };
    
    messages.value.push(aiMessage);
  } catch (error) {
    const errorMessage = {
      role: 'assistant',
      content: '很抱歉，请求失败：' + (error.response?.data?.error || error.message),
      timestamp: new Date().toISOString()
    };
    messages.value.push(errorMessage);
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (messagesAreaRef.value) {
    messagesAreaRef.value.scrollTop = messagesAreaRef.value.scrollHeight;
  }
};

onMounted(() => {
  fetchAvailableModels();
});
</script>

<style scoped>
/* 全局样式 */
.function-router {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* 顶部导航栏 - 最高层级 */
.top-navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  position: relative;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 80px;
}

/* 导航栏标题样式 */
.navbar-title {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  margin: 0 20px;
}

.navbar-title .title-container {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 12px 20px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
  justify-content: center;
}

.navbar-title .title-icon {
  font-size: 2rem;
  animation: sparkle 2s ease-in-out infinite;
}

.navbar-title .title-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  text-align: center;
}

.navbar-title .main-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.navbar-title .subtitle {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0;
  font-weight: 500;
  line-height: 1.3;
}

.navbar-title .title-badge {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 20px;
  padding: 4px 12px;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(5, 150, 105, 0.3);
}

.nav-back-button {
  color: white !important;
  font-size: 1rem;
  font-weight: 500;
  padding: 10px 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.nav-back-button:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.6);
  transform: translateX(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.navbar-title {
  text-align: center;
  flex: 1;
  margin: 0 40px;
}

.main-title {
  margin: 0 0 8px 0;
  font-size: 2.2rem;
  font-weight: 700;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.subtitle {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
  font-weight: 400;
  letter-spacing: 0.2px;
}

/* 苹果风格毛玻璃效果样式 */
.apple-glass-title {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(30px);
  border-radius: 12px;
  padding: 8px 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 3px 16px rgba(0, 0, 0, 0.1);
}

.title-container {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.title-icon {
  font-size: 1.6rem;
  animation: icon-float 3s ease-in-out infinite;
}

.title-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.title-badge {
  background: linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%);
  border-radius: 10px;
  padding: 4px 10px;
  backdrop-filter: blur(10px);
}

.badge-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
  letter-spacing: 0.5px;
}

.apple-glass-content {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(40px);
  border-radius: 16px;
  margin: 10px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.function-control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
}

.function-info {
  flex: 1;
}

.function-control-bar .function-title-line {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: nowrap;  /* 禁止换行，强制同一行显示 */
}

.function-control-bar .function-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0;
  color: #1e293b;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
  flex-shrink: 0;  /* 防止标题压缩 */
}

.function-control-bar .function-description {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0;
  white-space: nowrap;
  position: relative;
  padding-left: 12px;
  flex-shrink: 0;  /* 防止描述压缩 */
}

.function-control-bar .function-description::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 1px;
  height: 12px;
  background: rgba(100, 116, 139, 0.3);
}

.apple-glass-select .el-input__wrapper {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(20px);
}

.apple-glass-messages {
  backdrop-filter: blur(10px);
  padding: 14px 18px;
  max-height: 60vh;
  overflow-y: auto;
}

.apple-glass-avatar {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.apple-glass-message {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 10px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(10px);
}

.apple-glass-input {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(30px);
  border-top: 1px solid rgba(255, 255, 255, 0.4);
  padding: 14px 18px;
}

.apple-glass-field .el-input__wrapper {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px 0 0 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(20px);
}

.apple-glass-button {
  background: rgba(0, 122, 255, 0.9) !important;
  border: 1px solid rgba(0, 122, 255, 0.6) !important;
  border-radius: 0 12px 12px 0 !important;
  backdrop-filter: blur(20px);
}

@keyframes icon-float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-5px);
  }
}

.navbar-actions {
  width: 140px;
  display: flex;
  justify-content: flex-end;
}

/* 主布局 */
.main-layout {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
  padding: 0;
}

/* 主内容区主体部分 */
.main-content-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  margin: 0;
  padding: 0;
}



@keyframes sparkle {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

/* 左侧菜单 - 辅助导航 */
.sidebar-nav {
  width: 280px;
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
  z-index: 100;
}

.menu-header {
  padding: 16px 20px 12px;
  border-bottom: 1px solid #f1f5f9;
}

.menu-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
  letter-spacing: -0.2px;
}

.function-menu {
  border: none;
  flex: 1;
  padding: 6px 10px;
  overflow-y: auto;
  max-height: calc(100vh - 180px);
}

.menu-item {
  height: 40px;
  margin: 2px 0;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-weight: 500;
  color: #475569;
  font-size: 0.95rem;
}

.menu-item:hover {
  background: #f1f5f9;
  color: #334155;
  transform: translateX(1px);
}

.menu-item.is-active {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  box-shadow: 0 1px 4px rgba(59, 130, 246, 0.3);
}

/* 右侧内容区域 */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  overflow: hidden;
  height: 100%;
}

/* 功能容器 */
.function-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
  margin: 0;
}

.function-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: none;
  margin: 0 auto;
  width: 100%;
  padding: 0 24px;
}

/* 功能标题区域 */
.function-header {
  padding: 32px 0 24px;
  text-align: center;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 24px;
}

.function-title {
  margin: 0 0 12px 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.5px;
}

.function-description {
  margin: 0;
  font-size: 1.1rem;
  color: #64748b;
  line-height: 1.5;
}

/* 消息容器 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 0 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: calc(100vh - 280px);
  margin-bottom: 0;
}

/* 消息气泡 */
.message-bubble {
  display: flex;
  gap: 12px;
  animation: messageSlideIn 0.3s ease;
  max-width: 85%;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-bubble.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-bubble.assistant {
  align-self: flex-start;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.2rem;
}

.message-bubble.user .message-avatar {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.message-bubble.assistant .message-avatar {
  background: linear-gradient(135deg, #10b981, #059669);
}

.message-content {
  flex: 1;
  max-width: calc(100% - 52px);
}

.message-text {
  background: white;
  padding: 16px 20px;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  line-height: 1.5;
  font-size: 1rem;
  color: #334155;
  word-wrap: break-word;
}

.message-bubble.user .message-text {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-bubble.assistant .message-text {
  border-bottom-left-radius: 4px;
  border: 1px solid #e2e8f0;
}

.message-time {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-top: 6px;
  text-align: right;
}

.message-bubble.user .message-time {
  text-align: left;
}

/* 输入区域 */
.input-container {
  padding: 20px 0 24px;
  background: white;
  border-top: 1px solid #e2e8f0;
  margin-top: auto;
  width: 100%;
}

.input-wrapper {
  display: flex;
  gap: 6px;
  align-items: flex-end;
  width: 100%;
  max-width: none;
  margin: 0 auto;
  padding: 0 24px;
}

.message-input :deep(.el-input-group) {
  display: flex;
  width: 100%;
}

.message-input :deep(.el-input__inner) {
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  font-size: 1rem;
  padding: 12px 20px;
  transition: all 0.2s ease;
  flex: 1;
}

.message-input :deep(.el-input__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.message-input :deep(.el-input-group__append) {
  border-radius: 12px;
  border: 1px solid #3b82f6;
  background: #3b82f6;
  padding: 0 8px;
  overflow: hidden;
  border-left: none;
}

.send-button {
  background: #3b82f6 !important;
  border-color: #3b82f6 !important;
  color: white !important;
  border-radius: 12px !important;
  transition: all 0.2s ease;
  height: 100%;
  padding: 0 24px;
  min-width: 100px;
  font-weight: 600;
  border: none !important;
}

.send-button:hover {
  background: #2563eb !important;
  border-color: #2563eb !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.send-button:active {
  background: #1d4ed8 !important;
  transform: translateY(0);
  box-shadow: none;
}

.model-selector-wrapper {
  display: flex;
  justify-content: center;
}

.model-selector {
  width: 240px;
}

.model-selector :deep(.el-input__inner) {
  border-radius: 8px;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-layout {
    flex-direction: column;
  }
  
  .sidebar-nav {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .function-menu {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 12px;
  }
  
  .menu-item {
    flex: 1;
    min-width: 120px;
    margin: 0;
  }
}

@media (max-width: 768px) {
  .navbar-content {
    padding: 12px 16px;
    height: 70px;
  }
  
  .main-title {
    font-size: 1.8rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .function-title {
    font-size: 1.6rem;
  }
  
  .message-bubble {
    max-width: 95%;
  }
}
</style>