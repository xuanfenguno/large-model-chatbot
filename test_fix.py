import requests
import json
from PIL import Image
import io

def test_upload_after_fix():
    """
    测试修复后的上传功能
    """
    # 创建测试图片
    img = Image.new('RGB', (100, 100), color='blue')
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    
    # 首先尝试登录获取有效token（虽然会失败，但可测试登录接口）
    login_url = "http://127.0.0.1:8080/api/v1/login/"
    
    print("1. 测试登录接口...")
    login_data = {"username": "invalid", "password": "invalid"}
    try:
        login_resp = requests.post(login_url, json=login_data)
        print(f"   登录响应: {login_resp.status_code}")
    except Exception as e:
        print(f"   登录测试失败: {e}")
    
    # 测试无认证上传（应该返回401）
    upload_url = "http://127.0.0.1:8080/api/v1/upload-avatar/"
    
    print("\n2. 测试未认证的上传请求...")
    try:
        response = requests.post(upload_url, files={'avatar': ('test.jpg', img_io, 'image/jpeg')})
        print(f"   上传响应状态码: {response.status_code}")
        print(f"   上传响应内容: {response.text}")
        
        if response.status_code == 500:
            print("   ❌ 仍然存在500错误")
        else:
            print(f"   ✅ 没有返回500错误，状态码: {response.status_code}")
    except Exception as e:
        print(f"   上传测试失败: {e}")
    
    # 重置图片IO流
    img_io.seek(0)
    
    # 测试带无效token的上传
    print("\n3. 测试带无效token的上传请求...")
    try:
        headers = {'Authorization': 'Bearer invalid_token'}
        response = requests.post(upload_url, 
                                files={'avatar': ('test.jpg', img_io, 'image/jpeg')},
                                headers=headers)
        print(f"   带token上传响应状态码: {response.status_code}")
        print(f"   响应内容: {response.text}")
        
        if response.status_code == 500:
            print("   ❌ 仍然存在500错误")
        else:
            print(f"   ✅ 没有返回500错误，状态码: {response.status_code}")
    except Exception as e:
        print(f"   带token上传测试失败: {e}")

if __name__ == "__main__":
    test_upload_after_fix()