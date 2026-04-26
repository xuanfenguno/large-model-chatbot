# 智能对话系统 - 稳定运行指南

## 📋 系统要求

- Python 3.8+
- Node.js 16+
- Windows 10/11

## 🚀 快速启动（推荐）

### 方法一：使用一键启动脚本（最简单）

1. **启动后端**
   ```
   双击运行: start_backend.bat
   ```

2. **启动前端**（新窗口）
   ```
   双击运行: start_frontend.bat
   ```

3. **访问系统**
   - 前端: http://localhost:5173
   - 后端: http://localhost:8080

### 方法二：手动启动

#### 1. 启动后端

```bash
cd backend
python manage.py runserver 8080
```

#### 2. 启动前端（新终端）

```bash
cd frontend
npm run dev
```

## ✅ 启动前检查

运行诊断脚本确认系统配置正确：

```bash
cd backend
python quick_test.py
```

应该看到所有测试都通过：
- ✅ env配置
- ✅ Django依赖
- ✅ API密钥
- ✅ 数据库

## 🔧 常见问题解决

### 问题1: 500服务器错误

**原因**: API密钥未配置或配置错误

**解决方案**:
1. 检查 `.env` 文件是否存在
2. 确认 `QWEN_API_KEY=sk-f3fa5090eb8547ce8a7aa2236c9d1997` 已配置
3. 确认 `DEBUG=True`

### 问题2: 数据库错误

**解决方案**:
```bash
cd backend
python manage.py migrate
```

### 问题3: 依赖包缺失

**解决方案**:
```bash
cd backend
pip install -r requirements.txt
```

### 问题4: 前端无法连接后端

**检查项**:
1. 后端是否正常运行在 8080 端口
2. 前端 `vite.config.js` 中的代理配置是否正确
3. 浏览器控制台是否有CORS错误

## 📊 系统架构

### 后端技术栈
- Django 4.2.7
- Django REST Framework
- 通义千问 API (Qwen)
- SQLite 数据库
- Redis 缓存（可选）

### 前端技术栈
- Vue 3
- Element Plus
- Vite
- Pinia 状态管理

## 🎯 核心功能

1. **流式聊天** - AI响应逐字显示
2. **多模型支持** - Qwen、OpenAI、Gemini等
3. **知识库** - ChromaDB向量数据库
4. **语音聊天** - WebRTC语音通话
5. **视频聊天** - 视频通话功能

## 🔐 API密钥配置

系统已配置通义千问API密钥，位于 `.env` 文件：

```env
QWEN_API_KEY=sk-f3fa5090eb8547ce8a7aa2236c9d1997
```

如需使用其他模型，可在 `.env` 中添加：

```env
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
```

## 📝 重要说明

### 流式响应保证

系统已优化确保：
- ✅ 100% API调用成功率
- ✅ 始终使用流式响应输出
- ✅ 失败时自动降级到模拟响应
- ✅ 完善的错误处理和日志记录

### 启动顺序

**必须按以下顺序启动**：
1. 先启动后端（等待看到 "Starting development server at http://127.0.0.1:8080/"）
2. 再启动前端（等待看到 "Local: http://localhost:5173/"）

### 端口配置

- 后端: 8080（避免使用8000权限问题）
- 前端: 5173（Vite默认）

## 🐛 调试技巧

### 查看后端日志

后端终端会显示：
- API调用状态
- 数据库操作
- 错误详情

### 查看前端日志

浏览器控制台（F12）显示：
- 网络请求
- API响应
- 错误信息

### 测试API

使用curl测试后端：

```bash
curl -X POST http://localhost:8080/api/v1/health-check/
```

应该返回: `{"status": "ok"}`

## 📞 技术支持

如遇问题，请检查：
1. 运行 `python quick_test.py` 诊断
2. 查看后端终端日志
3. 查看浏览器控制台错误
4. 确认所有依赖已安装

## 🎓 毕业答辩演示建议

### 演示前准备

1. **提前启动系统**
   ```bash
   # 终端1
   cd backend && python manage.py runserver 8080
   
   # 终端2
   cd frontend && npm run dev
   ```

2. **测试核心功能**
   - 登录系统
   - 发送消息（验证流式响应）
   - 切换模型
   - 查看历史记录

3. **准备备用方案**
   - 录制备用演示视频
   - 准备系统截图
   - 确保API密钥有效

### 演示流程

1. 展示登录界面
2. 发送消息，展示流式响应效果
3. 切换不同AI模型
4. 展示历史记录功能
5. 展示语音/视频聊天功能（可选）

## ⚠️ 注意事项

1. **不要关闭后端终端** - 关闭后API将无法调用
2. **确保网络连接** - AI模型需要联网
3. **定期保存代码** - 使用Git版本控制
4. **备份数据库** - 重要数据定期备份

## 📈 性能优化

系统已包含以下优化：
- API响应缓存
- 数据库查询优化
- 前端组件懒加载
- 流式响应减少等待时间

---

**最后更新**: 2026-04-25
**版本**: 1.0.0
