# Docker 部署指南

## 项目结构

```
chat/
├── backend/          # Django 后端
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/         # Vue 前端
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── .env.example
```

## 前置要求

- Docker 已安装
- Docker Compose 已安装

## 快速开始

### 1. 配置环境变量

复制 `.env.example` 到 `.env` 并填写必要的配置：

```bash
cp .env.example .env
```

### 2. 构建并启动容器

在项目根目录执行：

```bash
docker-compose up --build
```

### 3. 访问应用

- 前端: http://localhost:80
- 后端 API: http://localhost:8080/api

## 常用命令

### 启动容器

```bash
docker-compose up -d
```

### 查看日志

```bash
# 所有服务日志
docker-compose logs -f

# 单个服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 停止容器

```bash
docker-compose down
```

### 重启容器

```bash
docker-compose restart
```

### 重新构建

```bash
docker-compose up --build
```

## 单独构建镜像

### 后端镜像

```bash
cd backend
docker build -t chat-backend .
```

### 前端镜像

```bash
cd frontend
docker build -t chat-frontend .
```

## 数据持久化

Docker Compose 配置了以下卷：

- `backend_static`: 静态文件
- `backend_media`: 媒体文件
- `redis_data`: Redis 数据

## 生产环境部署

1. 设置 `DEBUG=False`
2. 配置安全的 `DJANGO_SECRET_KEY`
3. 更新 `ALLOWED_HOSTS`
4. 使用生产级数据库（如 PostgreSQL）
5. 配置 HTTPS/SSL
6. 设置适当的环境变量

## 故障排除

### 端口冲突

如果端口已被占用，修改 `docker-compose.yml` 中的端口映射。

### 权限问题

确保 Docker 有权限访问项目目录。

### 依赖问题

重新构建镜像：

```bash
docker-compose down -v
docker-compose up --build
```
