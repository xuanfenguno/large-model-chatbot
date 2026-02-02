import requests
import json
from PIL import Image
import io

def test_with_debug_info():
    """
    测试上传功能并提供调试信息
    """
    # 创建测试图片
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    
    # 尝试无认证上传（预期会失败，但应返回401而非500）
    upload_url = "http://127.0.0.1:8080/api/v1/upload-avatar/"
    
    files = {
        'avatar': ('test_avatar.jpg', img_io, 'image/jpeg')
    }
    
    print("正在测试未认证的上传请求（应该返回401）...")
    try:
        response = requests.post(upload_url, files=files, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 500:
            print("❌ 发生了500服务器错误！")
            print("这表明后端存在内部错误")
        elif response.status_code == 401:
            print("✅ 正确返回401未授权错误")
        else:
            print(f"? 返回了意外状态码: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    test_with_debug_info()