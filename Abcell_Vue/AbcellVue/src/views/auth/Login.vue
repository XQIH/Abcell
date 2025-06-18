<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <h2>登录</h2>
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" show-password />
        </el-form-item>
        <el-button type="primary" @click="submitForm">登录</el-button>
        <el-button @click="$router.push('/register')">注册</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref,inject } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/api'
import { ElMessage } from 'element-plus'  // 添加这行
import { useStore } from 'vuex'  // 添加这行

const router = useRouter()
const store = useStore()  // 添加这行
const formRef = ref(null)

const form = ref({
  email: '',
  password: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}
const refreshApp = inject('refreshApp')
const submitForm = async () => {
  try {
    const response = await api.login({
      email: form.value.email,
      password: form.value.password
    })
    
    // 修改登录成功处理
    if (response.data && response.data.access) {
      localStorage.setItem('token', response.data.access)
      localStorage.setItem('refreshToken', response.data.refresh)  // 添加这行
      store.commit('setToken', { 
        token: response.data.access,
        expiresIn: 3600 // 或其他过期时间
      })
      store.commit('setUserId', response.data.user_id)  // 确保这样调用
      store.commit('setUserData', {
        user_id: response.data.user_id,
        permission_level: response.data.permission_level,
        username: response.data.username,
        avatar: response.data.avatar // 添加这行
      })
      refreshApp()
      console.log('登录成功，权限级别：', response.data.permission_level)  // 添加这行
      ElMessage.success('登录成功')
      router.push('/dashboard')
    }
    else {
      throw new Error('无效的响应格式')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || error.message || '登录失败')
  }
}



</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.auth-card {
  width: 400px;
  padding: 20px;
}
</style>