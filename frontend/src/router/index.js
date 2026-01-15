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
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    ElMessageBox.alert('请先登录', '提示', {
      confirmButtonText: '去登录',
      type: 'warning'
    }).then(() => {
      next({ name: 'Login', query: { redirect: to.fullPath } })
    }).catch(() => {
      next({ name: 'Login' })
    })
  } else {
    next()
  }
})

export default router