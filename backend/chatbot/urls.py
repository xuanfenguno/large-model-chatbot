from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, login_view, register_view, health_check, available_models, wechat_auth_url, wechat_auth_callback, qq_auth_url, qq_auth_callback, github_auth_url, github_auth_callback, request_password_reset, reset_password

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('health/', health_check, name='health_check'),
    path('models/', available_models, name='available-models'),
    path('auth/wechat/', wechat_auth_url, name='wechat-auth-url'),
    path('auth/wechat/callback/', wechat_auth_callback, name='wechat-auth-callback'),
    path('auth/qq/', qq_auth_url, name='qq-auth-url'),
    path('auth/qq/callback/', qq_auth_callback, name='qq-auth-callback'),
    path('auth/github/', github_auth_url, name='github-auth-url'),
    path('auth/github/callback/', github_auth_callback, name='github-auth-callback'),
    path('password/reset/request/', request_password_reset, name='request-password-reset'),
    path('password/reset/', reset_password, name='reset-password'),
]