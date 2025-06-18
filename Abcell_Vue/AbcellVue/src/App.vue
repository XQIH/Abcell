<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <el-container>
      <el-header class="app-header">
        <div class="logo">
          <el-icon class="menu-icon" :size="22">
            <Menu/>
          </el-icon>
          <span>ABCell台账管理系统</span>
        </div>
        <div class="user-info">
          <template v-if="isLoggedIn">
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="el-dropdown-link">
                <el-avatar :icon="UserFilled"/>
                <span class="username">{{ userName }}</span>
                <el-icon class="el-icon--right">
                  <ArrowDown/>
                </el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="userCenter">个人中心</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <span class="not-logged-in">未登录</span>
          </template>
        </div>
      </el-header>

      <!-- 主体内容 -->
      <el-container>
        <!-- 侧边栏菜单 -->
        <el-aside :width="asideWidth" class="app-sidebar">
          <el-menu
              :default-active="activeMenu"
              class="el-menu-vertical"
              background-color="#304156"
              text-color="#bfcbd9"
              active-text-color="#409EFF"
              :collapse="isCollapse"
              :router="true"
          >
            <el-menu-item index="/dashboard">
              <el-icon>
                <HomeFilled/>
              </el-icon>
              <span>首页概览</span>
            </el-menu-item>

            <el-sub-menu index="cell">
              <template #title>
                <el-icon>
                  <List/>
                </el-icon>
                <span>细胞管理</span>
              </template>
              <el-menu-item index="/cell/inventory">细胞库存</el-menu-item>
              <el-menu-item index="/cell/out">细胞出库</el-menu-item>
              <el-menu-item index="/cell/type">细胞类型</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="storage">
              <template #title>
                <el-icon>
                  <Files/>
                </el-icon>
                <span>存储管理</span>
              </template>
              <el-menu-item index="/storage/freezer">冰柜管理</el-menu-item>
              <el-menu-item index="/storage/location">存储位置</el-menu-item>
            </el-sub-menu>

            <el-menu-item index="/user">
              <el-icon>
                <User/>
              </el-icon>
              <span>用户管理</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主内容区 -->
        <el-main class="app-main">
          <!-- 面包屑导航 -->
          <el-breadcrumb separator="/" class="breadcrumb" v-if="$route.path !== '/dashboard'">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="(item, index) in breadcrumbList" :key="index">
              {{ item }}
            </el-breadcrumb-item>
          </el-breadcrumb>

          <!-- 页面内容 -->
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component"/>
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import {ref, computed, watch, onMounted, provide, inject} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useStore} from 'vuex'
import {
  Menu,
  UserFilled,
  ArrowDown,
  HomeFilled,
  List,
  Files,
  User
} from '@element-plus/icons-vue'
import {ElLoading, ElMessage, ElMessageBox} from 'element-plus'
const refreshApp = inject('refreshApp')
const router = useRouter()
const route = useRoute()
const store = useStore()

// 添加登录状态
const isLoggedIn = ref()
if (store.state.user.username){
  isLoggedIn.value = true
}else {
  isLoggedIn.value = false
}

// 修改userName为计算属性，从store获取
const userName = computed(() => store.state.user?.username)
// const userPermission = ref(3) // 用户权限级别，1-3
const isCollapse = ref(false) // 是否折叠菜单
const breadcrumbList = ref([]) // 面包屑导航列表

// 计算属性
const activeMenu = computed(() => route.path)
const asideWidth = computed(() => isCollapse.value ? '64px' : '220px')

// 方法
const getBreadcrumb = () => {
  const matched = route.matched.filter(item => item.name)
  const first = matched[0]
  if (first && first.name !== 'Dashboard') {
    matched.unshift({path: '/dashboard', name: 'Dashboard'})
  }
  breadcrumbList.value = matched.map(item => {
    return item.meta && item.meta.title ? item.meta.title : item.name
  })
}

const handleCommand = (command) => {
  switch (command) {
    case 'userCenter':
      showUserCenter()
      break
    case 'logout':
      logout()
      break
  }
}

const showUserCenter = () => {
  router.push('/user/profile')
}


const logout = () => {
  
  ElMessageBox.confirm('确定要退出登录吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    // 显示加载状态
    const loading = ElLoading.service({
      lock: true,
      text: '正在退出登录...'
    })
    
    try {
      // 更新登录状态
      isLoggedIn.value = false
      // 清理localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('userId')
      localStorage.removeItem('username')
      localStorage.removeItem('permissionLevel')
      
      // 重置store状态
      store.commit('clearUserData')
      
      // 添加延迟确保UI更新
      await new Promise(resolve => setTimeout(resolve, 500))
      
      router.push('/login')

      ElMessage.success('退出成功')
    } finally {
      loading.close()
    }
  }).catch(() => {
  })
  
}


// 监听路由变化
watch(() => route.path, (newPath) => {
  getBreadcrumb()
  
  // 添加权限检查
  if (newPath === '/user') {
    const permissionLevel = store.state.user?.permission_level
    if (permissionLevel > 1) {
      ElMessage.warning('权限不足，无法访问用户管理')
      router.push('/dashboard')
    }
  }
})

// 初始化面包屑导航
getBreadcrumb()

onMounted(() => {
  // 添加store存在性检查
  if (!store) {
    console.error('Store is not available')
    router.push('/login')
    return
  }

  const token = store.state?.user?.token || localStorage.getItem('token')
  if (!token && router.currentRoute.value.path !== '/login' && router.currentRoute.value.path !== '/register') {
    router.push('/login')
  }
})
provide('refreshApp', () => {
  // 这里可以添加其他需要刷新的状态
  isLoggedIn.value = true

})
</script>

<style lang="scss">
/* 在原有样式基础上添加 */
.not-logged-in {
  color: #fff;
  font-size: 14px;
  cursor: default;
}
#app {
  height: 100vh;
  overflow: hidden;

  .app-header {
    background-color: #304156;
    color: #fff;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    border-bottom: 1px solid #1f2d3d;

    .logo {
      display: flex;
      align-items: center;
      font-size: 18px;
      font-weight: bold;

      .menu-icon {
        margin-right: 10px;
        cursor: pointer;
      }
    }

    .user-info {
      .el-dropdown-link {
        display: flex;
        align-items: center;
        color: #fff;
        cursor: pointer;

        .username {
          margin: 0 10px;
        }
      }
    }
  }

  .app-sidebar {
    background-color: #304156;
    height: calc(100vh - 60px);
    overflow-y: auto;
    transition: width 0.3s;

    .el-menu-vertical {
      border-right: none;
      height: 100%;
    }
  }

  .app-main {
    background-color: #f0f2f5;
    height: calc(100vh - 60px);
    overflow-y: auto;
    padding: 20px;

    .breadcrumb {
      margin-bottom: 20px;
      padding: 10px 15px;
      background-color: #fff;
      border-radius: 4px;
      box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
    }
  }
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-track {
  background-color: #f1f1f1;
}

/* 路由切换动画 */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>