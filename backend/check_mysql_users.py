#!/usr/bin/env python
"""
MySQL数据库用户信息查询脚本
"""
import os
import sys
import pymysql
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def check_mysql_users():
    """检查MySQL数据库中的用户信息"""
    
    # MySQL连接配置（从环境变量获取）
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'root123'),
        'database': os.getenv('DB_NAME', 'chatbot_db'),
        'charset': 'utf8mb4'
    }
    
    try:
        # 连接MySQL数据库
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        print("🔍 MySQL数据库连接成功！")
        print("=" * 60)
        
        # 查询所有表
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("📋 数据库中的表：")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "=" * 60)
        
        # 查询用户表
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        user_count = cursor.fetchone()[0]
        print(f"👥 总用户数: {user_count}")
        
        # 查询用户详细信息
        cursor.execute("""
            SELECT username, email, date_joined, last_login 
            FROM auth_user 
            ORDER BY date_joined DESC 
            LIMIT 10
        """)
        users = cursor.fetchall()
        
        print("\n📊 最新注册用户（前10个）：")
        for user in users:
            username, email, date_joined, last_login = user
            print(f"  - 用户名: {username}")
            print(f"    邮箱: {email}")
            print(f"    注册时间: {date_joined}")
            if last_login:
                print(f"    最后登录: {last_login}")
            print()
        
        # 查询用户配置表
        cursor.execute("SELECT COUNT(*) FROM chatbot_userprofile;")
        profile_count = cursor.fetchone()[0]
        print(f"📝 用户配置数: {profile_count}")
        
        # 查询用户配置详情
        cursor.execute("""
            SELECT u.username, p.phone, p.created_at 
            FROM auth_user u 
            LEFT JOIN chatbot_userprofile p ON u.id = p.user_id 
            WHERE p.phone IS NOT NULL
            LIMIT 5
        """)
        profiles = cursor.fetchall()
        
        if profiles:
            print("\n📱 有手机号的用户：")
            for profile in profiles:
                username, phone, created_at = profile
                print(f"  - 用户名: {username}, 手机号: {phone}, 创建时间: {created_at}")
        
        # 关闭连接
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("✅ MySQL数据库查询完成！")
        
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        print("💡 提示：请检查MySQL服务是否启动，以及数据库配置是否正确")

if __name__ == '__main__':
    check_mysql_users()