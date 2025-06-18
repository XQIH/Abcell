<template>
  <div class="storage-location-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>存储位置管理</h2>
    </div>

    <!-- 层级展示区域 -->
    <el-card class="hierarchy-card">
      <template #header>
        <div class="card-header">
          <span>存储层级结构</span>
          <el-button type="primary" size="small" icon="Plus" @click="showFreezerDialog">新增冰柜</el-button>
        </div>
      </template>

      <!-- 树形展示 -->
      <el-tree
          :data="locationTree"
          node-key="id"
          :props="treeProps"
          :expand-on-click-node="false"
          :highlight-current="true"
          @node-click="handleNodeClick"
      >
        <template #default="{ node, data }">
          <span class="custom-tree-node">
            <span>{{ node.label }}</span>

            <span class="node-actions">
              <el-button
                  type="primary"
                  link
                  size="small"
                  icon="Plus"
                  @click.stop="showAddDialog(data.type, data.id)"
              >
                添加子级
              </el-button>
              <el-button
                  type="primary"
                  link
                  size="small"
                  icon="Edit"
                  @click.stop="showEditDialog(data)"
              >
                编辑
              </el-button>
              <el-button
                  type="danger"
                  link
                  size="small"
                  icon="Delete"
                  @click.stop="showDeleteConfirm(data)"
              >
                删除
              </el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <!-- 新增对话框 -->
    <el-dialog
        v-model="addDialogVisible"
        :title="addDialogTitle"
        width="50%"
    >
      <el-form
          :model="addForm"
          :rules="addRules"
          ref="addFormRef"
          label-width="120px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="addForm.name"/>
        </el-form-item>
        <el-form-item label="编号" prop="number">
          <el-input v-model="addForm.number"/>
        </el-form-item>
        <!-- 新增行号和列号字段 -->
        <el-form-item label="行号" prop="row_num" v-if="addForm.level === 'cell'">
          <el-input-number v-model="addForm.row_num" :min="1"/>
        </el-form-item>
        <el-form-item label="列号" prop="col_num" v-if="addForm.level === 'cell'">
          <el-input-number v-model="addForm.col_num" :min="1"/>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="addForm.description" type="textarea" :rows="3"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAddForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog
        v-model="editDialogVisible"
        title="编辑存储位置"
        width="50%"
    >
      <el-form
          :model="editForm"
          :rules="editRules"
          ref="editFormRef"
          label-width="120px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="editForm.name"/>
        </el-form-item>
        <el-form-item label="编号" prop="number">
          <el-input v-model="editForm.number"/>
        </el-form-item>
        <!-- 新增行号和列号字段 -->
        <el-form-item label="行号" prop="row_num" v-if="editForm.level === 'cell'">
          <el-input-number v-model="editForm.row_num" :min="1"/>
        </el-form-item>
        <el-form-item label="列号" prop="col_num" v-if="editForm.level === 'cell'">
          <el-input-number v-model="editForm.col_num" :min="1"/>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="3"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEditForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, onMounted, computed} from 'vue'
import {useStore} from 'vuex'
import api from '@/api/api'
import {ElMessage, ElMessageBox} from "element-plus";

const store = useStore()

// 树形数据
const locationTree = ref([])
const treeProps = ref({
  label: 'name',
  children: 'children'
})

// 对话框相关
const addDialogVisible = ref(false)
const editDialogVisible = ref(false)
const addDialogTitle = ref('新增冰柜')
const addFormRef = ref(null)
const editFormRef = ref(null)

// 权限检查方法
const checkPermission = (requiredLevel) => {
  const hasPermission = store.getters.hasPermission(requiredLevel)
  if (!hasPermission) {
    ElMessage.warning('权限不足，无法执行此操作')
    return false
  }
  return true
}


// 新增表单
const addForm = ref({
  level: 'freezer', // freezer, level, column, drawer, box, cell
  parentId: null,
  name: '',
  number: '',
  description: '',
  row_num: 1,  // 新增行号
  col_num: 1   // 新增列号
})

// 编辑表单
const editForm = ref({
  id: null,
  level: '', // freezer, level, column, drawer, box, cell
  name: '',
  number: '',
  description: '',
  row_num: 1,  // 格子行号
  col_num: 1   // 格子列号
})

// 表单验证规则
const baseRules = {
  name: [
    {required: true, message: '请输入名称', trigger: 'blur'},
    {max: 100, message: '长度不超过100个字符', trigger: 'blur'}
  ],
  // 编号和描述不应该设为必填
  number: [
    {max: 50, message: '长度不超过50个字符', trigger: 'blur'}
  ],
  description: [
    {max: 500, message: '长度不超过500个字符', trigger: 'blur'}
  ],
  // 只有格子需要行号和列号
  row_num: [
    {required: editForm.value.level === 'cell', message: '请输入行号', trigger: 'blur'}
  ],
  col_num: [
    {required: editForm.value.level === 'cell', message: '请输入列号', trigger: 'blur'}
  ]
}

const addRules = ref({...baseRules})
const editRules = ref({...baseRules})

// 获取层级结构数据
const fetchLocationTree = async () => {
  try {
    const response = await api.getLocationTree()
    console.log(response)
    locationTree.value = response.data
  } catch (error) {
    console.error('获取存储位置树失败:', error)
    ElMessage.error('获取存储位置树失败')
  }
}

// 显示新增对话框
// 新增专门显示冰柜对话框的方法
const showFreezerDialog = () => {
  if (!checkPermission(1)) return // 1级权限才能新增冰柜
  addForm.value = {
    level: 'freezer',
    parentId: null,
    name: '',
    number: '',
    description: ''
  }
  addDialogTitle.value = '新增冰柜'
  addDialogVisible.value = true
}

// 修改原来的showAddDialog方法，只用于添加子级
const showAddDialog = (currentLevel, parentId = null) => {
  if (!checkPermission(2)) return // 2级权限才能添加子级
  // 定义层级关系映射
  const levelHierarchy = {
    'freezer': 'level',    // 冰柜下添加层
    'level': 'column',     // 层下添加列
    'column': 'drawer',    // 列下添加抽屉
    'drawer': 'box',       // 抽屉下添加盒子
    'box': 'cell',         // 盒子下添加格子
    'cell': null           // 格子不能再添加子级
  }

  const nextLevel = levelHierarchy[currentLevel]
  if (!nextLevel) {
    ElMessage.warning('当前层级不能再添加子级')
    return
  }

  addForm.value = {
    level: nextLevel,  // 这里改为下一级类型
    parentId,
    name: '',
    number: '',
    description: ''
  }

  // 根据下一级类型设置对话框标题
  const levelNames = {
    'freezer': '冰柜',
    'level': '层',
    'column': '列',
    'drawer': '抽屉',
    'box': '盒子',
    'cell': '格子'
  }
  addDialogTitle.value = `新增${levelNames[nextLevel]}`
  addDialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (data) => {
  if (!checkPermission(2)) return // 2级权限才能编辑
  editForm.value = {
    id: data.id,
    level: data.type,
    name: data.name,
    number: data.number || '',
    description: data.description || '',
    // 确保包含所有可能需要的字段
    row_num: data.row_num || 1,
    col_num: data.col_num || 1
  }
  editDialogVisible.value = true
}

// 提交新增表单
const submitAddForm = async () => {
  try {
    await addFormRef.value.validate()

    let apiMethod, params = {
      name: addForm.value.name,
      number: addForm.value.number,
      description: addForm.value.description
    }

    // 根据层级调用不同的API
    switch (addForm.value.level) {
      case 'freezer':
        params.number = addForm.value.number
        apiMethod = api.createFreezer1
        break
      case 'level':
        params.freezer = addForm.value.parentId
        apiMethod = api.createLevel
        break
      case 'column':
        params.level = addForm.value.parentId
        apiMethod = api.createColumn
        break
      case 'drawer':
        params.column = addForm.value.parentId
        apiMethod = api.createDrawer
        break
      case 'box':
        params.drawer = addForm.value.parentId
        apiMethod = api.createBox
        break
      case 'cell':
        params.box = addForm.value.parentId
        params.row_num = addForm.value.row_num  // 添加行号
        params.col_num = addForm.value.col_num  // 添加列号
        apiMethod = api.createCell1
        break
    }

    await apiMethod(params)
    ElMessage.success('添加成功')
    addDialogVisible.value = false
    fetchLocationTree() // 刷新树形数据
  } catch (error) {
    if (error.response) {
      if (error.response.status === 400) {
        for (const [field, errors] of Object.entries(error.response.data)) {
          ElMessage.error(`${field}: ${errors}`)
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

// 提交编辑表单
const submitEditForm = async () => {
  try {
    await editFormRef.value.validate()

    let apiMethod, params = {
      id: editForm.value.id,
      name: editForm.value.name,
      number: editForm.value.number,  // 确保包含编号
      description: editForm.value.description
    }

    // 如果是格子，添加行号和列号
    if (editForm.value.level === 'cell') {
      params.row_num = editForm.value.row_num
      params.col_num = editForm.value.col_num
    }

    // 根据层级调用不同的API
    switch (editForm.value.level) {
      case 'freezer':
        params.number = editForm.value.number
        apiMethod = api.updateFreezer1
        break
      case 'level':
        apiMethod = api.updateLevel
        break
      case 'column':
        apiMethod = api.updateColumn
        break
      case 'drawer':
        apiMethod = api.updateDrawer
        break
      case 'box':
        apiMethod = api.updateBox
        break
      case 'cell':
        apiMethod = api.updateCell1
        break
    }

    await apiMethod(params)
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    fetchLocationTree() // 刷新树形数据
  } catch (error) {
    if (error.response) {
      if (error.response.status === 400) {
        for (const [field, errors] of Object.entries(error.response.data)) {
          ElMessage.error(`${field}: ${errors}`)
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

// 显示删除确认
const showDeleteConfirm = (data) => {
  if (!checkPermission(2)) return // 2级权限才能删除
  ElMessageBox.confirm(`确定要删除 ${data.name} 吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      let apiMethod
      switch (data.type) {
        case 'freezer':
          apiMethod = api.deleteFreezer
          break
        case 'level':
          apiMethod = api.deleteLevel
          break
        case 'column':
          apiMethod = api.deleteColumn
          break
        case 'drawer':
          apiMethod = api.deleteDrawer
          break
        case 'box':
          apiMethod = api.deleteBox
          break
        case 'cell':
          apiMethod = api.deleteCell1
          break
      }

      await apiMethod(data.id)
      ElMessage.success('删除成功')
      fetchLocationTree() // 刷新树形数据
    } catch (error) {
      if (error.response) {
        if (error.response.status === 400) {
          for (const [field, errors] of Object.entries(error.response.data)) {
            ElMessage.error(`${field}: ${errors}`)
          }
        } else {
          ElMessage.error(`操作失败: ${error.response.statusText}`)
        }
      } else if (error.name !== 'Error') { // 忽略表单验证错误
        console.error('操作失败:', error)
        ElMessage.error('操作失败')
      }
    }
  }).catch(() => {
  })
}

// 节点点击事件
const handleNodeClick = (data) => {
  console.log('点击节点:', data)
}
onMounted(() => {
  console.log('当前权限级别:', store.state.user.permission_level)
})
// 初始化数据
onMounted(() => {
  fetchLocationTree()
})
</script>

<style scoped lang="scss">
.storage-location-container {
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

.hierarchy-card {
  border-radius: 8px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;

  .node-actions {
    display: none;
  }

  &:hover .node-actions {
    display: block;
  }
}

:deep(.el-tree-node__content) {
  height: 36px;
}
</style>