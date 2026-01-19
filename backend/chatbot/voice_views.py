from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
import json
import uuid
from datetime import datetime, timedelta

# 存储通话状态的临时存储（生产环境应使用Redis）
active_calls = {}
call_signaling = {}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_call(request):
    """发起语音通话"""
    try:
        target_user_id = request.data.get('target_user_id')
        call_id = str(uuid.uuid4())
        
        # 验证目标用户是否存在
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({
                'error': '目标用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 检查目标用户是否在线（简化实现）
        # 实际项目中应该检查用户的在线状态
        
        # 创建通话记录
        call_data = {
            'call_id': call_id,
            'caller_id': request.user.id,
            'caller_username': request.user.username,
            'target_user_id': target_user_id,
            'target_username': target_user.username,
            'status': 'pending',  # pending, accepted, rejected, ended
            'created_at': datetime.now().isoformat(),
            'accepted_at': None,
            'ended_at': None,
            'duration': 0
        }
        
        active_calls[call_id] = call_data
        
        # 这里应该通过WebSocket通知目标用户
        # 简化实现：返回通话信息
        
        return Response({
            'call_id': call_id,
            'status': 'initiated',
            'message': '通话请求已发送'
        })
        
    except Exception as e:
        return Response({
            'error': f'发起通话失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def answer_call(request):
    """接听语音通话"""
    try:
        call_id = request.data.get('call_id')
        
        if call_id not in active_calls:
            return Response({
                'error': '通话不存在或已过期'
            }, status=status.HTTP_404_NOT_FOUND)
        
        call_data = active_calls[call_id]
        
        # 验证用户是否有权限接听此通话
        if call_data['target_user_id'] != request.user.id:
            return Response({
                'error': '无权接听此通话'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 更新通话状态
        call_data['status'] = 'accepted'
        call_data['accepted_at'] = datetime.now().isoformat()
        
        # 这里应该通过WebSocket通知发起方
        
        return Response({
            'call_id': call_id,
            'status': 'accepted',
            'message': '通话已接听'
        })
        
    except Exception as e:
        return Response({
            'error': f'接听通话失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_call(request):
    """拒绝语音通话"""
    try:
        call_id = request.data.get('call_id')
        
        if call_id not in active_calls:
            return Response({
                'error': '通话不存在或已过期'
            }, status=status.HTTP_404_NOT_FOUND)
        
        call_data = active_calls[call_id]
        
        # 验证用户是否有权限拒绝此通话
        if call_data['target_user_id'] != request.user.id:
            return Response({
                'error': '无权拒绝此通话'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 更新通话状态
        call_data['status'] = 'rejected'
        call_data['ended_at'] = datetime.now().isoformat()
        
        # 这里应该通过WebSocket通知发起方
        
        return Response({
            'call_id': call_id,
            'status': 'rejected',
            'message': '通话已拒绝'
        })
        
    except Exception as e:
        return Response({
            'error': f'拒绝通话失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_call(request):
    """结束语音通话"""
    try:
        call_id = request.data.get('call_id')
        
        if call_id not in active_calls:
            return Response({
                'error': '通话不存在或已过期'
            }, status=status.HTTP_404_NOT_FOUND)
        
        call_data = active_calls[call_id]
        
        # 验证用户是否有权限结束此通话
        if (call_data['caller_id'] != request.user.id and 
            call_data['target_user_id'] != request.user.id):
            return Response({
                'error': '无权结束此通话'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 计算通话时长
        if call_data['accepted_at']:
            accepted_time = datetime.fromisoformat(call_data['accepted_at'])
            ended_time = datetime.now()
            duration = int((ended_time - accepted_time).total_seconds())
            call_data['duration'] = duration
        
        # 更新通话状态
        call_data['status'] = 'ended'
        call_data['ended_at'] = datetime.now().isoformat()
        
        # 这里应该通过WebSocket通知对方
        
        # 清理通话数据（保留一段时间供查询）
        # 实际项目中应该将通话记录保存到数据库
        
        return Response({
            'call_id': call_id,
            'status': 'ended',
            'duration': call_data.get('duration', 0),
            'message': '通话已结束'
        })
        
    except Exception as e:
        return Response({
            'error': f'结束通话失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_call_status(request):
    """获取通话状态"""
    try:
        call_id = request.GET.get('call_id')
        
        if call_id not in active_calls:
            return Response({
                'error': '通话不存在或已过期'
            }, status=status.HTTP_404_NOT_FOUND)
        
        call_data = active_calls[call_id]
        
        # 验证用户是否有权限查看此通话
        if (call_data['caller_id'] != request.user.id and 
            call_data['target_user_id'] != request.user.id):
            return Response({
                'error': '无权查看此通话'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return Response(call_data)
        
    except Exception as e:
        return Response({
            'error': f'获取通话状态失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signaling(request):
    """WebRTC信令交换"""
    try:
        call_id = request.data.get('call_id')
        signal_type = request.data.get('type')  # offer, answer, ice-candidate
        signal_data = request.data.get('data')
        
        if call_id not in active_calls:
            return Response({
                'error': '通话不存在或已过期'
            }, status=status.HTTP_404_NOT_FOUND)
        
        call_data = active_calls[call_id]
        
        # 验证用户是否有权限发送信令
        if (call_data['caller_id'] != request.user.id and 
            call_data['target_user_id'] != request.user.id):
            return Response({
                'error': '无权发送信令'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 存储信令数据
        if call_id not in call_signaling:
            call_signaling[call_id] = []
        
        signaling_entry = {
            'type': signal_type,
            'data': signal_data,
            'from_user_id': request.user.id,
            'timestamp': datetime.now().isoformat()
        }
        
        call_signaling[call_id].append(signaling_entry)
        
        # 这里应该通过WebSocket将信令转发给对应用户
        
        return Response({
            'status': 'signaling_sent',
            'message': '信令已发送'
        })
        
    except Exception as e:
        return Response({
            'error': f'信令发送失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_signaling(request):
    """获取信令数据"""
    try:
        call_id = request.GET.get('call_id')
        last_timestamp = request.GET.get('last_timestamp')
        
        if call_id not in call_signaling:
            return Response({
                'signals': []
            })
        
        signals = call_signaling[call_id]
        
        # 过滤出指定时间戳之后的新信令
        if last_timestamp:
            filtered_signals = [
                signal for signal in signals 
                if signal['timestamp'] > last_timestamp
            ]
        else:
            filtered_signals = signals
        
        # 过滤掉当前用户自己发送的信令
        user_signals = [
            signal for signal in filtered_signals
            if signal['from_user_id'] != request.user.id
        ]
        
        return Response({
            'signals': user_signals,
            'last_timestamp': signals[-1]['timestamp'] if signals else last_timestamp
        })
        
    except Exception as e:
        return Response({
            'error': f'获取信令失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 清理过期通话的定时任务（简化实现）
def cleanup_expired_calls():
    """清理过期通话"""
    current_time = datetime.now()
    expired_calls = []
    
    for call_id, call_data in active_calls.items():
        created_time = datetime.fromisoformat(call_data['created_at'])
        
        # 超过30分钟未接听的通话视为过期
        if (call_data['status'] == 'pending' and 
            (current_time - created_time) > timedelta(minutes=30)):
            expired_calls.append(call_id)
        
        # 超过24小时的已结束通话清理
        elif (call_data['status'] in ['ended', 'rejected'] and 
              (current_time - created_time) > timedelta(hours=24)):
            expired_calls.append(call_id)
    
    for call_id in expired_calls:
        if call_id in active_calls:
            del active_calls[call_id]
        if call_id in call_signaling:
            del call_signaling[call_id]