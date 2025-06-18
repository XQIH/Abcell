<template>
  <div class="user-management-container">
    <!-- 页面标题和操作按钮 -->
    <div class="page-header">
      <h2>用户管理</h2>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="handleAdd">新增用户</el-button>
      </div>
    </div>

    <!-- 搜索和过滤区域 -->
    <el-card class="search-card">
      <el-form :model="searchForm" :inline="true">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="searchForm.email" placeholder="请输入邮箱" clearable />
        </el-form-item>
        <el-form-item label="权限级别">
          <el-select v-model="searchForm.permission_level" placeholder="请选择权限级别" clearable>
            <el-option label="1级权限" :value="1" />
            <el-option label="2级权限" :value="2" />
            <el-option label="3级权限" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格区域 -->
    <el-card class="table-card">
      <el-table
        :data="tableData"
        border
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="phone" label="电话" width="150" />
        <el-table-column prop="gender" label="性别" width="100">
          <template #default="{ row }">
            <el-tag :type="row.gender === '男' ? '' : 'danger'">
              {{ row.gender || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="permission_level" label="权限级别" width="120">
          <template #default="{ row }">
            <el-tag :type="getPermissionTag(row.permission_level)">
              {{ row.permission_level_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
              :disabled="row.id.toString() === currentUserId?.toString()"
            >
              删除
            </el-button>
            <el-button
              size="small"
              type="warning"
              @click="handleResetPassword(row)"
            >
              重置密码
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页控件 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="50%"
    >
      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="120px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="权限级别" prop="permission_level">
          <el-select v-model="form.permission_level" placeholder="请选择权限级别">
            <el-option label="1级权限" :value="1" />
            <el-option label="2级权限" :value="2" />
            <el-option label="3级权限" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogTitle === '新增用户'">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="resetPwdDialogVisible"
      title="重置密码"
      width="40%"
    >
      <el-form
        :model="resetPwdForm"
        :rules="resetPwdRules"
        ref="resetPwdFormRef"
        label-width="120px"
      >
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="resetPwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="resetPwdForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resetPwdDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitResetPassword">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, onMounted, computed, provide} from 'vue'
import { useStore} from 'vuex'
import api from '@/api/api'
import {ElMessage} from "element-plus";

const store = useStore()

// 当前用户ID
const currentUserId = store.state.user.id || localStorage.getItem('id')
console.log('id',currentUserId)
// 表格数据
const tableData = ref([])
console.log(tableData)
// 搜索表单
const searchForm = ref({
  username: '',
  email: '',
  permission_level: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)

// 对话框相关
const dialogVisible = ref(false)
const resetPwdDialogVisible = ref(false)
const dialogTitle = ref('新增用户')
const formRef = ref(null)
const resetPwdFormRef = ref(null)

// 表单数据
const form = ref({
  id: null,
  username: '',
  email: '',
  phone: '',
  gender: '男',
  permission_level: 1,
  password: ''
})

// 重置密码表单
const resetPwdForm = ref({
  user_id: null,
  new_password: '',
  confirm_password: ''
})

// 表单验证规则
const rules = {
  username: [
    {required: true, message: '请输入用户名', trigger: 'blur'},
    {max: 255, message: '长度不超过255个字符', trigger: 'blur'}
  ],
  email: [
    {required: true, message: '请输入邮箱', trigger: 'blur'},
    {type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change']}
  ],
  phone: [
    {pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur'}
  ],
  permission_level: [
    {required: true, message: '请选择权限级别', trigger: 'change'}
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'},
    {min: 6, message: '密码长度不能少于6位', trigger: 'blur'}
  ]
}

const resetPwdRules = {
  new_password: [
    {required: true, message: '请输入新密码', trigger: 'blur'},
    {min: 6, message: '密码长度不能少于6位', trigger: 'blur'}
  ],
  confirm_password: [
    {required: true, message: '请确认密码', trigger: 'blur'},
    {validator: validateConfirmPassword, trigger: 'blur'}
  ]
}

// 确认密码验证
function validateConfirmPassword(rule, value, callback) {
  if (value !== resetPwdForm.value.new_password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

// 获取权限级别标签样式
const getPermissionTag = (level) => {
  const map = {
    1: '',
    2: 'success',
    3: 'warning'
  }
  return map[level] || ''
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      username: searchForm.value.username,
      email: searchForm.value.email,
      permission_level: searchForm.value.permission_level
    }

     // 移除空值参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })

    const response = await api.getUsers(params)
    tableData.value = response.data
    console.log(response.data)
    total.value = response.data.length
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    username: '',
    email: '',
    permission_level: ''
  }
  handleSearch()
}

// 分页大小变化
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

// 当前页变化
const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

// 新增用户
const handleAdd = () => {
  dialogTitle.value = '新增用户'
  form.value = {
    id: null,
    username: '',
    email: '',
    phone: '',
    gender: '男',
    permission_level: 1,
    password: ''
  }
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (row) => {
  dialogTitle.value = '编辑用户'
  form.value = {...row}
  dialogVisible.value = true
}

// 删除用户
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.deleteUser(row.id)
    ElMessage.success('删除成功')
    fetchData() // 刷新数据
  } catch (error) {
    if (error !== 'cancel') { // 忽略用户取消的情况
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 重置密码
const handleResetPassword = (row) => {
  resetPwdForm.value = {
    user_id: row.id,
    new_password: '',
    confirm_password: ''
  }
  resetPwdDialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()

    const userData = {
      username: form.value.username,
      email: form.value.email,
      phone: form.value.phone,
      gender: form.value.gender,
      permission_level: form.value.permission_level
    }

    if (dialogTitle.value === '新增用户') {
      userData.password = form.value.password
      await api.register(userData)
      ElMessage.success('添加成功')
    } else {
      await api.updateUser(form.value.id, userData)
      ElMessage.success('更新成功')
    }

    dialogVisible.value = false
    fetchData() // 刷新数据
  } catch (error) {
    if (error.response) {
      if (error.response.status === 400) {
        for (const [field, errors] of Object.entries(error.response.data)) {
          ElMessage.error(`${field}: ${errors.join}`)
        }
      } else {
        ElMessage.error(`操作失败: ${error.response.statusText}`)
      }
    } else if (error.username !== 'Error') { // 忽略表单验证错误
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 提交重置密码
const submitResetPassword = async () => {
  try {
    await resetPwdFormRef.value.validate()

    await api.resetPassword(
        resetPwdForm.value.user_id,
        resetPwdForm.value.new_password,
        resetPwdForm.value.confirm_password
    )

    ElMessage.success('密码重置成功')
    resetPwdDialogVisible.value = false
  } catch (error) {
    if (error.response) {
      if (error.response.status === 400) {
        for (const [field, errors] of Object.entries(error.response.data)) {
          ElMessage.error(`${field}: ${errors.join(', ')}`)
        }
      } else {
        ElMessage.error(`操作失败: ${error.response.statusText}`)
      }
    } else if (error.username !== 'Error') { // 忽略表单验证错误
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }
}


// 初始化数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.user-management-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h2 {
    margin: 0;
    font-size: 24px;
    color: #303133;
  }
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;

  .el-form {
    display: flex;
    flex-wrap: wrap;
  }

  .el-form-item {
    margin-right: 20px;
    margin-bottom: 0;
  }
}

.table-card {
  border-radius: 8px;

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}

.el-table {
  :deep(.cell) {
    white-space: nowrap;
  }
}

.el-tag {
  margin: 2px;
}
</style>