#!/usr/bin/env python
"""
检查系统状态和可能的错误
"""

import os
import sys
import traceback
from django.core.management import execute_from_command_line
from django.conf import settings

# 添加后端目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    django.setup()
    
    # 尝试导入可能导致错误的模块
    from chatbot.views import upload_avatar
    from django.contrib.auth.models import User
    from chatbot.models import UserProfile
    
    print("✓ Django 配置正常")
    print("✓ 关键模块导入正常")
    
    # 检查媒体目录权限
    import stat
    media_dir = os.path.join(settings.BASE_DIR, 'media')
    if os.path.exists(media_dir):
        print(f"✓ 媒体目录存在: {media_dir}")
    else:
        print(f"✗ 媒体目录不存在: {media_dir}")
    
    # 检查 avatars 目录
    avatars_dir = os.path.join(media_dir, 'avatars')
    if os.path.exists(avatars_dir):
        print(f"✓ 头像目录存在: {avatars_dir}")
    else:
        print(f"✗ 头像目录不存在: {avatars_dir}")
        os.makedirs(avatars_dir, exist_ok=True)
        print(f"✓ 已创建头像目录: {avatars_dir}")
        
except Exception as e:
    print(f"✗ 错误: {str(e)}")
    traceback.print_exc()