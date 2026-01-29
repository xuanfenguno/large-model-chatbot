from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, login_view, register_view, health_check, available_models, request_password_reset, reset_password, reset_password_test, function_router, stream_chat
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
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('health/', health_check, name='health_check'),
    path('models/', available_models, name='available-models'),

    path('password/reset/request/', request_password_reset, name='request-password-reset'),
    path('password/reset/', reset_password, name='reset-password'),
    path('password/reset/test/', reset_password_test, name='reset-password-test'),
    # 功能路由API
    path('function-router/', function_router, name='function-router'),
    # 流式聊天API
    path('stream-chat/', stream_chat, name='stream-chat'),
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
]