import requests
import json
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from chatbot.models import UserProfile

def test_login_and_avatar_upload():
    """
    测试登录和头像上传流程
    """
    print("=== 登录和头像上传测试 ===")
    
    # 首先检查是否有测试用户，如果没 有则创建
    username = "testuser"
    password = "TestPassword123!"
    
    # 检查用户是否存在，如果不存在则创建
    try:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'test@example.com',
                'password': make_password(password)
            }
        )
        
        if created:
            print(f"✓ 已创建测试用户: {username}")
        else:
            print(f"- 测试用户 {username} 已存在")
            
        # 确保用户配置存在
        profile, profile_created = UserProfile.objects.get_or_create(user=user)
        if profile_created:
            print(f"✓ 已创建用户配置")
        
    except Exception as e:
        print(f"✗ 用户创建失败: {e}")
        return
    
    # 测试登录
    login_url = "http://127.0.0.1:8080/api/v1/login/"
    
    print(f"\n1. 测试登录...")
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        login_response = requests.post(login_url, json=login_data, timeout=10)
        print(f"   登录响应状态码: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_json = login_response.json()
            token = login_json.get('access')
            print(f"   ✓ 登录成功，获得访问令牌")
            
            # 现在尝试上传头像
            print(f"\n2. 测试头像上传...")
            upload_url = "http://127.0.0.1:8080/api/v1/upload-avatar/"
            
            # 创建一个测试图片
            import io
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)
            
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            files = {
                'avatar': ('test_avatar.jpg', img_io, 'image/jpeg')
            }
            
            upload_response = requests.post(upload_url, headers=headers, files=files, timeout=30)
            print(f"   上传响应状态码: {upload_response.status_code}")
            
            if upload_response.status_code == 200:
                print(f"   ✓ 头像上传成功!")
                response_data = upload_response.json()
                print(f"   响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            else:
                print(f"   ✗ 头像上传失败!")
                print(f"   响应内容: {upload_response.text}")
                
        else:
            print(f"   ✗ 登录失败!")
            print(f"   响应内容: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ✗ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"   ✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

class Command(BaseCommand):
    help = '测试登录和头像上传功能'

    def handle(self, *args, **options):
        test_login_and_avatar_upload()