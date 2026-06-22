from django.apps import AppConfig


class ChatbotAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    label = 'chatbot'  # 保持迁移历史兼容
