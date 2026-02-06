#!/bin/bash

# 确保在正确的目录下
cd "$(dirname "$0")"

# 设置Django环境变量
export DJANGO_SETTINGS_MODULE="config.settings"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误：Python 3 未安装"
    exit 1
fi

# 安装依赖
echo "正在检查并安装依赖..."
pip install -r requirements.txt

# 收集静态文件（如果需要）
# python manage.py collectstatic --noinput

# 创建数据库迁移文件
echo "正在创建数据库迁移文件..."
python manage.py makemigrations

# 应用数据库迁移
echo "正在应用数据库迁移..."
python manage.py migrate

# 创建超级用户
echo "正在创建超级用户..."
python manage.py createsuperuser --username admin --email admin@example.com --noinput

# 设置超级用户密码
echo "from django.contrib.auth.models import User; u = User.objects.get(username='admin'); u.set_password('admin123'); u.save(); print('超级用户密码设置成功')" | python manage.py shell

echo "数据库设置完成！"
echo "用户名：admin"
echo "密码：admin123"
echo "管理后台地址：http://localhost:8000/admin/"

# 启动开发服务器
echo "启动开发服务器..."
python manage.py runserver