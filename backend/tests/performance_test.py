"""
性能测试脚本
"""
import os
import sys
import django
import time
from django.core.management import execute_from_command_line

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chatbot.models import Conversation, Message, UserProfile
from django.contrib.auth.models import User
from django.test import Client
from django.core.cache import cache
import threading
import logging

logger = logging.getLogger(__name__)


def test_database_performance():
    """
    测试数据库查询性能
    """
    print("开始数据库性能测试...")
    
    # 测试1: 获取用户会话列表
    start_time = time.time()
    user = User.objects.first()
    if user:
        conversations = Conversation.objects.filter(user=user).select_related('user').order_by('-updated_at')[:10]
        conv_count = len(list(conversations))
    else:
        conv_count = 0
    conv_time = time.time() - start_time
    print(f"获取用户会话列表 ({conv_count} 个会话): {conv_time:.4f}秒")

    # 测试2: 获取会话消息
    start_time = time.time()
    if conversations:
        first_conv = conversations[0]
        messages = Message.objects.filter(conversation=first_conv).select_related('conversation__user').order_by('created_at')[:50]
        msg_count = len(list(messages))
    else:
        msg_count = 0
    msg_time = time.time() - start_time
    print(f"获取会话消息 ({msg_count} 条消息): {msg_time:.4f}秒")

    # 测试3: 获取用户配置
    start_time = time.time()
    if user:
        try:
            profile = UserProfile.objects.select_related('user').get(user=user)
        except UserProfile.DoesNotExist:
            profile = None
    else:
        profile = None
    profile_time = time.time() - start_time
    print(f"获取用户配置: {profile_time:.4f}秒")

    print("数据库性能测试完成")


def test_cache_performance():
    """
    测试缓存性能
    """
    print("\n开始缓存性能测试...")
    
    # 测试缓存设置
    start_time = time.time()
    test_data = {'test': 'data', 'timestamp': time.time()}
    cache.set('performance_test_key', test_data, 300)
    set_time = time.time() - start_time
    print(f"设置缓存: {set_time:.4f}秒")

    # 测试缓存获取
    start_time = time.time()
    retrieved_data = cache.get('performance_test_key')
    get_time = time.time() - start_time
    print(f"获取缓存: {get_time:.4f}秒")

    # 测试缓存命中率
    hits = 0
    misses = 0
    for i in range(100):
        if cache.get(f'test_key_{i}') is None:
            cache.set(f'test_key_{i}', f'value_{i}', 300)
            misses += 1
        else:
            hits += 1
    
    print(f"缓存命中率: {hits}/100 hits, {misses}/100 misses")

    print("缓存性能测试完成")


def simulate_concurrent_requests():
    """
    模拟并发请求
    """
    print("\n开始并发请求测试...")
    
    def make_request():
        client = Client()
        # 模拟API请求
        response = client.get('/api/v1/health/')  # 假设存在健康检查端点
        return response.status_code

    # 创建多个线程模拟并发请求
    threads = []
    start_time = time.time()
    
    for i in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    print(f"10个并发请求总耗时: {total_time:.4f}秒")
    print("并发请求测试完成")


def run_all_tests():
    """
    运行所有性能测试
    """
    print("=" * 50)
    print("开始性能测试")
    print("=" * 50)
    
    test_database_performance()
    test_cache_performance()
    simulate_concurrent_requests()
    
    print("\n" + "=" * 50)
    print("性能测试完成")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()