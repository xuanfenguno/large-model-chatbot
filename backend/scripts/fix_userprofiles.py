#!/usr/bin/env python
"""修复UserProfile表中的重复条目"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from app.models.models import UserProfile
from django.db import transaction

def fix_duplicate_userprofiles():
    """修复重复的用户配置文件"""
    print("开始修复重复的UserProfile...")
    
    # 查找重复的user_id
    duplicate_profiles = []
    seen_user_ids = set()
    
    for profile in UserProfile.objects.all():
        if profile.user_id in seen_user_ids:
            duplicate_profiles.append(profile)
        else:
            seen_user_ids.add(profile.user_id)
    
    if not duplicate_profiles:
        print("未发现重复的UserProfile")
        return
    
    print(f"发现 {len(duplicate_profiles)} 个重复的UserProfile")
    
    # 删除重复条目
    for profile in duplicate_profiles:
        print(f"删除重复的UserProfile: user_id={profile.user_id}")
        profile.delete()
    
    print("重复条目清理完成")
    
    # 为没有UserProfile的用户创建配置文件
    users_without_profile = []
    for user in User.objects.all():
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            users_without_profile.append(user)
    
    if users_without_profile:
        print(f"为 {len(users_without_profile)} 个没有配置文件的用户创建UserProfile")
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            print(f"为用户 {user.username} 创建UserProfile")

if __name__ == '__main__':
    fix_duplicate_userprofiles()