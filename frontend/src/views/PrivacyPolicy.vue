<template>
  <div class="privacy-container">
    <div class="privacy-header">
      <el-button type="primary" text @click="goBack" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1 class="privacy-title">隐私政策</h1>
    </div>
    
    <div class="privacy-content">
      <div class="privacy-card">
        <div class="privacy-section">
          <h2>1. 信息收集</h2>
          <p>我们收集的信息包括：</p>
          <ul>
            <li><strong>账户信息：</strong>用户名、邮箱地址</li>
            <li><strong>使用数据：</strong>聊天记录、交互数据</li>
            <li><strong>设备信息：</strong>IP地址、浏览器类型</li>
            <li><strong>技术信息：</strong>Cookies、日志文件</li>
          </ul>
        </div>
        
        <div class="privacy-section">
          <h2>2. 信息使用</h2>
          <p>我们使用收集的信息用于：</p>
          <ul>
            <li>提供和改进AI聊天服务</li>
            <li>个性化用户体验</li>
            <li>确保服务安全运行</li>
            <li>遵守法律法规要求</li>
            <li>与用户进行必要沟通</li>
          </ul>
        </div>
        
        <div class="privacy-section">
          <h2>3. 信息共享</h2>
          <p>我们承诺不会将您的个人信息出售给第三方。在以下情况下，我们可能会共享信息：</p>
          <ul>
            <li>获得您明确同意</li>
            <li>为遵守法律要求</li>
            <li>保护我们的合法权益</li>
            <li>与服务提供商合作（需签订保密协议）</li>
          </ul>
        </div>
        
        <div class="privacy-section">
          <h2>4. 数据安全</h2>
          <p>我们采取合理的安全措施保护您的信息：</p>
          <ul>
            <li>数据传输使用SSL加密</li>
            <li>定期进行安全审计</li>
            <li>访问权限控制</li>
            <li>数据备份和恢复机制</li>
          </ul>
        </div>
        
        <div class="privacy-section">
          <h2>5. 数据保留</h2>
          <p>我们仅在实现本政策所述目的所必需的时间内保留您的个人信息：</p>
          <ul>
            <li>账户信息：账户存续期间</li>
            <li>聊天记录：根据用户设置保留</li>
            <li>日志文件：最长保留6个月</li>
          </ul>
        </div>
        
        <div class="privacy-section">
          <h2>6. 用户权利</h2>
          <p>您对自己的个人信息享有以下权利：</p>
          <ul>
            <li><strong>访问权：</strong>查看我们持有的您的个人信息</li>
            <li><strong>更正权：</strong>更正不准确的个人信息</li>
            <li><strong>删除权：</strong>要求删除您的个人信息</li>
            <li><strong>限制处理权：</strong>限制我们处理您的信息</li>
            <li><strong>数据携带权：</strong>获取您的个人信息副本</li>
          </ul>
        </div>
        
        <div class="privacy-section">
          <h2>7. Cookies使用</h2>
          <p>我们使用Cookies来：</p>
          <ul>
            <li>记住您的登录状态</li>
            <li>分析服务使用情况</li>
            <li>个性化内容展示</li>
          </ul>
          <p>您可以通过浏览器设置管理Cookies。</p>
        </div>
        
        <div class="privacy-section">
          <h2>8. 未成年人保护</h2>
          <p>我们非常重视未成年人的个人信息保护：</p>
          <ul>
            <li>不建议未成年人使用本服务</li>
            <li>如发现未成年人使用，将采取保护措施</li>
            <li>监护人可联系我们对相关信息进行处理</li>
          </ul>
        </div>
        
        <div class="privacy-section">
          <h2>9. 政策更新</h2>
          <p>我们可能会不时更新本隐私政策。更新后的政策将在网站上公布。</p>
        </div>
        
        <div class="privacy-section">
          <h2>10. 联系我们</h2>
          <p>如您对本隐私政策有任何疑问，请联系我们：</p>
          <ul>
            <li>邮箱：privacy@example.com</li>
            <li>电话：400-123-4567</li>
          </ul>
        </div>
        
        <div class="privacy-footer">
          <p class="update-time">最后更新日期：2025年1月16日</p>
          <el-button type="primary" @click="goBack" class="agree-btn">
            我已阅读并理解
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.privacy-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.privacy-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.back-btn {
  color: white !important;
  margin-right: 20px;
}

.privacy-title {
  color: white;
  font-size: 28px;
  font-weight: 600;
  margin: 0;
}

.privacy-content {
  display: flex;
  justify-content: center;
}

.privacy-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  max-width: 800px;
  width: 100%;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.privacy-section {
  margin-bottom: 30px;
}

.privacy-section h2 {
  color: #303133;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 15px;
  border-left: 4px solid #67c23a;
  padding-left: 12px;
}

.privacy-section p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 10px;
}

.privacy-section ul {
  color: #606266;
  line-height: 1.6;
  margin-left: 20px;
}

.privacy-section li {
  margin-bottom: 8px;
}

.privacy-section strong {
  color: #303133;
}

.privacy-footer {
  text-align: center;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #e4e7ed;
}

.update-time {
  color: #909399;
  font-size: 14px;
  margin-bottom: 20px;
}

.agree-btn {
  width: 200px;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .privacy-card {
    padding: 20px;
    margin: 0 10px;
  }
  
  .privacy-title {
    font-size: 24px;
  }
}
</style>