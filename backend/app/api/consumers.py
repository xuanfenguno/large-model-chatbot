import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class VoiceCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """建立WebSocket连接"""
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            # 创建用户特定的组
            self.user_group_name = f"user_{self.user.id}"
            
            # 加入用户组
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"User {self.user.username} connected to voice call WebSocket")
        else:
            await self.close()

    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        logger.info(f"User {self.user.username} disconnected from voice call WebSocket")

    async def receive(self, text_data):
        """接收客户端消息"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'voice_call_initiate':
                await self.initiate_voice_call(data)
            elif message_type == 'voice_call_answer':
                await self.answer_voice_call(data)
            elif message_type == 'voice_call_reject':
                await self.reject_voice_call(data)
            elif message_type == 'voice_call_end':
                await self.end_voice_call(data)
            elif message_type == 'webrtc_offer':
                await self.webrtc_offer(data)
            elif message_type == 'webrtc_answer':
                await self.webrtc_answer(data)
            elif message_type == 'webrtc_ice_candidate':
                await self.webrtc_ice_candidate(data)
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    # 语音通话相关处理
    async def voice_call_incoming(self, event):
        """处理 incoming-call 事件"""
        await self.send(text_data=json.dumps({
            'type': 'incoming_call',
            'call_id': event['call_id'],
            'caller_username': event['caller_username']
        }))

    async def voice_call_accepted(self, event):
        """处理 call-accepted 事件"""
        await self.send(text_data=json.dumps({
            'type': 'call_accepted',
            'call_id': event['call_id']
        }))

    async def voice_call_rejected(self, event):
        """处理 call-rejected 事件"""
        await self.send(text_data=json.dumps({
            'type': 'call_rejected',
            'call_id': event['call_id']
        }))

    async def voice_call_ended(self, event):
        """处理 call-ended 事件"""
        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'call_id': event['call_id']
        }))

    # WebRTC信令处理
    async def webrtc_offer(self, event):
        """处理 offer 事件"""
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'call_id': event['call_id'],
            'offer': event['data']
        }))

    async def webrtc_answer(self, event):
        """处理 answer 事件"""
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'call_id': event['call_id'],
            'answer': event['data']
        }))

    async def webrtc_ice_candidate(self, event):
        """处理 ice-candidate 事件"""
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'call_id': event['call_id'],
            'candidate': event['data']
        }))

    # 客户端请求处理
    async def initiate_voice_call(self, data):
        """发起语音通话"""
        target_user_id = data.get('target_user_id')
        call_id = data.get('call_id')

        # 验证目标用户是否存在
        target_user = await self.get_user(target_user_id)
        if not target_user:
            await self.send(text_data=json.dumps({
                'error': '目标用户不存在'
            }))
            return

        # 通知目标用户
        await self.channel_layer.group_send(
            f"user_{target_user_id}",
            {
                "type": "voice.call.incoming",
                "call_id": call_id,
                "caller_username": self.user.username
            }
        )

        await self.send(text_data=json.dumps({
            'type': 'call_initiated',
            'call_id': call_id
        }))

    async def answer_voice_call(self, data):
        """接听语音通话"""
        call_id = data.get('call_id')

        # 通知发起方
        # 这里需要从数据库或缓存中获取通话信息以确定发起方
        # 为了简化，我们假设知道发起方ID
        # 在实际实现中，需要从active_calls中获取信息
        caller_id = data.get('caller_id')  # 这里应该是从缓存中获取
        if caller_id:
            await self.channel_layer.group_send(
                f"user_{caller_id}",
                {
                    "type": "voice.call.accepted",
                    "call_id": call_id
                }
            )

        await self.send(text_data=json.dumps({
            'type': 'call_answered',
            'call_id': call_id
        }))

    async def reject_voice_call(self, data):
        """拒绝语音通话"""
        call_id = data.get('call_id')

        # 通知发起方
        caller_id = data.get('caller_id')  # 这里应该是从缓存中获取
        if caller_id:
            await self.channel_layer.group_send(
                f"user_{caller_id}",
                {
                    "type": "voice.call.rejected",
                    "call_id": call_id
                }
            )

        await self.send(text_data=json.dumps({
            'type': 'call_rejected',
            'call_id': call_id
        }))

    async def end_voice_call(self, data):
        """结束语音通话"""
        call_id = data.get('call_id')

        # 通知对方
        other_user_id = data.get('other_user_id')  # 这里应该是从缓存中获取
        if other_user_id:
            await self.channel_layer.group_send(
                f"user_{other_user_id}",
                {
                    "type": "voice.call.ended",
                    "call_id": call_id
                }
            )

        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'call_id': call_id
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        """异步获取用户"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None