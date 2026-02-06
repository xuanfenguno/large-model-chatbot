# 后端目录结构说明

## 目录结构

```
backend/
├── chatbot/                 # 核心应用模块
│   ├── __init__.py
│   ├── api_base.py          # API基类
│   ├── consumers.py         # WebSocket消费者
│   ├── enhanced_api.py      # 增强API功能
│   ├── function_router.py   # 功能路由
│   ├── knowledge_base_views.py # 知识库视图
│   ├── middleware.py        # 中间件
│   ├── models.py           # 数据模型
│   ├── security_config.py  # 安全配置
│   ├── serializers.py      # 序列化器
│   ├── tasks.py            # 异步任务
│   ├── urls.py             # URL路由
│   ├── views.py            # 视图函数
│   ├── voice_views.py      # 语音相关视图
│   ├── management/         # Django管理命令
│   ├── middleware/         # 自定义中间件
│   ├── migrations/         # 数据库迁移文件
│   └── utils/              # 工具函数
├── config/                 # 项目配置
│   ├── __init__.py
│   ├── asgi.py
│   ├── cache_config.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── middleware/             # 全局中间件
│   └── cache_middleware.py
├── scripts/                # 脚本文件
│   ├── __init__.py
│   ├── clear_blacklist.py  # 清除黑名单脚本
│   ├── fix_userprofiles.py # 修复用户资料脚本
│   ├── make_migrations.sh  # 创建迁移脚本
│   ├── optimized_server.py # 优化服务器脚本
│   ├── start_lightweight.py # 轻量级启动脚本
│   ├── start_memory_optimized.py # 内存优化启动脚本
│   └── start_optimized.py  # 优化启动脚本
├── tests/                  # 测试文件
│   ├── __init__.py
│   ├── performance_test.py # 性能测试
│   └── tests.py            # 单元测试
├── chroma_data/            # Chroma数据库数据
├── .env.example           # 环境变量示例
├── .gitignore             # Git忽略文件
└── requirements.txt       # 依赖包列表
```

## 主要模块说明

### chatbot/
- 核心业务逻辑
- 包含功能路由、API调用、视图处理等功能

### config/
- Django项目配置
- 包含设置、URL配置等

### scripts/
- 存放各种脚本文件
- 包括启动脚本、维护脚本等

### tests/
- 存放测试文件
- 包括单元测试、性能测试等

### middleware/
- 存放自定义中间件

### management/
- Django管理命令

### utils/
- 实用工具函数

## 文件命名规范

- Python文件：使用snake_case命名法
- 类名：使用PascalCase命名法
- 函数名：使用snake_case命名法
- 变量名：使用snake_case命名法