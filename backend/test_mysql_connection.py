import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# 尝试连接MySQL
try:
    import pymysql
    
    # 尝试连接到MySQL服务器（不指定数据库）
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root123'),
        charset='utf8mb4'
    )
    
    print("成功连接到MySQL服务器!")
    
    # 检查数据库是否存在
    cursor = connection.cursor()
    cursor.execute("SHOW DATABASES;")
    databases = cursor.fetchall()
    
    print("\n当前存在的数据库:")
    for db in databases:
        print(f"- {db[0]}")
    
    # 检查我们的数据库是否存在
    target_db = os.getenv('DB_NAME', 'chatbot_db')
    if (target_db,) in databases:
        print(f"\n数据库 '{target_db}' 已存在")
    else:
        print(f"\n数据库 '{target_db}' 不存在")
        
        # 尝试创建数据库
        try:
            cursor.execute(f"CREATE DATABASE `{target_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"数据库 '{target_db}' 已创建成功!")
        except Exception as e:
            print(f"创建数据库 '{target_db}' 失败: {e}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"连接MySQL失败: {e}")
    print("请确保MySQL服务器正在运行，并且用户名和密码正确")