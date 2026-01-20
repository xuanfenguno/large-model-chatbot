import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessageBox } from 'element-plus'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: {
      requiresAuth: false,
      title: '首页'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: {
      requiresAuth: false,
      title: '登录'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: {
      requiresAuth: false,
      title: '注册'
    }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/Chat.vue'),
    meta: {
      requiresAuth: true,
      title: '聊天'
    }
  },
  {
    path: '/voice-chat',
    name: 'VoiceChat',
    component: () => import('../views/VoiceChat.vue'),
    meta: {
      requiresAuth: true,
      title: '语音助手'
    }
  },
  {
    path: '/video-chat',
    name: 'VideoChat',
    component: () => import('../views/VideoChat.vue'),
    meta: {
      requiresAuth: true,
      title: '视频通话'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: {
      requiresAuth: true,
      title: '设置'
    }
  },
  {
    path: '/user-agreement',
    name: 'UserAgreement',
    component: () => import('../views/UserAgreement.vue'),
    meta: {
      requiresAuth: false,
      title: '用户协议'
    }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue'),
    meta: {
      requiresAuth: false,
      title: '忘记密码'
    }
  },
  {
    path: '/privacy-policy',
    name: 'PrivacyPolicy',
    component: () => import('../views/PrivacyPolicy.vue'),
    meta: {
      requiresAuth: false,
      title: '隐私政策'
    }
  },
  {
    path: '/ai-test',
    name: 'AITest',
    component: () => import('../views/AITest.vue'),
    meta: {
      requiresAuth: false,
      title: 'API测试'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title + ' - AI聊天机器人'
  }
  
  // 检查路由保护
  if (to.meta.requiresAuth) {
    // 添加调试信息
    console.log('路由守卫检查认证状态:', {
      path: to.path,
      token: authStore.token,
      user: authStore.user,
      isLoggedIn: authStore.isLoggedIn,
      localStorageToken: localStorage.getItem('token'),
      localStorageUser: localStorage.getItem('user')
    })
    
    // 更可靠的认证检查：同时检查store和localStorage
    const hasValidToken = authStore.token || localStorage.getItem('token')
    const hasValidUser = authStore.user || localStorage.getItem('user')
    const isAuthenticated = hasValidToken && hasValidUser
    
    console.log('认证检查结果:', {
      hasValidToken: !!hasValidToken,
      hasValidUser: !!hasValidUser,
      isAuthenticated
    })
    
    if (!isAuthenticated) {
      console.log('用户未登录，跳转到登录页面')
      // 如果用户未登录，直接跳转到登录页面
      next({ name: 'Login', query: { redirect: to.fullPath } })
    } else {
      console.log('用户已登录，允许访问')
      
      // 确保认证状态同步
      if (!authStore.token && localStorage.getItem('token')) {
        authStore.token = localStorage.getItem('token')
        authStore.user = JSON.parse(localStorage.getItem('user') || 'null')
        console.log('已从localStorage恢复认证状态')
      }
      
      next()
    }
  } else {
    next()
  }
})

export default router