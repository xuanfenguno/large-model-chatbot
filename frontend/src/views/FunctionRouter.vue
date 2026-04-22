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
        
        <!-- AI多功能助手标题 - 居中 -->
        <div class="navbar-title">
          <div class="title-container">
            <div class="title-icon">✨</div>
            <div class="title-content">
              <h1 class="main-title">AI多功能助手</h1>
              <p class="subtitle">12种智能功能，为您提供个性化AI体验</p>
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
          <el-menu-item index="text_summary" class="menu-item">
            <span>文本摘要</span>
          </el-menu-item>
          <el-menu-item index="report_generator" class="menu-item">
            <span>周报生成器</span>
          </el-menu-item>
          <el-menu-item index="travel_planner" class="menu-item">
            <span>旅行计划师</span>
          </el-menu-item>
          <el-menu-item index="translate" class="menu-item">
            <span>翻译</span>
          </el-menu-item>
          <el-menu-item index="programming" class="menu-item">
            <span>编程帮助</span>
          </el-menu-item>
          <el-menu-item index="story" class="menu-item">
            <span>故事创作</span>
          </el-menu-item>
          <el-menu-item index="poetry" class="menu-item">
            <span>诗词创作</span>
          </el-menu-item>
          <el-menu-item index="chengyu" class="menu-item">
            <span>成语接龙</span>
          </el-menu-item>
          <el-menu-item index="role_playing" class="menu-item">
            <span>角色扮演</span>
          </el-menu-item>
          <el-menu-item index="social_media_copywriter" class="menu-item">
            <span>小红书文案</span>
          </el-menu-item>
          <el-menu-item index="visual_idiom_puzzle" class="menu-item">
            <span>看图猜成语</span>
          </el-menu-item>
        </el-menu>
      </aside>
      
      <!-- 右侧内容区域 -->
      <main class="content-area">
        <div class="main-container">
          <!-- 顶部功能栏 - 已移除功能标题 -->
          <div class="top-control-bar">
          </div>
          
          <!-- 聊天区域 -->
          <div class="chat-section">
            <!-- 消息显示区域 -->
            <div class="messages-area" ref="messagesAreaRef">
              <div 
                v-for="(msg, index) in messages" 
                :key="index" 
                :class="['message-item', msg.role]"
              >
                <div class="message-avatar">
                  {{ msg.role === 'user' ? '👤' : '🤖' }}
                </div>
                <div class="message-content">
                  <div class="message-text">
                    {{ msg.content }}
                    <img v-if="msg.image_url" :src="msg.image_url" alt="Image" class="message-image" />
                  </div>
                  <div class="message-time">{{ formatDate(msg.timestamp) }}</div>
                </div>
              </div>
              
              <!-- 空状态 -->
              <div v-if="messages.length === 0" class="empty-state">
                <div class="empty-icon">💬</div>
                <h3>开始对话</h3>
                <p>选择左侧功能，开始与AI助手对话</p>
              </div>
            </div>
            
            <!-- 输入区域 -->
            <div class="input-area">
              <!-- 翻译语言选择器 -->
              <div v-if="activeFunction === 'translate'" class="language-selector">
                <span class="selector-label">目标语言：</span>
                <el-select v-model="targetLanguage" placeholder="选择目标语言" size="default" style="width: 120px">
                  <el-option label="中文" value="中文" />
                  <el-option label="英语" value="英语" />
                  <el-option label="日语" value="日语" />
                  <el-option label="韩语" value="韩语" />
                  <el-option label="法语" value="法语" />
                  <el-option label="德语" value="德语" />
                  <el-option label="西班牙语" value="西班牙语" />
                  <el-option label="俄语" value="俄语" />
                </el-select>
              </div>

              <div class="input-container">
                <div class="input-wrapper">
                  <el-input
                    v-model="inputMessage"
                    :placeholder="getInputPlaceholder(activeFunction)"
                    @keyup.enter="sendMessage"
                    :disabled="loading"
                    size="large"
                    class="message-input"
                    type="textarea"
                    :rows="3"
                    resize="none"
                  >
                    <template #append>
                      <input
                        type="file"
                        accept="image/*"
                        @change="handleImageUpload"
                        :disabled="loading"
                        class="image-upload-input"
                      />
                      <el-button
                        type="text"
                        :icon="Image"
                        @click="() => document.querySelector('.image-upload-input').click()"
                        :disabled="loading"
                        class="image-upload-btn"
                      />
                    </template>
                  </el-input>
                  <el-button 
                    @click="sendMessage" 
                    :loading="loading" 
                    type="primary"
                    size="large"
                    class="send-button"
                  >
                    发送
                  </el-button>
                </div>
                
                <!-- 图片预览区域 -->
                <div v-if="imagePreviewUrl" class="image-preview-wrapper">
                  <img :src="imagePreviewUrl" alt="Preview" class="image-preview" />
                  <el-icon class="remove-image-btn" @click="removeImage"><Close /></el-icon>
                </div>
              </div>
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
import { ElMessage } from 'element-plus';
import { Image, Plus, Close } from '@element-plus/icons-vue';

const router = useRouter();

const activeFunction = ref('auto');
const inputMessage = ref('');
const messages = ref([]);
const loading = ref(false);
const selectedModel = ref('qwen-vl-plus');
const availableModels = ref([]);
const messagesAreaRef = ref(null);
const targetLanguage = ref('中文'); // 新增：翻译目标语言
const selectedImage = ref(null);
const imagePreviewUrl = ref('');

// 处理图片选择
const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      ElMessage.error('不支持的图片格式，请上传 JPG、PNG、GIF 或 WebP 格式的图片');
      return;
    }

    // 验证文件大小（最大10MB）
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过10MB');
      return;
    }

    selectedImage.value = file;
    // 生成预览URL
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreviewUrl.value = e.target.result;
    };
    reader.readAsDataURL(file);

    ElMessage.success('图片已选择');
  }
};

// 移除已选择的图片
const removeImage = () => {
  selectedImage.value = null;
  imagePreviewUrl.value = '';
};

// 上传图片到后端（用于聊天图片识别）
const uploadImage = async (imageFile) => {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);

    const token = localStorage.getItem('token');
    const response = await service.post('/upload-image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      },
      timeout: 30000
    });

    if (response.data && response.data.image_url) {
      return response.data.image_url;
    }

    return null;
  } catch (error) {
    console.error('图片上传失败:', error);
    ElMessage.error('图片上传失败，请稍后重试');
    return null;
  }
};

// 从 localStorage 加载聊天记录
const loadMessagesFromStorage = () => {
  const savedMessages = localStorage.getItem('function-router-messages');
  if (savedMessages) {
    try {
      messages.value = JSON.parse(savedMessages);
      console.log(`从缓存加载了 ${messages.value.length} 条消息`);
    } catch (e) {
      console.error('解析缓存消息失败:', e);
    }
  }
};

// 保存聊天记录到 localStorage
const saveMessagesToStorage = () => {
  try {
    localStorage.setItem('function-router-messages', JSON.stringify(messages.value));
  } catch (e) {
    console.error('缓存消息失败:', e);
  }
};

// 获取可用模型列表
import { service } from '@/utils/request';

const fetchAvailableModels = async () => {
  try {
    const response = await service.get('/models/');
    availableModels.value = response.data.map(model => ({
      value: model.name,
      label: model.label || model.name
    }));
  } catch (error) {
    console.error('获取模型列表失败:', error);
    // 默认模型列表
    availableModels.value = [
      { value: 'qwen-vl-plus', label: 'Qwen VL Plus (支持图片)' },
      { value: 'qwen-vl-max', label: 'Qwen VL Max (支持图片)' },
      { value: 'kimi-large', label: 'Kimi Large' },
      { value: 'qwen-max', label: 'Qwen Max' },
      { value: 'qwen-plus', label: 'Qwen Plus' },
      { value: 'qwen-turbo', label: 'Qwen Turbo' },
    ];
  }
};

onMounted(() => {
  fetchAvailableModels();
  loadMessagesFromStorage(); // 加载缓存的聊天记录
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
  const functionNames = {
    auto: '自动识别',
    text_summary: '文本摘要',
    report_generator: '周报生成器',
    travel_planner: '旅行计划师',
    translate: '翻译',
    programming: '编程帮助',
    story: '故事创作',
    poetry: '诗词创作',
    chengyu: '成语接龙',
    role_playing: '角色扮演',
    social_media_copywriter: '小红书文案',
    visual_idiom_puzzle: '看图猜成语',
  };
  return funcNames[funcType] || '未知功能';
};

// 获取功能描述
const getFunctionDescription = (funcType) => {
  const descriptions = {
    auto: 'AI自动识别您的需求并选择最适合的功能',
    chat: '与AI进行自然对话，获取智能回答',
    story: '生成精彩的故事，激发想象力',
    chengyu: '参与成语接龙游戏，学习传统文化',
    homophone: '找出与给定词语同音但字不同的词',
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
    text_summary: '请粘贴需要总结的文本...',
    report_generator: '请输入本周工作要点，AI将为您生成周报...',
    travel_planner: '请输入目的地、天数和偏好，AI将为您规划行程...',
    translate: '请输入需要翻译的内容...',
    programming: '请输入您遇到的编程问题...',
    story: '请输入故事主题，比如“一个宇航员在火星的奇遇”...',
    poetry: '请输入诗词主题或要求...',
    chengyu: '开始成语接龙...',
    role_playing: '请输入您想让AI扮演的角色和对话场景...',
    social_media_copywriter: '请输入产品或场景关键词，AI将为您生成小红书文案...',
    visual_idiom_puzzle: '输入“开始”，获取第一个看图猜成语挑战！',
  };
  return placeholders[funcType] || '请输入内容...';
};

// 处理功能选择
const handleFunctionSelect = (index) => {
  activeFunction.value = index;
};

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() && !selectedImage.value) return;
  
  let content = inputMessage.value.trim();
  let imageUrl = null;
  
  // 处理图片上传
  if (selectedImage.value) {
    imageUrl = await uploadImage(selectedImage.value);
    if (!imageUrl) {
      return;
    }
  }
  
  // 如果只发送图片没有文字，添加默认提示让AI识别图片
  if (!content && imageUrl) {
    content = '请详细描述这张图片的内容，包括图片中的物体、人物、场景、文字等信息。';
  }
  
  const userMessage = {
    role: 'user',
    content: content,
    image_url: imageUrl,
    timestamp: new Date().toISOString()
  };
  
  messages.value.push(userMessage);
  saveMessagesToStorage(); // 保存聊天记录
  inputMessage.value = '';
  selectedImage.value = null;
  imagePreviewUrl.value = '';
  loading.value = true;
  
  try {
    const payload = {
      input: content,
      model: selectedModel.value,
      function: activeFunction.value
    };

    if (imageUrl) {
      payload.image_url = imageUrl;
    }

    if (activeFunction.value === 'translate') {
      payload.language = targetLanguage.value;
    }

    const response = await service.post('/function-router/', payload);
    
    const aiMessage = {
      role: 'assistant',
      content: response.data.result,
      timestamp: new Date().toISOString()
    };
    
    messages.value.push(aiMessage);
    saveMessagesToStorage(); // 保存聊天记录
  } catch (error) {
    const errorMessage = {
      role: 'assistant',
      content: '很抱歉，请求失败：' + (error.response?.data?.error || error.message),
      timestamp: new Date().toISOString()
    };
    messages.value.push(errorMessage);
    saveMessagesToStorage(); // 保存聊天记录
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

/* 顶部导航栏样式 */
.top-navbar {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 0;
  padding: 0;
  border: none;
  box-shadow: none;
  max-width: none;
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
  background: #ffffff;
  border-radius: 12px;
  padding: 12px 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
  background: #f1f5f9;
  border-radius: 8px;
  padding: 4px 10px;
}

.nav-back-button {
  color: #64748b !important;
  font-size: 1rem;
  font-weight: 500;
  padding: 10px 20px;
  border: 1px solid #cbd5e1 !important;
  border-radius: 8px;
  transition: all 0.3s ease;
  background: #ffffff;
}

.nav-back-button:hover {
  background: #f8fafc !important;
  border-color: #94a3b8;
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

/* 标题样式 */
.apple-glass-title {
  background: #ffffff;
  border-radius: 8px;
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
  background: #ffffff;
  border-radius: 16px;
  margin: 10px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.function-control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
  min-height: 36px;
  max-width: 800px;
  margin: 0 auto;
}

.function-info {
  flex: 1;
}

.function-control-bar .function-title-line {
  display: flex;
  align-items: center;
  gap: 8px;  /* 减小间隔 */
  flex-wrap: nowrap;
  height: 24px;
  line-height: 24px;
  position: relative;  /* 相对定位 */
  left: 0;            /* 明确指定位置 */
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
  letter-spacing: -0.3px;
  line-height: 28px;
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

.model-selector :deep(.el-input__wrapper) {
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

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

/* 新增：翻译语言选择器样式 */
.language-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 0 20px;
}

.selector-label {
  font-size: 0.9rem;
  color: #475569;
  font-weight: 500;
}

:deep(.language-selector .el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
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
  background: #f1f5f9;
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
  padding: 20px 20px 16px;
  border-bottom: 1px solid #f1f5f9;
  border-radius: 16px 16px 0 0;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
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
  padding: 8px 8px;
  overflow-y: auto;
  max-height: calc(100vh - 180px);
  border-radius: 16px;
  background: #fafafa;
}

.menu-item {
  height: 44px;
  margin: 3px 0;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  border: 1px solid transparent;
  color: #475569;
  font-size: 0.95rem;
  padding-left: 8px !important;
}

.menu-item:hover {
  background: #f1f5f9;
  color: #334155;
  transform: translateY(-1px);
  border-color: #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.menu-item.is-active {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
  border-color: #3b82f6;
  transform: translateY(-1px);
}

/* 右侧内容区域 */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: transparent;
  overflow: hidden;
  height: 100%;
  border-radius: 0;
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
  border-radius: 20px;
  background: white;
  margin: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

/* 功能标题区域 */
.function-header {
  padding: 16px 24px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 16px;
  border-radius: 20px 20px 0 0;
  background: linear-gradient(135deg, #f8fafc, #ffffff);
  width: fit-content;  /* 紧凑宽度 */
  float: left;         /* 浮动到左侧 */
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
/* 删除重复的.input-container样式 */

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
  height: 80px !important;
  width: 80px !important;
  font-size: 0.9rem !important;
  font-weight: 600 !important;
  margin-bottom: 8px !important;
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

/* 图片上传样式 */
.image-upload-input {
  display: none;
}

.image-upload-btn {
  position: absolute;
  right: 80px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  color: #606266;
  font-size: 20px;
}

.image-upload-btn:hover {
  color: #409EFF;
}

/* 图片预览样式 */
.image-preview-wrapper {
  display: flex;
  align-items: center;
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 12px;
  position: relative;
  max-width: 100%;
}

.image-preview {
  max-width: 200px;
  max-height: 150px;
  border-radius: 8px;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #909399;
  font-size: 16px;
  transition: all 0.3s ease;
}

.remove-image-btn:hover {
  background: #fff;
  color: #f56c6c;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 消息中的图片显示 */
.message-image {
  max-width: 200px;
  max-height: 150px;
  border-radius: 8px;
  object-fit: cover;
  margin: 8px 0;
}

.user-message .message-image {
  align-self: flex-start;
  margin-left: 12px;
}

.assistant-message .message-image {
  align-self: flex-start;
  margin-right: 12px;
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

/* ===== 新布局样式 ===== */

/* 主容器 */
.main-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  margin: 5px;
  overflow: hidden;
}

/* 顶部控制栏 */
.top-control-bar {
  display: flex;
  justify-content: flex-start;  /* 左对齐 */
  align-items: center;
  padding: 6px 20px;
  background: rgba(248, 250, 252, 0.9);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
  min-height: 44px;
  max-width: 800px;
  margin: 0 auto;
}

.main-container .function-header {
  flex: 0 0 auto;
  min-width: 0;
  text-align: left;
  width: auto;
  float: none;
  display: block;
}

.function-title-line {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 24px;
  max-width: 400px;
  justify-content: flex-start;  /* 左对齐 */
}

.function-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  letter-spacing: -0.3px;
  white-space: nowrap;
  line-height: 24px;
}

.function-separator {
  color: #cbd5e1;
  font-size: 0.8rem;
  font-weight: 300;
  line-height: 24px;
}

.function-description {
  font-size: 0.8rem;
  font-weight: 300;
  color: #64748b;
  margin: 0;
  line-height: 24px;
  white-space: nowrap;
}



/* 聊天区域 */
.chat-section {
  display: flex;
  flex-direction: column;
  flex: 1;
  height: calc(100vh - 180px);
  position: relative; /* 为子元素绝对定位提供参考 */
}

/* 消息区域 */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(100vh - 280px);
  padding-bottom: 80px; /* 为底部输入区域留出空间 */
}

/* 自动识别提示 */
.auto-identify-prompt {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: #64748b;
  padding: 1px 12px;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  margin: -2px 24px 0 24px;
  max-width: fit-content;
}

.auto-identify-title {
  font-weight: 600;
  color: #3b82f6;
}

.auto-identify-separator {
  color: #cbd5e1;
}

.auto-identify-description {
  font-weight: 400;
}

/* 消息项 */
.message-item {
  display: flex;
  gap: 12px;
  animation: messageSlideIn 0.3s ease;
  max-width: 80%;
}

.message-item.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-item.assistant {
  align-self: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.1rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-item.user .message-avatar {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.9), rgba(29, 78, 216, 0.9));
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-color: rgba(59, 130, 246, 0.8);
  color: white;
}

.message-item.assistant .message-avatar {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.9), rgba(5, 150, 105, 0.9));
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-color: rgba(16, 185, 129, 0.8);
  color: white;
}

.message-content {
  flex: 1;
  max-width: calc(100% - 48px);
}

.message-text {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  line-height: 1.5;
  font-size: 0.95rem;
  color: #334155;
  word-wrap: break-word;
}

.message-item.user .message-text {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.9), rgba(29, 78, 216, 0.9));
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: white;
}

.message-item.assistant .message-text {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.message-time {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 4px;
  text-align: right;
}

.message-item.user .message-time {
  text-align: left;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px !important;
  color: #64748b;
  text-align: center;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  margin: 60px !important;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.8;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-state h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #475569;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
}

.empty-state p {
  font-size: 0.9rem;
  margin: 0;
  opacity: 0.8;
}

/* 输入区域 */
.input-area {
  padding: 8px 24px 12px 24px;
  background: rgba(248, 250, 252, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.4);
  position: absolute;  /* 绝对定位 */
  bottom: 0;          /* 固定在底部 */
  left: 0;
  right: 0;
  z-index: 10;        /* 确保在适当层级 */
  width: auto;        /* 自适应宽度 */
  margin: 0 20px 10px 20px;  /* 左右留边距，更明显地靠左 */
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: center; /* 改为center确保在同一水平线 */
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 1px solid rgba(203, 213, 225, 0.8);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.2s ease;
  font-size: 0.95rem;
  line-height: 1.5;
  padding: 12px 16px;
  resize: none;
  min-height: 80px;
  height: 80px;
}

.message-input :deep(.el-textarea__inner):focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.input-container {
  width: 100%;
}

.send-button {
  background: #3b82f6 !important;
  border-color: #3b82f6 !important;
  color: white !important;
  border-radius: 12px !important;
  transition: all 0.2s ease;
  height: 80px !important;
  width: 80px !important;
  font-size: 0.9rem !important;
  font-weight: 600 !important;
  margin-bottom: 0 !important; /* 移除底部边距 */
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

/* 响应式调整 */
@media (max-width: 1024px) {
  .top-control-bar {
    flex-direction: column;
    gap: 16px;
    padding: 20px 24px;
  }
  
  .model-selector-section {
    margin-left: 0;
    width: 100%;
  }
  
  .model-selector {
    width: 100%;
  }
  
  .messages-area {
    padding: 0 24px;
  }
  
  .input-area {
    padding: 16px 24px;
  }
}

@media (max-width: 768px) {
  .main-container {
    margin: 12px;
    border-radius: 12px;
  }
  
  .top-control-bar {
    padding: 16px 20px;
    min-height: auto;
  }
  
  .function-title {
    font-size: 1.5rem;
  }
  
  .function-description {
    font-size: 0.9rem;
  }
  
  .messages-area {
    padding: 0 16px;
  }
  
  .message-item {
    max-width: 90%;
  }
  
  .input-area {
    padding: 12px 16px;
  }
}
</style>