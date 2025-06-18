<template>
  <div class="register-container">
    <el-card class="register-card">
      <div class="register-header">
        <h2>用户注册</h2>
        <p>创建您的Abcell账号</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input
              v-model="form.username"
              placeholder="用户名"
              :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="email">
          <el-input
              v-model="form.email"
              placeholder="邮箱"
              :prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item prop="phone">
          <el-input
              v-model="form.phone"
              placeholder="电话"
              :prefix-icon="Phone"
          />
        </el-form-item>

        <el-form-item prop="gender">
          <el-select
              v-model="form.gender"
              placeholder="请选择性别"
              style="width: 100%"
          >
            <el-option label="男" value="男"/>
            <el-option label="女" value="女"/>
            <el-option label="其他" value="其他"/>
          </el-select>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              :prefix-icon="Lock"
              show-password
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="确认密码"
              :prefix-icon="Lock"
              show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
              type="primary"
              :loading="loading"
              class="register-btn"
              @click="submitForm"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-footer">
        <span>已有账号？</span>
        <el-button type="text" @click="$router.push('/login')">立即登录</el-button>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import api from '@/api/api'
import {ElMessage} from 'element-plus'
import {User, Message, Phone, Lock} from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref(null)

const form = ref({
  username: '',  // 使用username而不是name
  email: '',
  password: '',
  confirmPassword: '',
  phone:'',
  gender:'',
})

// 密码验证规则
const validatePassword = (rule, value, callback) => {
  if (value !== form.value.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [  // 修改为username验证
    {required: true, message: '请输入用户名', trigger: 'blur'}
  ],
  email: [
    {required: true, message: '请输入邮箱', trigger: 'blur'},
    {type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change']}
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'},
    {min: 6, message: '密码长度不能少于6位', trigger: 'blur'}
  ],
  confirmPassword: [
    {required: true, message: '请确认密码', trigger: 'blur'},
    {validator: validatePassword, trigger: 'blur'}
  ]
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
    const response = await api.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      gender: form.value.gender,
      phone: form.value.phone,
    })

    ElMessage.success('注册成功')
    router.push('/login')
  } catch (error) {
    if (error.response) {
      if (error.response.status === 400) {
        for (const [field, errors] of Object.entries(error.response.data)) {
          ElMessage.error(`${field}: ${errors.join(', ')}`)
        }
      } else {
        ElMessage.error(`注册失败: ${error.response.statusText}`)
      }
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.register-card {
  width: 450px;
  padding: 20px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  margin-bottom: 10px;
  color: #409EFF;
}

.register-btn {
  width: 100%;
}

.register-footer {
  text-align: center;
  margin-top: 20px;
  color: #909399;
}
</style>