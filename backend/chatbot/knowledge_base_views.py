"""
知识库API视图
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .utils.knowledge_base import knowledge_base_manager, real_time_source

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_knowledge_base(request):
    """
    搜索知识库
    """
    try:
        query = request.data.get('query', '')
        top_k = request.data.get('top_k', 5)
        
        if not query:
            return Response({'error': 'Query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = knowledge_base_manager.search(query, n_results=top_k)
        
        return Response({
            'results': results,
            'query': query,
            'count': len(results),
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_knowledge_base(request):
    """
    添加内容到知识库
    """
    try:
        doc_id = request.data.get('doc_id')
        content = request.data.get('content')
        metadata = request.data.get('metadata', {})
        
        if not doc_id or not content:
            return Response({'error': 'doc_id and content are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 添加用户信息到元数据
        metadata['user_id'] = request.user.id
        metadata['added_by'] = request.user.username
        metadata['added_at'] = timezone.now().isoformat()
        
        knowledge_base_manager.add_document(doc_id, content, metadata)
        
        return Response({
            'success': True, 
            'doc_id': doc_id,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_from_knowledge_base(request, doc_id):
    """
    从知识库删除内容
    """
    try:
        knowledge_base_manager.delete_document(doc_id)
        
        return Response({
            'success': True,
            'doc_id': doc_id,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_knowledge_base(request):
    """
    手动同步知识库
    """
    try:
        # 同步数据库内容
        real_time_source.sync_from_database()
        
        # 可选：同步外部API（如果有配置）
        external_sources = request.data.get('external_sources', [])
        for source in external_sources:
            real_time_source.sync_from_external_api(
                source['url'], 
                source.get('headers', {})
            )
        
        return Response({
            'success': True,
            'message': 'Knowledge base synchronized successfully',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_knowledge_base_stats(request):
    """
    获取知识库统计信息
    """
    try:
        # 由于ChromaDB的API限制，我们无法直接获取文档总数
        # 但可以返回一些基本统计信息
        return Response({
            'kb_available': knowledge_base_manager.client is not None,
            'collection_name': knowledge_base_manager.collection_name,
            'timestamp': timezone.now().isoformat(),
            'message': 'Statistics available when ChromaDB is initialized'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)