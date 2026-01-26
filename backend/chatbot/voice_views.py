from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
import json
import uuid
from datetime import datetime, timedelta
import asyncio
import redis
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import VoiceCallRecord

# 存储通话状态的临时存储（生产环境应使用Redis）
active_calls = {}
call_signaling = {}

# 尝试连接Redis，如果不可用则使用内存存储
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_available = True
except:
    redis_available = False
    print("Redis unavailable, using in-memory storage")

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
        call_record = VoiceCallRecord.objects.create(
            call_id=call_id,
            caller=request.user,
            callee=target_user,
            status='pending'
        )
        
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
        
        # 通过WebSocket通知目标用户
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{target_user_id}",
                {
                    "type": "voice.call.incoming",
                    "call_id": call_id,
                    "caller_username": request.user.username
                }
            )
        
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
        
        # 更新通话记录
        try:
            call_record = VoiceCallRecord.objects.get(call_id=call_id)
            call_record.status = 'accepted'
            call_record.accepted_at = datetime.now()
            call_record.save()
        except VoiceCallRecord.DoesNotExist:
            pass  # 如果记录不存在，继续执行
        
        # 通过WebSocket通知发起方
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{call_data['caller_id']}",
                {
                    "type": "voice.call.accepted",
                    "call_id": call_id
                }
            )
        
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
        
        # 更新通话记录
        try:
            call_record = VoiceCallRecord.objects.get(call_id=call_id)
            call_record.status = 'rejected'
            call_record.ended_at = datetime.now()
            call_record.save()
        except VoiceCallRecord.DoesNotExist:
            pass  # 如果记录不存在，继续执行
        
        # 通过WebSocket通知发起方
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{call_data['caller_id']}",
                {
                    "type": "voice.call.rejected",
                    "call_id": call_id
                }
            )
        
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
        
        # 更新通话记录
        try:
            call_record = VoiceCallRecord.objects.get(call_id=call_id)
            call_record.status = 'ended'
            call_record.ended_at = datetime.now()
            if call_record.accepted_at:
                call_record.duration = int((ended_time - call_record.accepted_at).total_seconds())
            call_record.save()
        except VoiceCallRecord.DoesNotExist:
            pass  # 如果记录不存在，继续执行
        
        # 通过WebSocket通知对方
        channel_layer = get_channel_layer()
        if channel_layer:
            # 通知发起方
            if request.user.id != call_data['caller_id']:
                async_to_sync(channel_layer.group_send)(
                    f"user_{call_data['caller_id']}",
                    {
                        "type": "voice.call.ended",
                        "call_id": call_id
                    }
                )
            # 通知被叫方
            if request.user.id != call_data['target_user_id']:
                async_to_sync(channel_layer.group_send)(
                    f"user_{call_data['target_user_id']}",
                    {
                        "type": "voice.call.ended",
                        "call_id": call_id
                    }
                )
        
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
        
        # 通过WebSocket将信令转发给对应用户
        channel_layer = get_channel_layer()
        if channel_layer:
            # 确定接收方ID
            recipient_id = (
                call_data['target_user_id'] if request.user.id == call_data['caller_id'] 
                else call_data['caller_id']
            )
            
            async_to_sync(channel_layer.group_send)(
                f"user_{recipient_id}",
                {
                    "type": f"webrtc.{signal_type}",
                    "call_id": call_id,
                    "data": signal_data,
                    "sender_id": request.user.id
                }
            )
        
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_call_history(request):
    """获取通话历史记录"""
    try:
        # 获取用户的所有通话记录，按时间倒序排列
        call_records = VoiceCallRecord.objects.filter(
            models.Q(caller=request.user) | models.Q(callee=request.user)
        ).order_by('-initiated_at')
        
        # 序列化数据
        records_data = []
        for record in call_records:
            records_data.append({
                'call_id': record.call_id,
                'caller': {
                    'id': record.caller.id,
                    'username': record.caller.username
                },
                'callee': {
                    'id': record.callee.id,
                    'username': record.callee.username
                },
                'status': record.status,
                'initiated_at': record.initiated_at.isoformat() if record.initiated_at else None,
                'accepted_at': record.accepted_at.isoformat() if record.accepted_at else None,
                'ended_at': record.ended_at.isoformat() if record.ended_at else None,
                'duration': record.call_duration,
                'is_caller': record.caller.id == request.user.id
            })
        
        return Response({
            'records': records_data,
            'total': len(records_data)
        })
        
    except Exception as e:
        return Response({
            'error': f'获取通话历史失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_calls(request):
    """获取当前活跃通话"""
    try:
        # 获取用户参与的活跃通话
        active_records = VoiceCallRecord.objects.filter(
            models.Q(caller=request.user) | models.Q(callee=request.user),
            status__in=['pending', 'accepted']
        ).order_by('-initiated_at')
        
        active_calls_data = []
        for record in active_records:
            active_calls_data.append({
                'call_id': record.call_id,
                'caller': {
                    'id': record.caller.id,
                    'username': record.caller.username
                },
                'callee': {
                    'id': record.callee.id,
                    'username': record.callee.username
                },
                'status': record.status,
                'initiated_at': record.initiated_at.isoformat() if record.initiated_at else None,
                'is_caller': record.caller.id == request.user.id
            })
        
        return Response({
            'active_calls': active_calls_data,
            'total': len(active_calls_data)
        })
        
    except Exception as e:
        return Response({
            'error': f'获取活跃通话失败: {str(e)}'
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