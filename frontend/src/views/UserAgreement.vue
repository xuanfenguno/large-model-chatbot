<template>
  <div class="agreement-container">
    <div class="agreement-header">
      <el-button type="primary" text @click="goBack" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1 class="agreement-title">用户协议</h1>
    </div>
    
    <div class="agreement-content">
      <div class="agreement-card">
        <div class="agreement-section">
          <h2>1. 协议范围</h2>
          <p>本协议是您与AI聊天机器人服务提供方之间就使用AI聊天服务所订立的协议。</p>
        </div>
        
        <div class="agreement-section">
          <h2>2. 服务内容</h2>
          <p>我们提供基于人工智能的聊天对话服务，包括但不限于：</p>
          <ul>
            <li>智能问答服务</li>
            <li>文本生成服务</li>
            <li>信息查询服务</li>
            <li>其他相关AI服务</li>
          </ul>
        </div>
        
        <div class="agreement-section">
          <h2>3. 用户权利与义务</h2>
          <h3>3.1 用户权利</h3>
          <ul>
            <li>使用本服务提供的各项功能</li>
            <li>获取及时、准确的服务响应</li>
            <li>对服务提出意见和建议</li>
          </ul>
          
          <h3>3.2 用户义务</h3>
          <ul>
            <li>遵守国家法律法规</li>
            <li>不发布违法、违规内容</li>
            <li>妥善保管账户信息</li>
            <li>不进行恶意攻击行为</li>
          </ul>
        </div>
        
        <div class="agreement-section">
          <h2>4. 服务使用规则</h2>
          <p>用户在使用本服务时，不得：</p>
          <ul>
            <li>发布违反法律法规的内容</li>
            <li>侵犯他人知识产权</li>
            <li>进行商业性广告宣传</li>
            <li>干扰服务正常运行</li>
            <li>其他不当使用行为</li>
          </ul>
        </div>
        
        <div class="agreement-section">
          <h2>5. 免责声明</h2>
          <p>5.1 本服务基于人工智能技术，生成内容可能存在不准确或错误的情况，用户应自行判断内容的准确性。</p>
          <p>5.2 因不可抗力、网络问题等导致的服务中断，我们不承担相应责任。</p>
          <p>5.3 用户因使用本服务产生的任何损失，我们概不负责。</p>
        </div>
        
        <div class="agreement-section">
          <h2>6. 协议修改</h2>
          <p>我们有权根据需要修改本协议，修改后的协议将在网站公布后生效。</p>
        </div>
        
        <div class="agreement-section">
          <h2>7. 法律适用</h2>
          <p>本协议的订立、执行和解释均适用中华人民共和国法律。</p>
        </div>
        
        <div class="agreement-footer">
          <p class="update-time">最后更新日期：2025年1月16日</p>
          <el-button type="primary" @click="goBack" class="agree-btn">
            我已阅读并同意
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
.agreement-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.agreement-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.back-btn {
  color: white !important;
  margin-right: 20px;
}

.agreement-title {
  color: white;
  font-size: 28px;
  font-weight: 600;
  margin: 0;
}

.agreement-content {
  display: flex;
  justify-content: center;
}

.agreement-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  max-width: 800px;
  width: 100%;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.agreement-section {
  margin-bottom: 30px;
}

.agreement-section h2 {
  color: #303133;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 15px;
  border-left: 4px solid #409eff;
  padding-left: 12px;
}

.agreement-section h3 {
  color: #606266;
  font-size: 16px;
  font-weight: 500;
  margin: 15px 0 10px 0;
}

.agreement-section p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 10px;
}

.agreement-section ul {
  color: #606266;
  line-height: 1.6;
  margin-left: 20px;
}

.agreement-section li {
  margin-bottom: 8px;
}

.agreement-footer {
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
  .agreement-card {
    padding: 20px;
    margin: 0 10px;
  }
  
  .agreement-title {
    font-size: 24px;
  }
}
</style>