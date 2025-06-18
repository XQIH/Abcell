<template>
  <div class="cell-out-container">
    <!-- 页面标题和操作按钮 -->
    <div class="page-header">
      <h2>细胞出库管理</h2>
      <div class="header-actions">
        <el-button type="primary" icon="Download" @click="handleOut">细胞出库</el-button>
        <el-button icon="Refresh" @click="refreshData">刷新数据</el-button>
      </div>
    </div>

    <!-- 搜索和过滤区域 -->
    <el-card class="search-card">
      <el-form :model="searchForm" :inline="true">
        <el-form-item label="细胞ID">
          <el-input v-model="searchForm.cellId" placeholder="请输入细胞ID" clearable />
        </el-form-item>
        <el-form-item label="接收人">
          <el-input v-model="searchForm.receiver" placeholder="请输入接收人" clearable />
        </el-form-item>
<!--        <el-form-item label="出库日期">-->
<!--          <el-date-picker-->
<!--            v-model="searchForm.dateRange"-->
<!--            type="daterange"-->
<!--            range-separator="至"-->
<!--            start-placeholder="开始日期"-->
<!--            end-placeholder="结束日期"-->
<!--            value-format="YYYY-MM-DD"-->
<!--          />-->
<!--        </el-form-item>-->
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
        <el-table-column prop="cell.cell_id" label="细胞ID" width="180">
          <template #default="{ row }">
            {{ row.cell_inventory.cell_id }}
          </template>
        </el-table-column>
        <el-table-column prop="cell.cell_type.name" label="细胞类型" width="120">
        <template #default="{ row }">
            <el-tag :type="getCategoryTag(row.cell_inventory.cell_type.name)">{{ getCategoryName(row.cell_inventory.cell_type.name) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="out_time" label="出库时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.out_time)}}
          </template>
        </el-table-column>
        <el-table-column prop="out_person.name" label="出库人" width="120" />
        <el-table-column prop="receiver" label="接收人" width="120" />
        <el-table-column prop="purpose" label="用途" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetails(row)">详情</el-button>
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

    <!-- 出库对话框 -->
    <el-dialog
      v-model="outDialogVisible"
      :title="outDialogTitle"
      width="50%"
    >
      <el-form
        :model="outForm"
        :rules="outRules"
        ref="outFormRef"
        label-width="120px"
      >
        <el-form-item label="选择细胞" prop="cell_id">
          <el-select
            v-model="outForm.cell_id"
            placeholder="请选择要出库的细胞"
            filterable
            remote
            :remote-method="searchCells"
            :loading="searchLoading"
          >
            <el-option
              v-for="cell in availableCells"
              :key="cell.id"
              :label="`${cell.cell_id} (${cell.cell_type.name}) - 位置: ${cell.storage_location}`"
              :value="cell.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="接收人" prop="receiver">
          <el-input v-model="outForm.receiver" />
        </el-form-item>
        <el-form-item label="用途" prop="purpose">
          <el-input v-model="outForm.purpose" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="outForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="outDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitOut">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="出库记录详情"
      width="50%"
    >
      <el-descriptions :column="1" border v-if="currentRecord">
        <el-descriptions-item label="细胞ID">{{ currentRecord.cell_inventory.cell_id }}</el-descriptions-item>
        <el-descriptions-item label="细胞类型">{{ currentRecord.cell_inventory.cell_type.name }}</el-descriptions-item>
        <el-descriptions-item label="存储位置">{{ currentRecord.cell_inventory.storage_location }}</el-descriptions-item>
        <el-descriptions-item label="出库时间">{{ formatDateTime(currentRecord.out_time) }}</el-descriptions-item>
        <el-descriptions-item label="出库人">{{ currentRecord.out_person.name }}</el-descriptions-item>
        <el-descriptions-item label="接收人">{{ currentRecord.receiver }}</el-descriptions-item>
        <el-descriptions-item label="用途">{{ currentRecord.purpose }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentRecord.notes || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/api'
import {ElMessage} from "element-plus";
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
const currentRecord = ref(null)
const availableCells = ref([])

// 搜索表单
const searchForm = ref({
  cellId: '',
  receiver: '',
  dateRange: []
})


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


// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)

// 对话框相关
const outDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const outDialogTitle = ref('细胞出库')
const searchLoading = ref(false)

// 出库表单
const outForm = ref({
  cell_id: '',
  receiver: '',
  purpose: '',
  notes: ''
})

// 表单验证规则
const outRules = {
  cell_id: [{ required: true, message: '请选择细胞', trigger: 'blur' }],
  receiver: [{ required: true, message: '请输入接收人', trigger: 'blur' }],
  purpose: [{ required: true, message: '请输入用途', trigger: 'blur' }]
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      cell_id: searchForm.value.cellId,
      receiver: searchForm.value.receiver,
      start_date: searchForm.value.dateRange?.[0],
      end_date: searchForm.value.dateRange?.[1]
    }

    const response = await api.getCellOutRecords(params)
    tableData.value = response.data
    console.log(response)
    total.value = response.data.length
  } catch (error) {
    console.error('获取出库记录失败:', error)
    ElMessage.error('获取出库记录失败')
  } finally {
    loading.value = false
  }
}

// 搜索可用细胞
const searchCells = async (query) => {
  if (!query) {
    availableCells.value = []
    return
  }

  searchLoading.value = true
  try {
    const response = await api.searchAvailableCells(query)
    availableCells.value = response.data
    console.log(response.data)
  } catch (error) {
    console.error('搜索细胞失败:', error)
    ElMessage.error('搜索细胞失败')
  } finally {
    searchLoading.value = false
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
    cellId: '',
    receiver: '',
    dateRange: []
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

// 刷新数据
const refreshData = () => {
  fetchData()
}

// 出库操作
const handleOut = () => {
  if (!checkPermission(2)) return // 2级权限才能出库
  outDialogTitle.value = '细胞出库'
  outForm.value = {
    cell_id: '',
    receiver: '',
    purpose: '',
    notes: ''
  }
  outDialogVisible.value = true
}

// 查看详情
const viewDetails = (row) => {
  currentRecord.value = row
  detailDialogVisible.value = true
}

const outFormRef = ref(null) // 新增这行
// 提交出库
const submitOut = async () => {
  try {
    await outFormRef.value.validate()
    console.log(outForm.value)
    // 转换数据格式：cell_id → cell_inventory
    const payload = {
      cell_inventory: outForm.value.cell_id,  // 改为后端需要的字段名
      receiver: outForm.value.receiver,
      purpose: outForm.value.purpose,
      notes: outForm.value.notes
    }
    // 调用出库API
    await api.createCellOutRecord(payload)
    ElMessage.success('出库成功')
    outDialogVisible.value = false
    fetchData() // 刷新数据
  } catch (error) {
    if (error.response) {
      if (error.response.status === 400) {
        for (const [field, errors] of Object.entries(error.response.data)) {
          ElMessage.error(`${field}: ${errors.join(', ')}`)
        }
      } else {
        ElMessage.error(`出库失败: ${error.response.statusText}`)
      }
    } else if (error.name !== 'Error') { // 忽略表单验证错误
      console.error('出库失败:', error)
      ElMessage.error('出库失败')
    }
  }
}

// 初始化数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.cell-out-container {
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
</style>