from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConversationViewSet, 
    MessageViewSet, 
    UserLoginView, 
    UserRegistrationView, 
    available_models, 
    request_password_reset, 
    reset_password, 
    reset_password_test,
    function_router, 
    stream_function_router_view,
    stream_chat, 
    chat,
    upload_avatar, 
    upload_chat_image,
    get_user_info,
    health_check,
    user_settings,
    ai_settings,
    appearance_settings,
    privacy_settings,
    change_password,
    profile,
    get_role_presets
)
from .voice_views import initiate_call, answer_call, reject_call, end_call, get_call_status, signaling, get_signaling, get_call_history, get_active_calls
# Knowledge base views are now imported from their dedicated file
from .knowledge_base_views import (
    search_knowledge_base,
    add_to_knowledge_base,
    delete_from_knowledge_base,
    sync_knowledge_base,
    get_knowledge_base_stats
)

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
# router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('health-check/', health_check, name='health-check'),
    path('', include(router.urls)),
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),

    path('models/', available_models, name='available-models'),

    path('password/reset/request/', request_password_reset, name='request-password-reset'),
    path('password/reset/', reset_password, name='reset-password'),
    path('password/reset/test/', reset_password_test, name='reset-password-test'),
    # 功能路由API
    path('function-router/', function_router, name='function-router'),
    # 流式功能路由API
    path('stream-function-router/', stream_function_router_view, name='stream-function-router'),
    # 预设角色列表API
    path('role-presets/', get_role_presets, name='role-presets'),
    # 流式聊天API
    path('stream-chat/', stream_chat, name='stream-chat'),
    path('chat/', chat, name='chat'),
    # 语音通话API
    path('voice/initiate/', initiate_call, name='initiate-call'),
    path('voice/answer/', answer_call, name='answer-call'),
    path('voice/reject/', reject_call, name='reject-call'),
    path('voice/end/', end_call, name='end-call'),
    path('voice/status/', get_call_status, name='call-status'),
    path('voice/signaling/', signaling, name='signaling'),
    path('voice/signaling/get/', get_signaling, name='get-signaling'),
    path('voice/history/', get_call_history, name='call-history'),
    path('voice/active/', get_active_calls, name='active-calls'),
    # 知识库API
    path('knowledge-base/search/', search_knowledge_base, name='search_knowledge_base'),
    path('knowledge-base/add/', add_to_knowledge_base, name='add_to_knowledge_base'),
    path('knowledge-base/delete/<str:doc_id>/', delete_from_knowledge_base, name='delete_from_knowledge_base'),
    path('knowledge-base/sync/', sync_knowledge_base, name='sync_knowledge_base'),
    path('knowledge-base/stats/', get_knowledge_base_stats, name='get_knowledge_base_stats'),
    # 头像上传和用户信息API
    path('upload-avatar/', upload_avatar, name='upload-avatar'),
    path('upload-image/', upload_chat_image, name='upload-chat-image'),
    path('user-info/', get_user_info, name='get-user-info'),
    # 用户设置API
    path('settings/', user_settings, name='user-settings'),
    path('ai-settings/', ai_settings, name='ai-settings'),
    path('appearance-settings/', appearance_settings, name='appearance-settings'),
    path('privacy-settings/', privacy_settings, name='privacy-settings'),
    # 修改密码API
    path('change-password/', change_password, name='change-password'),
    # 个人资料API
    path('profile/', profile, name='profile'),
]