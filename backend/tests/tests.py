"""
聊天机器人应用的单元测试
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Conversation, Message
from django.utils import timezone


class ModelTestCase(TestCase):
    """测试模型层的功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_conversation_creation(self):
        """测试会话创建"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation',
            model='gpt-3.5-turbo'
        )
        
        self.assertEqual(conversation.user, self.user)
        self.assertEqual(conversation.title, 'Test Conversation')
        self.assertEqual(conversation.model, 'gpt-3.5-turbo')
        self.assertIsNotNone(conversation.created_at)
        
    def test_message_creation(self):
        """测试消息创建"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation',
            model='gpt-3.5-turbo'
        )
        
        message = Message.objects.create(
            conversation=conversation,
            role='user',
            content='Hello, world!'
        )
        
        self.assertEqual(message.conversation, conversation)
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, 'Hello, world!')
        self.assertFalse(message.is_read)


class APITestCase(APITestCase):
    """测试API端点"""
    
    def setUp(self):
        """设置测试环境"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        
    def test_health_check_endpoint(self):
        """测试健康检查端点"""
        url = reverse('health-check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'ok')
        
    def test_login_view(self):
        """测试登录视图"""
        url = reverse('login-view')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        
    def test_register_view(self):
        """测试注册视图"""
        url = reverse('register-view')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        
        # 验证用户已创建
        self.assertTrue(User.objects.filter(username='newuser').exists())


class ConversationViewSetTestCase(APITestCase):
    """测试会话视图集"""
    
    def setUp(self):
        """设置测试环境"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_conversation(self):
        """测试创建会话"""
        url = reverse('conversation-list')
        data = {
            'title': 'Test Conversation',
            'model': 'gpt-3.5-turbo'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(Conversation.objects.first().user, self.user)
        
    def test_get_conversations(self):
        """测试获取会话列表"""
        # 创建一些会话
        Conversation.objects.create(
            user=self.user,
            title='Test 1',
            model='gpt-3.5-turbo'
        )
        Conversation.objects.create(
            user=self.user,
            title='Test 2',
            model='gpt-4'
        )
        
        url = reverse('conversation-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class MessageViewSetTestCase(APITestCase):
    """测试消息视图集"""
    
    def setUp(self):
        """设置测试环境"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation',
            model='gpt-3.5-turbo'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_message(self):
        """测试创建消息"""
        url = reverse('message-list')
        data = {
            'conversation': self.conversation.id,
            'role': 'user',
            'content': 'Hello, AI!'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().content, 'Hello, AI!')