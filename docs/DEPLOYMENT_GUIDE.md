# AI聊天机器人部署指南

## 环境要求

- Python 3.8+
- Node.js 16+ (仅前端开发)
- MySQL 5.7+ 或 PostgreSQL 12+ (推荐生产环境)
- Redis (可选，用于缓存和会话存储)
- Docker & Docker Compose (推荐)

## 本地开发部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd chat
```

### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 3. 数据库迁移

```bash
# 应用数据库迁移
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser
```

### 4. 启动后端服务

```bash
python manage.py runserver 8000
```

### 5. 前端设置（如果需要）

```bash
# 在另一个终端窗口中
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 生产环境部署

### 使用Docker部署（推荐）

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: aichat_db
      MYSQL_USER: aichat_user
      MYSQL_PASSWORD: secure_password
      MYSQL_ROOT_PASSWORD: root_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=mysql://aichat_user:secure_password@db:3306/aichat_db
      - REDIS_URL=redis://redis:6379/0
      - DJANGO_SETTINGS_MODULE=config.settings.production
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"
    volumes:
      - media_data:/app/media
      - static_data:/app/static

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_data:/app/static
      - media_data:/app/media
    depends_on:
      - backend

volumes:
  mysql_data:
  media_data:
  static_data:
```

### 传统部署步骤

#### 1. 服务器准备

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx supervisor git mysql-server redis-server
```

#### 2. 配置数据库

```sql
-- 登录MySQL
mysql -u root -p

-- 创建数据库和用户
CREATE DATABASE aichat_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'aichat_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON aichat_db.* TO 'aichat_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. 部署应用

```bash
# 克隆代码
git clone <repository-url>
cd chat/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装生产级WSGI服务器
pip install gunicorn

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件，配置生产环境参数
```

#### 4. 配置Django

```bash
# 收集静态文件
python manage.py collectstatic --noinput

# 应用数据库迁移
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser
```

#### 5. 配置Gunicorn

创建 `gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

#### 6. 配置Supervisor

创建 `/etc/supervisor/conf.d/aichat.conf`:

```ini
[program:aichat]
command=/path/to/your/venv/bin/gunicorn config.wsgi:application -c gunicorn.conf.py
directory=/path/to/your/project/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/aichat.log
environment=DJANGO_SETTINGS_MODULE="config.settings.production"
```

#### 7. 配置Nginx

创建 `/etc/nginx/sites-available/aichat`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/your/project/backend/static/;
        expires 30d;
    }

    location /media/ {
        alias /path/to/your/project/backend/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/aichat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 8. 启动服务

```bash
# 重启Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start aichat

# 重启Nginx
sudo systemctl reload nginx
```

## 环境变量配置

以下是必需的环境变量：

```bash
# Django设置
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False  # 生产环境中设为False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 数据库配置
DATABASE_URL=mysql://user:password@host:port/database_name

# Redis配置（可选）
REDIS_URL=redis://localhost:6379/0

# AI API配置
OPENAI_API_KEY=your-openai-api-key
GOOGLE_GEMINI_API_KEY=your-google-gemini-api-key
MOONSHOT_API_KEY=your-moonshot-api-key
QWEN_API_KEY=your-qwen-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key

# 微信OAuth配置
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret
```

## SSL证书配置

使用Let's Encrypt配置SSL：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 监控和日志

### 日志配置

应用日志位于：
- `/var/log/aichat.log` (应用日志)
- `/var/log/nginx/access.log` (访问日志)
- `/var/log/nginx/error.log` (错误日志)

### 性能监控

系统会自动监控：
- API响应时间
- 数据库查询次数
- CPU和内存使用率
- 慢查询检测

## 备份策略

### 数据库备份

```bash
# 备份数据库
mysqldump -u aichat_user -p aichat_db > backup_$(date +%F).sql

# 自动备份脚本 (crontab)
0 2 * * * /usr/bin/mysqldump -u aichat_user -p'password' aichat_db > /backup/aichat_$(date +\%Y\%m\%d).sql
```

### 媒体文件备份

定期备份上传的媒体文件到云存储或远程服务器。

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证数据库凭据是否正确

2. **API密钥无效**
   - 检查环境变量是否正确设置
   - 确认API提供商账户状态

3. **性能问题**
   - 检查数据库索引
   - 监控慢查询日志
   - 考虑增加缓存

### 调试命令

```bash
# 检查应用状态
sudo supervisorctl status aichat

# 查看应用日志
sudo tail -f /var/log/aichat.log

# 检查Nginx状态
sudo systemctl status nginx

# 检查数据库连接
python manage.py dbshell
```

## 更新和维护

### 代码更新

```bash
# 停止服务
sudo supervisorctl stop aichat

# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 应用数据库迁移
python manage.py migrate

# 重启服务
sudo supervisorctl start aichat
```

### 安全更新

定期更新系统和依赖包：
- `pip install --upgrade pip setuptools`
- `pip install -r requirements.txt --upgrade`
- 定期更新操作系统安全补丁