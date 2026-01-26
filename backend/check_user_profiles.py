#!/usr/bin/env python
"""
检查并修复用户配置文件的脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from django.contrib.auth.models import User
from chatbot.models import UserProfile

def check_and_fix_user_profiles():
    """检查并修复缺失的用户配置文件"""
    print("检查用户配置文件完整性...")
    
    # 查找没有配置文件的用户
    users_without_profile = []
    for user in User.objects.all():
        try:
            profile = user.profile  # 尝试访问用户的配置文件
        except UserProfile.DoesNotExist:
            users_without_profile.append(user)
    
    if users_without_profile:
        print(f"发现 {len(users_without_profile)} 个用户缺少配置文件:")
        for user in users_without_profile:
            print(f"  - 用户ID: {user.id}, 用户名: {user.username}")
        
        print("\n正在为这些用户创建配置文件...")
        for user in users_without_profile:
            profile = UserProfile.objects.create(user=user)
            print(f"  - 为用户 '{user.username}' 创建配置文件")
        
        print("配置文件修复完成!")
    else:
        print("所有用户都有对应的配置文件，无需修复。")

def main():
    check_and_fix_user_profiles()

if __name__ == "__main__":
    main()