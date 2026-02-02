import requests
import os
from PIL import Image
from io import BytesIO

# 创建一个测试图片
def create_test_image():
    # 创建一个简单的测试图片
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io

# 测试上传
def test_upload():
    # 注意：你需要先登录获取有效的token
    # 这只是一个示例，实际使用时需要有效的认证信息
    
    # 创建测试图片
    test_img = create_test_image()
    
    # 发送上传请求
    url = 'http://127.0.0.1:8080/api/v1/upload-avatar/'
    
    # 注意：你需要有效的JWT token
    headers = {
        'Authorization': 'Bearer YOUR_VALID_TOKEN_HERE'  # 替换为有效的token
    }
    
    files = {
        'avatar': ('test_avatar.jpg', test_img, 'image/jpeg')
    }
    
    try:
        response = requests.post(url, files=files, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_upload()