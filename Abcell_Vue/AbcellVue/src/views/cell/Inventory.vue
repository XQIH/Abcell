<template>
  <div class="cell-inventory-container">
    <!-- 页面标题和操作按钮 -->
    <div class="page-header">
      <h2>细胞库存管理</h2>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="handleAdd">新增细胞</el-button>
        <el-button icon="Download">导出数据</el-button>
      </div>
    </div>

    <!-- 搜索和过滤区域 -->
    <el-card class="search-card">
      <el-form :model="searchForm" :inline="true">
        <el-form-item label="细胞ID">
          <el-input v-model="searchForm.cell_id" placeholder="请输入细胞ID" clearable/>
        </el-form-item>
<!--        <el-form-item label="细胞类型">-->
<!--          <el-select v-model="searchForm.cell_type" placeholder="请选择细胞类型" clearable>-->
<!--            <el-option label="原代细胞" value="原代细胞"/>-->
<!--            <el-option label="人源细胞" value="人源细胞"/>-->
<!--            <el-option label="小鼠细胞" value="小鼠细胞"/>-->
<!--            <el-option label="大鼠细胞" value="大鼠细胞"/>-->
<!--          </el-select>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="存储位置">-->
<!--          <el-cascader-->
<!--              v-model="form.storage_location"-->
<!--              :options="locationOptions"-->
<!--              :props="cascaderProps"-->
<!--              placeholder="请选择存储位置"-->
<!--              clearable-->
<!--              filterable-->
<!--          />-->
<!--        </el-form-item>-->
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="在库" value="in_stock"/>
            <el-option label="出库" value="out_stock"/>
            <el-option label="已销毁" value="destroyed"/>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">细胞类型分布</div>
          </template>
          <div class="chart-container" ref="typeChart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">细胞状态统计</div>
          </template>
          <div class="chart-container" ref="statusChart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据表格区域 -->
    <el-card class="table-card">
      <el-table
          :data="tableData"
          border
          style="width: 100%"
          v-loading="loading"
          @sort-change="handleSortChange"
      >
        <el-table-column prop="cell_id" label="细胞ID" width="100" sortable>
          <template #default="{ row }">
            <el-tooltip :content="row.cell_id" placement="top" :disabled="!row.cell_id || row.cell_id.length <= 10">
              <span>{{ row.cell_id?.length > 10 ? row.cell_id.substring(0, 10) + '...' : row.cell_id }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="cell_type" label="细胞类型" width="120">
          <template #default="{ row }">
            <el-tooltip :content="row.cell_type.name" placement="top" :disabled="!row.cell_type.name || row.cell_type.name.length <= 10">
            <el-tag :type="getCellTypeTag(row.cell_type.name)">{{ row.cell_type.name }}</el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="storage_location" label="存储位置" width="180">
          <template #default="{ row }">
            <el-tooltip :content="row.storage_location" placement="top">
              <span>{{ row.storage_location }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" sortable/>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'in_stock' ? 'success' : row.status === 'out_stock' ? 'warning' : 'danger'">
              {{ row.status === 'in_stock' ? '在库' : row.status === 'out_stock' ? '出库' : '已销毁' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="entryTime" label="入库时间" width="180" sortable>
          <template #default="{ row }">
              {{ formatDateTime(row.entry_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="entry_person" label="录入人" width="85">
          <template #default="{ row }">
            {{ row.entry_person }}
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
        <el-form-item label="细胞ID" prop="cell_id">
          <el-input v-model="form.cell_id"/>
        </el-form-item>
        <el-form-item label="细胞类型" prop="cell_type">
          <el-select v-model="form.cell_type" class="category-select" placeholder="请选择细胞类型">
            <el-option label="原代细胞" value="primary"/>
            <el-option label="人源细胞" value="human"/>
            <el-option label="小鼠细胞" value="mouse"/>
            <el-option label="大鼠细胞" value="rat"/>
          </el-select>
        </el-form-item>
        <el-form-item label="存储位置" prop="storageLocation">
          <el-cascader
              v-model="form.storage_location"
              :options="locationOptions"
              placeholder="请选择存储位置"
          />
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1"/>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="in_stock">在库</el-radio>
            <el-radio label="out_stock">出库</el-radio>
            <el-radio label="destroyed">已销毁</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="form.notes" type="textarea" :rows="3"/>
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
import {ref, onMounted} from 'vue';
import * as echarts from 'echarts';
import api from "@/api/api.js";
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

const cascaderProps = {
  value: 'value',
  label: 'label',
  children: 'children',
  checkStrictly: true,  // 可以选择任意一级
  emitPath: true        // 返回完整路径
}

// 表格数据
const tableData = ref([])
const cellTypes = ref([])
const statistics = ref({})


// 搜索表单
const searchForm = ref({
  cell_id: '',
  cell_type: '',
  location: '',
  status: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)
const loading = ref(false)

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新增细胞')
// 修改表单初始值
const form = ref({
  cell_id: '',
  cell_type: '',
  storage_location: '',
  quantity: 1,
  status: 'IN_STOCK',
  notes: ''
})
const formRef = ref(null)

// 修改表单验证规则
const rules = {
  cell_id: [{required: true, message: '请输入细胞ID', trigger: 'blur'}],
  cell_type: [{required: true, message: '请选择细胞类型', trigger: 'change'}],
  storage_location: [{required: true, message: '请选择存储位置', trigger: 'change'}],
  quantity: [{required: true, message: '请输入数量', trigger: 'blur'}],
  status: [{required: true, message: '请选择状态', trigger: 'change'}]
}

// 存储位置选项
const locationOptions = ref([])
console.log(locationOptions)
// 图表引用
const typeChart = ref(null)
const statusChart = ref(null)

// 在 script setup 中添加这个方法
const transformLocationData = (data) => {
  return data.map(item => ({
    value: item.id,
    label: `${item.name} (${item.number})`,
    children: item.children ? transformLocationData(item.children) : null
  }))
}

const initCharts = () => {
  // 统计细胞类型数量
  const typeCounts = {};
  // 新增：统计细胞状态
  const statusCounts = {
    'in_stock': 0,
    'out_stock': 0,
    'destroyed': 0
  };

  tableData.value.forEach(item => {
    const typeName = item.cell_type?.name || '未知类型';
    typeCounts[typeName] = (typeCounts[typeName] || 0) + 1;

    // 新增：统计细胞状态
    if (item.status) {
      statusCounts[item.status] = (statusCounts[item.status] || 0) + 1;
    }
  });

  // 转换为图表需要的格式
  const typeChartData = Object.entries(typeCounts).map(([name, value]) => ({
    value,
    name
  }));

  // 新增：状态统计数据转换
  const statusLabels = ['在库', '出库', '已销毁'];
  const statusData = [
    statusCounts['in_stock'],
    statusCounts['out_stock'],
    statusCounts['destroyed']
  ];

  // 细胞类型分布图（原有代码保持不变）
  const typeChartInstance = echarts.init(typeChart.value);
  typeChartInstance.setOption({
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        name: '细胞类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: typeChartData  // 使用动态统计数据
      }
    ]
  });

  // 新增：细胞状态统计图
  const statusChartInstance = echarts.init(statusChart.value);
  statusChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {type: 'shadow'}
    },
    xAxis: {type: 'value'},
    yAxis: {
      type: 'category',
      data: statusLabels
    },
    series: [{
      name: '数量',
      type: 'bar',
      data: statusData,
      itemStyle: {
        color: function (params) {
          // 根据状态设置不同颜色
          const colorMap = {
            '在库': '#67C23A',
            '出库': '#E6A23C',
            '已销毁': '#F56C6C'
          };
          return colorMap[statusLabels[params.dataIndex]] || '#409EFF';
        }
      }
    }]
  });

  // 窗口大小变化时重绘两个图表
  window.addEventListener('resize', () => {
    typeChartInstance.resize();
    statusChartInstance.resize();
  });
}

// 获取细胞类型标签样式
const getCellTypeTag = (type) => {
  const typeMap = {
    '人源细胞': '',
    '小鼠细胞': 'info',
    '大鼠细胞': 'warning',
    '原代细胞': 'danger'
  }
  return typeMap[type] || ''
}

// 搜索方法
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    cell_id: '',
    cell_type: '',
    location: '',
    status: ''
  }
  handleSearch()
}


// 修改格式化存储位置的方法
const formatLocation = (locationIds) => {
  if (!locationIds || !locationIds.length) return '未指定'

  const findPath = (options, ids, path = []) => {
    if (!ids.length) return path

    const currentId = ids[0]
    const found = options.find(opt => opt.value === currentId)

    if (found) {
      path.push(found.label)
      if (ids.length > 1 && found.children) {
        return findPath(found.children, ids.slice(1), path)
      }
    }
    return path
  }

  return findPath(locationOptions.value, locationIds).join(' > ') || '未知位置'
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const cellResponse = await api.getCells(
        currentPage.value,
        pageSize.value,
        {
          cell_id: searchForm.value.cell_id,
          cell_type: searchForm.value.cell_type,
          status: searchForm.value.status,
          storage_location: searchForm.value.location
        }
    );
    tableData.value = cellResponse.data;
    total.value = cellResponse.data.length;

    // 数据获取完成后重新初始化图表
    initCharts();
  } catch (error) {
    console.error('获取数据失败:', error);
    ElMessage.error('获取数据失败');
  } finally {
    loading.value = false;
  }
};
// 初始化时获取必要数据
onMounted(async () => {
  await fetchData()

  // 获取存储位置选项
  try {
    const locationResponse = await api.getLocationTree()
    locationOptions.value = transformLocationData(locationResponse.data)
    console.log('转换后的位置选项:', locationOptions.value)
  } catch (error) {
    console.error('获取存储位置失败:', error)
    ElMessage.error('加载存储位置失败')
  }
  // 获取细胞类型选项
  try {
    const typeResponse = await api.getCellTypes()
    cellTypes.value = typeResponse.data
    console.log(typeResponse)
  } catch (error) {
    console.error('获取细胞类型失败:', error)
  }


})
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

// 排序变化
const handleSortChange = ({column, prop, order}) => {
  fetchData()
}

// 新增细胞
const handleAdd = () => {
  if (!checkPermission(2)) return // 2级权限才能新增
  dialogTitle.value = '新增细胞'
  form.value = {
    cell_id: '',
    cell_type: '',
    storage_location: '',
    quantity: 1,
    status: 'in_stock',
    notes: ''
  }
  dialogVisible.value = true
}

// 编辑细胞
const handleEdit = (row) => {
  if (!checkPermission(2)) return // 2级权限才能编辑
  dialogTitle.value = '编辑细胞'
  form.value = {...row}
  dialogVisible.value = true
}

// 删除细胞
const handleDelete = (row) => {
  if (!checkPermission(2)) return // 1级权限才能删除
  ElMessageBox.confirm(`确定要删除细胞 ${row.cell_id} 吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    fetchData()
  }).catch(() => {
  })
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()
    // 获取细胞类型ID
    const selectedCellType = cellTypes.value.find(
        type => type.category === form.value.cell_type
    )
    console.log(selectedCellType)
    const cellTypeId = selectedCellType ? selectedCellType.id : null

    const payload = {
      cell_id: form.value.cell_id,
      cell_type: cellTypeId,  // 使用获取到的细胞类型ID
      storage_location: Array.isArray(form.value.storage_location)
          ? form.value.storage_location[form.value.storage_location.length - 1] // 取最后一级id
          : form.value.storage_location,
      quantity: form.value.quantity,
      status: form.value.status,
      notes: form.value.notes
    }

    if (dialogTitle.value === '新增细胞') {
      console.log(payload)
      await api.createCell(payload)
      ElMessage.success('添加成功')
    } else {
      await api.updateCell(form.value.cell_id, payload)
      ElMessage.success('更新成功')
    }

    dialogVisible.value = false
    fetchData()
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
// 生命周期钩子
onMounted(() => {
  fetchData()
  initCharts()
})
</script>

<style scoped lang="scss">

.search-card .el-form-item {
  margin-right: 20px;
  margin-bottom: 0;
  width: 200px; /* 统一设置宽度 */
}


.cell-inventory-container {
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

.chart-row {
  margin-bottom: 20px;

  .chart-card {
    border-radius: 8px;
    height: 300px;

    .chart-header {
      font-weight: bold;
      font-size: 16px;
    }

    .chart-container {
      width: 100%;
      height: 250px;
    }
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



