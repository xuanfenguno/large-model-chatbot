import requests

response = requests.get('http://127.0.0.1:8000/api/v1/models/')
if response.status_code == 200:
    models = response.json()
    openai_models = [m for m in models if m['provider'] == 'OpenAI']
    print(f'OpenAI 模型数量: {len(openai_models)}')
    for model in openai_models:
        print(f'  - {model["id"]}: {model["name"]}')
else:
    print(f'请求失败: {response.status_code}')