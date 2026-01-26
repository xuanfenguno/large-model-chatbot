import requests

response = requests.get('http://127.0.0.1:8000/api/v1/models/')
if response.status_code == 200:
    models = response.json()
    bailian_models = [m for m in models if '百炼' in m['name'] or 'Bailian' in m['name'] or 'bailian' in m['name']]
    print(f'百炼模型数量: {len(bailian_models)}')
    for model in bailian_models:
        print(f'  - {model["id"]}: {model["name"]}')
        
    # 也检查是否有其他不想要的模型
    all_models = [(m["id"], m["name"], m["provider"]) for m in models]
    print(f'\n总模型数: {len(all_models)}')
    for mid, name, provider in all_models:
        print(f'  - {mid}: {name} ({provider})')