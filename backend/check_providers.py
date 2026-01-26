import requests

response = requests.get('http://127.0.0.1:8000/api/v1/models/')
if response.status_code == 200:
    models = response.json()
    baichuan_models = [m for m in models if '百川' in m['name'] or 'Baichuan' in m['name'] or 'baichuan' in m['name']]
    print(f'百川模型数量: {len(baichuan_models)}')
    for model in baichuan_models:
        print(f'  - {model["id"]}: {model["name"]}')
    
    print()
    
    alibaba_models = [m for m in models if m['provider'] == 'Alibaba']
    print(f'阿里巴巴模型数量: {len(alibaba_models)}')
    for model in alibaba_models:
        print(f'  - {model["id"]}: {model["name"]}')
        
    print()
    
    # 检查是否有其他不想要的模型
    unwanted_models = [m for m in models if '百炼' in m['name']]
    print(f'百炼模型数量: {len(unwanted_models)}')
    for model in unwanted_models:
        print(f'  - {model["id"]}: {model["name"]}')