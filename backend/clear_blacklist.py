#!/usr/bin/env python
"""
用于清除IP黑名单的管理脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from django.core.cache import cache
import re

def clear_all_rate_limits():
    """清除所有的速率限制缓存"""
    try:
        # 查找所有与速率限制相关的缓存键
        rate_limit_keys = []
        
        # 注意：在实际的Django项目中，cache.keys()可能不可用
        # 这里我们采用直接清除所有缓存的方式
        cache.clear()
        print("✓ 已清除所有缓存，包括速率限制和黑名单记录")
        
    except Exception as e:
        print(f"✗ 清除缓存时出错: {e}")

def main():
    print("正在清除IP黑名单...")
    clear_all_rate_limits()
    print("完成！您的IP地址应该已经从黑名单中移除。")

if __name__ == "__main__":
    main()