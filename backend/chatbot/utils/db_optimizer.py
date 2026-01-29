"""
数据库查询优化工具
"""
from django.db import connection
from django.db.models import Prefetch, Count, Q
from django.core.paginator import Paginator
from chatbot.models import Conversation, Message, UserProfile, PasswordResetToken, VoiceCallRecord
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


def get_user_conversations_optimized(user_id, page=1, page_size=10, include_message_count=True):
    """
    优化的获取用户会话列表函数
    使用select_related和prefetch_related减少数据库查询
    """
    queryset = Conversation.objects.filter(user_id=user_id).select_related('user').order_by('-updated_at')
    
    if include_message_count:
        queryset = queryset.annotate(message_count=Count('messages'))
    
    paginator = Paginator(queryset, page_size)
    conversations = paginator.get_page(page)
    
    return conversations


def get_conversation_messages_optimized(conversation_id, page=1, page_size=50):
    """
    优化的获取会话消息列表函数
    """
    queryset = Message.objects.filter(conversation_id=conversation_id).select_related('conversation__user').order_by('created_at')
    
    paginator = Paginator(queryset, page_size)
    messages = paginator.get_page(page)
    
    return messages


def get_user_with_profile(user_id):
    """
    一次性获取用户及其配置信息
    """
    try:
        user = User.objects.select_related('profile').get(id=user_id)
        return user
    except User.DoesNotExist:
        return None


def get_users_with_recent_activity(days=7):
    """
    获取最近活跃的用户
    """
    from django.utils import timezone
    from datetime import timedelta
    
    recent_date = timezone.now() - timedelta(days=days)
    
    # 获取最近有会话活动的用户
    active_users = User.objects.filter(
        conversations__updated_at__gte=recent_date
    ).select_related('profile').distinct()
    
    return active_users


def bulk_create_messages(messages_data):
    """
    批量创建消息，提高插入效率
    """
    messages = []
    for data in messages_data:
        messages.append(Message(
            conversation_id=data['conversation_id'],
            role=data['role'],
            message_type=data['message_type'],
            content=data['content'],
            image_url=data.get('image_url'),
            is_read=data.get('is_read', False),
            audio_file=data.get('audio_file'),
            audio_duration=data.get('audio_duration'),
            transcription_confidence=data.get('transcription_confidence')
        ))
    
    return Message.objects.bulk_create(messages)


def get_statistics_for_dashboard():
    """
    为仪表板获取统计信息，使用单个查询获取多个统计数据
    """
    from django.db.models import Count, Avg
    
    stats = {}
    
    # 获取用户总数
    stats['total_users'] = User.objects.count()
    
    # 获取会话总数和平均会话长度
    conversation_stats = Conversation.objects.aggregate(
        total_conversations=Count('id'),
    )
    stats.update(conversation_stats)
    
    # 获取消息总数
    stats['total_messages'] = Message.objects.count()
    
    # 获取今日活跃用户数
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    stats['today_active_users'] = Conversation.objects.filter(
        updated_at__date=today
    ).values('user').distinct().count()
    
    return stats


def optimize_queryset_for_serialization(queryset, fields=None):
    """
    为序列化优化查询集，只获取必要字段
    """
    if fields:
        return queryset.values(*fields)
    return queryset


def get_user_conversations_with_latest_message(user_id):
    """
    获取用户会话及其最新消息，优化查询
    """
    from django.db.models import Max
    
    conversations = Conversation.objects.filter(user_id=user_id).select_related('user').annotate(
        latest_message_time=Max('messages__created_at')
    ).order_by('-latest_message_time')
    
    return conversations


def search_messages_optimized(user_id, search_term, max_results=50):
    """
    优化的消息搜索功能
    """
    conversations_ids = Conversation.objects.filter(user_id=user_id).values_list('id', flat=True)
    
    messages = Message.objects.filter(
        conversation_id__in=conversations_ids,
        content__icontains=search_term
    ).select_related('conversation').order_by('-created_at')[:max_results]
    
    return messages


def get_efficient_user_data(user_ids):
    """
    高效获取多个用户的数据
    """
    users = User.objects.filter(id__in=user_ids).select_related('profile').prefetch_related(
        'conversations',
        'outgoing_calls',
        'incoming_calls'
    )
    
    return users


def get_conversations_summary(conversation_ids):
    """
    获取会话摘要信息
    """
    conversations = Conversation.objects.filter(
        id__in=conversation_ids
    ).select_related('user').annotate(
        message_count=Count('messages'),
        last_message_time=Max('messages__created_at')
    ).values(
        'id', 'title', 'model', 'mode', 'created_at', 'updated_at',
        'user__username', 'message_count', 'last_message_time'
    )
    
    return conversations


def log_query_performance():
    """
    记录查询性能日志
    """
    logger.info(f"Total queries: {len(connection.queries)}")
    for query in connection.queries:
        logger.debug(f"Query: {query['sql']} | Time: {query['time']}")