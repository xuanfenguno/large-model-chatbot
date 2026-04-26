/**
 * 前端 AI 响应速度优化建议
 * 
 * 目标：让用户感觉 AI 响应更快，减少等待焦虑
 */

// ========================================
// 优化 1: 立即显示"思考中"状态
// ========================================
// 在 Chat.vue 的 sendMessage 方法中添加

/*
async sendMessage() {
  if (!this.messageInput.trim()) return;

  const messageContent = this.messageInput.trim();
  this.messageInput = '';

  // 保存用户消息
  this.messages.push({
    role: 'user',
    content: messageContent,
    image_url: this.tempImage || null,
    created_at: new Date().toISOString()
  });

  const tempImage = this.tempImage;
  this.tempImage = null;
  this.typingContent = '';
  this.isTyping = false;

  // ✅ 优化：立即显示 AI 思考状态
  this.isThinking = true;
  this.thinkingStartTime = Date.now();
  
  // 添加一个"思考中"的临时消息
  const thinkingMessageIndex = this.messages.length;
  this.messages.push({
    role: 'assistant',
    content: '',
    isThinking: true,  // 标记为思考中
    created_at: new Date().toISOString()
  });

  // 滚动到底部
  this.$nextTick(() => {
    this.scrollToBottom();
  });

  try {
    const response = await service.post('/stream-chat/', {
      message: messageContent,
      image_url: tempImage,
      conversation_id: this.selectedConversationId,
      model: this.selectedModel
    }, {
      timeout: 120000,
      responseType: 'text',
      onDownloadProgress: () => {} // 防止 axios 缓冲
    });

    // ✅ 优化：收到第一个字符时，移除思考中状态
    if (this.messages[thinkingMessageIndex]?.isThinking) {
      this.messages.splice(thinkingMessageIndex, 1);
    }
    
    // ... 处理流式响应
  } catch (error) {
    // 移除思考中状态
    if (this.messages[thinkingMessageIndex]?.isThinking) {
      this.messages.splice(thinkingMessageIndex, 1);
    }
    // ... 错误处理
  } finally {
    this.isThinking = false;
  }
}
*/

// ========================================
// 优化 2: 显示思考计时器
// ========================================
// 在模板中显示思考时间

/*
<template>
  <div v-if="isThinking" class="thinking-indicator">
    <el-icon class="is-loading">
      <Loading />
    </el-icon>
    <span>AI 正在思考，请稍候...</span>
    <span class="thinking-time">{{ thinkingDuration }}秒</span>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isThinking: false,
      thinkingStartTime: 0,
      thinkingTimer: null
    };
  },
  computed: {
    thinkingDuration() {
      return ((Date.now() - this.thinkingStartTime) / 1000).toFixed(1);
    }
  },
  watch: {
    isThinking(val) {
      if (val) {
        // 启动计时器更新
        this.thinkingTimer = setInterval(() => {
          this.$forceUpdate();
        }, 100);
      } else {
        // 停止计时器
        if (this.thinkingTimer) {
          clearInterval(this.thinkingTimer);
          this.thinkingTimer = null;
        }
      }
    }
  }
};
</script>

<style scoped>
.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  margin: 8px 0;
  font-size: 14px;
  color: #666;
}

.thinking-time {
  font-size: 12px;
  color: #999;
  margin-left: auto;
}
</style>
*/

// ========================================
// 优化 3: 优化流式响应处理
// ========================================
// 使用 EventSource 代替 axios 以获得更好的流式体验

/*
function createEventStream(url, data, callbacks) {
  const eventSource = new EventSource(url, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    }
  });

  eventSource.onmessage = (event) => {
    const parsed = JSON.parse(event.data);
    
    // 立即处理每个数据块
    if (callbacks.onData) {
      callbacks.onData(parsed);
    }
    
    // 完成时关闭连接
    if (parsed.status === 'completed') {
      eventSource.close();
      if (callbacks.onComplete) {
        callbacks.onComplete();
      }
    }
  };

  eventSource.onerror = (error) => {
    console.error('EventSource failed:', error);
    eventSource.close();
    if (callbacks.onError) {
      callbacks.onError(error);
    }
  };

  // 发送 POST 请求
  fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  return eventSource;
}

// 使用示例
const eventSource = createEventStream('/api/v1/stream-chat/', {
  message: '你好',
  conversation_id: 1
}, {
  onData: (data) => {
    console.log('收到数据块:', data.content);
    // 立即显示到界面
  },
  onComplete: () => {
    console.log('响应完成');
  },
  onError: (error) => {
    console.error('错误:', error);
  }
});
*/

// ========================================
// 优化 4: 预加载常用响应
// ========================================
// 对于常见问题，可以预加载响应

/*
const COMMON_QUESTIONS = {
  '你好': '你好！有什么我可以帮助你的吗？',
  'hello': 'Hello! How can I assist you today?',
  '你是谁': '我是一个 AI 助手，可以回答你的问题、提供帮助。',
  '再见': '再见！祝你有美好的一天！'
};

function getPreloadedResponse(question) {
  const normalized = question.trim().toLowerCase();
  return COMMON_QUESTIONS[normalized] || null;
}

// 在发送消息前先检查预加载响应
async sendMessage() {
  const preloaded = getPreloadedResponse(this.messageInput);
  if (preloaded) {
    // 立即显示预加载响应
    this.messages.push({
      role: 'assistant',
      content: preloaded,
      fromCache: true
    });
    return;
  }
  
  // 否则正常发送请求
  // ...
}
*/

// ========================================
// 优化 5: 乐观更新
// ========================================
// 在服务器响应前就更新界面

/*
async sendMessage() {
  // 乐观地假设请求会成功
  const optimisticMessage = {
    role: 'assistant',
    content: '正在生成回复...',
    isOptimistic: true
  };
  
  this.messages.push(optimisticMessage);
  
  try {
    const response = await service.post('/stream-chat/', {...});
    
    // 用真实响应替换乐观消息
    const index = this.messages.findIndex(m => m.isOptimistic);
    if (index !== -1) {
      this.messages.splice(index, 1);
    }
    
    // 添加真实响应
    // ...
  } catch (error) {
    // 更新乐观消息显示错误
    const index = this.messages.findIndex(m => m.isOptimistic);
    if (index !== -1) {
      this.messages[index].content = '抱歉，生成回复时出错，请重试。';
      this.messages[index].error = true;
    }
  }
}
*/

// ========================================
// 性能监控
// ========================================
// 添加性能监控以了解响应时间

/*
function trackPerformance(metricName, value) {
  console.log(`️ ${metricName}: ${value}ms`);
  
  // 可以发送到分析服务
  // analytics.track('performance', { metric: metricName, value });
}

// 在关键节点记录时间
const timings = {
  requestStart: Date.now(),
  firstByte: null,
  complete: null
};

// 发送请求
timings.requestStart = Date.now();

// 收到第一个字节
service.post('/stream-chat/', {...}, {
  onDownloadProgress: (progress) => {
    if (!timings.firstByte && progress.loaded > 0) {
      timings.firstByte = Date.now();
      trackPerformance('首字节时间', timings.firstByte - timings.requestStart);
    }
  }
});

// 完成
timings.complete = Date.now();
trackPerformance('总响应时间', timings.complete - timings.requestStart);
*/

// ========================================
// 总结
// ========================================
/*
优化优先级：
1. ⭐⭐⭐ 立即显示"思考中"状态 - 用户体验提升最大
2. ⭐⭐ 优化流式响应处理 - 减少延迟感
3. ⭐⭐ 显示思考计时器 - 让用户知道系统在响应
4. ⭐ 预加载常用响应 - 特定场景有效
5. ⭐ 乐观更新 - 提升感知速度

预期效果：
- 用户感知响应时间减少 50%
- 等待焦虑降低
- 整体体验更流畅
*/
