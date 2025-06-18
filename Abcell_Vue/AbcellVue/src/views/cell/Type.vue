<template>
  <div class="cell-type-container">
    <!-- 页面标题和操作按钮 -->
    <div class="page-header">
      <h2>细胞类型管理</h2>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="handleAdd">新增类型</el-button>
      </div>
    </div>

    <!-- 搜索和过滤区域 -->
    <el-card class="search-card">
      <el-form :model="searchForm" :inline="true">
        <el-form-item label="类型名称">
          <el-input v-model="searchForm.name" placeholder="请输入类型名称" clearable />
        </el-form-item>
        <el-form-item label="细胞类别">
          <el-select v-model="searchForm.category" placeholder="请选择细胞类别" clearable>
            <el-option label="原代细胞" value="primary" />
            <el-option label="人源细胞" value="human" />
            <el-option label="小鼠细胞" value="mouse" />
            <el-option label="大鼠细胞" value="rat" />
            <el-option label="贴壁细胞" value="adherent" />
            <el-option label="悬浮细胞" value="suspension" />
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
        <el-table-column prop="name" label="类型名称" width="180" />
        <el-table-column prop="category" label="细胞类别" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTag(row.category)">{{ getCategoryName(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述"> 
          <template #default="{ row }">
            <el-tooltip :content="row.description" placement="top">
              {{ row.description }}
            </el-tooltip>
          </template>                  
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" >
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
        <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
        <el-form-item label="类型名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="细胞类别" prop="category">
          <el-select
              v-model="form.category"
              placeholder="请选择细胞类别"
          >
            <el-option label="原代细胞" value="primary" />
            <el-option label="人源细胞" value="human" />
            <el-option label="小鼠细胞" value="mouse" />
            <el-option label="大鼠细胞" value="rat" />
            <el-option label="贴壁细胞" value="adherent" />
            <el-option label="悬浮细胞" value="suspension" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">  
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/api'
import {ElMessage, ElMessageBox} from "element-plus";
import { formatDate, formatDateTime } from '@/utils/dateUtils';
import { useStore } from 'vuex'
const store = useStore()

// 权限检查方法
const checkPermission = (requiredLevel) => {
  const hasPermission = store.getters.hasPermission(requiredLevel)
  if (!hasPermission) {
    ElMessage.warning('权限不足，无法执行此操作')
    return false
  }
  return true
}

// 表格数据
const tableData = ref([])

// 搜索表单
const searchForm = ref({
  name: '',
  category: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新增细胞类型')
const formRef = ref(null)

// 表单数据
const form = ref({
  name: '',
  category: '',
  description: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入类型名称', trigger: 'blur' },
    { max: 100, message: '长度不超过100个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择细胞类别', trigger: 'change' }
  ],
  description: [
    { max: 500, message: '长度不超过500个字符', trigger: 'blur' }
  ]
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      name: searchForm.value.name,
      category: searchForm.value.category
    }

    const response = await api.getCellTypes(params)
    tableData.value = response.data
    console.log(response.data)
    total.value = response.data.length
  } catch (error) {
    console.error('获取细胞类型失败:', error)
    ElMessage.error('获取细胞类型失败')
  } finally {
    loading.value = false
  }
}

// 获取类别名称
const getCategoryName = (category) => {
  const map = {
    'primary': '原代细胞',
    'human': '人源细胞',
    'mouse': '小鼠细胞',
    'rat': '大鼠细胞',
    'adherent': '贴壁细胞',
    'suspension': '悬浮细胞'
  }
  return map[category] || category
}

// 获取类别标签样式
const getCategoryTag = (category) => {
  const map = {
    'primary': '',
    'human': 'success',
    'mouse': 'info',
    'rat': 'warning',
    'adherent': 'danger',
    'suspension': ''
  }
  return map[category] || ''
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    name: '',
    category: ''
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

// 新增类型
const handleAdd = () => {
  if (!checkPermission(2)) return // 2级权限才能新增细胞类型
  dialogTitle.value = '新增细胞类型'
  form.value = {
    name: '',
    category: '',
    description: ''
  }
  dialogVisible.value = true
}

// 编辑类型
const handleEdit = (row) => {
  if (!checkPermission(2)) return // 2级权限才能编辑
  dialogTitle.value = '编辑细胞类型'
  form.value = { ...row }
  dialogVisible.value = true
}

// 删除类型
const handleDelete = async (row) => {
    if (!checkPermission(1)) return // 1级权限才能删除
  try {
    await ElMessageBox.confirm(`确定要删除细胞类型 "${row.name}" 吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.deleteCellType(row.id)
    ElMessage.success('删除成功')
    fetchData() // 刷新数据
  } catch (error) {
    if (error !== 'cancel') { // 忽略用户取消的情况
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()

    if (dialogTitle.value === '新增细胞类型') {
      await api.createCellType(form.value)
      ElMessage.success('添加成功')
    } else {
      await api.updateCellType(form.value.id, form.value)
      ElMessage.success('更新成功')
    }

    dialogVisible.value = false
    fetchData() // 刷新数据
  } catch (error) {
    if (error.response) {
      if (error.response.status === 400) {
        for (const [field, errors] of Object.entries(error.response.data)) {
          ElMessage.error(`${field}: ${errors.join(', ')}`)
        }
      } else {
        ElMessage.error(`操作失败: ${error.response.statusText}`)
      }
    } else if (error.name !== 'Error') { // 忽略表单验证错误
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
.cell-type-container {
  padding: 20px;
}
/* 统一设置所有选择框的默认宽度 */
.cell-type-container :deep(.el-select) {
  width: 200px; /* 默认宽度 */
}

///* 特定选择框的特殊宽度 */
//.cell-type-container :deep(.category-select) {
//  width: 10px;
//}
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