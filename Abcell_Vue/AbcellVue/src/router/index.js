// 在文件顶部添加store导入
import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'  // 添加这行

const routes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),  // 确保组件存在
    meta: { requiresAuth: true }
  },
  {
    path: '/cell/inventory',
    name: 'CellInventory',
    component: () => import('@/views/cell/Inventory.vue'),
    meta: { title: '细胞库存' }
  },
  {
    path: '/cell/out',
    name: 'CellOut',
    component: () => import('@/views/cell/Out.vue'),
    meta: { title: '细胞出库' }
  },
  {
    path: '/cell/type',
    name: 'CellType',
    component: () => import('@/views/cell/Type.vue'),
    meta: { title: '细胞类型' }
  },
  {
    path: '/storage/freezer',
    name: 'Freezer',
    component: () => import('@/views/storage/Freezer.vue'),
    meta: { title: '冰柜管理' }
  },
  {
    path: '/storage/location',
    name: 'StorageLocation',
    component: () => import('@/views/storage/Location.vue'),
    meta: { title: '存储位置' }
  },
  {
    path: '/user',
    name: 'UserManagement',
    component: () => import('@/views/user/Management.vue'),
    meta: { title: '用户管理', requireAuth: true, requiredLevel: 3 }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { title: '注册' }
  },
  // {
  //   path: '/user/profile',
  //   name: 'UserProfile',
  //   component: () => import('@/views/user/Profile.vue'),
  //   meta: { title: '个人中心' }
  // }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token') || store.state.user.token
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router