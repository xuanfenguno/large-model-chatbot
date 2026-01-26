import requests

response = requests.get('http://127.0.0.1:8000/api/v1/models/')
if response.status_code == 200:
    models = response.json()
    qwen_models = [m for m in models if '通义千问' in m['name']]
    print(f'通义千问相关模型数量: {len(qwen_models)}')
    for model in qwen_models:
        print(f'  - {model["id"]}: {model["name"]}')
else:
    print(f'请求失败: {response.status_code}')