# Vue.js 项目目录结构指南

## assets 目录
存放静态资源文件，主要包括：

### 图片资源
- `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg` 等图片文件
- 通常分为子目录管理，如 `images/`, `icons/`, `logos/`

### 字体文件
- `.woff`, `.woff2`, `.ttf`, `.otf` 等字体文件

### 样式文件
- 全局样式文件
- CSS 变量定义
- 主题相关的样式文件

### 示例结构
```
assets/
├── images/
│   ├── icons/
│   ├── logos/
│   └── backgrounds/
├── fonts/
└── styles/
    ├── global.css
    └── variables.css
```

## components 目录
存放可复用的 Vue 组件，主要包括：

### 基础组件
- 按钮(Button)、输入框(Input)、卡片(Card)等UI基础组件
- 表单组件(Form elements)
- 导航组件(Navigation)

### 业务组件
- 与具体业务逻辑相关的复合组件
- 页面特定的可复用组件

### 通用组件
- 模态框(Modal)
- 加载指示器(Loading)
- 提示消息组件(Toast/Alert)

### 示例结构
```
components/
├── ui/                 # 通用UI组件
│   ├── Button.vue
│   ├── Input.vue
│   └── Card.vue
├── forms/              # 表单相关组件
│   ├── FormInput.vue
│   └── FormSelect.vue
└── business/           # 业务组件
    ├── UserCard.vue
    └── ChatMessage.vue
```

## composables 目录
存放 Vue 3 的组合式函数(Composition Functions)，主要包括：

### 数据获取相关
- API 请求函数
- 数据处理逻辑

### 状态管理
- 可复用的状态逻辑
- 跨组件共享的状态

### 工具函数
- 日期处理
- 字符串处理
- 数字格式化

### 业务逻辑
- 认证相关逻辑
- 用户权限检查
- 购物车逻辑等

### 示例结构
```
composables/
├── api/
│   ├── useUserApi.js
│   └── useChatApi.js
├── auth/
│   └── useAuth.js
├── utils/
│   ├── useDate.js
│   └── useValidation.js
└── state/
    └── useGlobalState.js
```

## 当前项目结构分析
当前项目结构如下：
```
src/
├── App.vue
├── main.js
├── style.css
├── router/
│   └── index.js
├── stores/             # Pinia 状态管理
│   ├── auth.js
│   └── chat.js
├── utils/              # 工具函数
│   └── request.js
└── views/              # 页面视图组件
    ├── Chat.vue
    ├── Home.vue
    ├── Login.vue
    └── Register.vue
```

## 建议的目录结构调整
为了更好地组织代码，建议添加以下目录：

```
src/
├── assets/             # 静态资源
├── components/         # 可复用组件
├── composables/        # 组合式函数
├── views/              # 页面视图
├── stores/             # 状态管理
├── router/             # 路由配置
├── utils/              # 工具函数
├── App.vue
├── main.js
└── style.css
```

这样的结构有助于：
- 更好的代码组织和维护
- 团队协作效率提升
- 代码复用性增强
- 项目可扩展性提高