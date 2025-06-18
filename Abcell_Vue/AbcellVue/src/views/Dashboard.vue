<template>
  <div class="dashboard-container">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>欢迎回来，{{ userName }}！</h1>
          <p class="sub-title">今天是{{ currentDate }}，祝您工作愉快！</p>
        </div>
<!--        <el-image-->
<!--          class="welcome-image"-->
<!--          :src="require('@/assets/images/lab-icon.png')"-->
<!--          fit="cover"-->
<!--        ></el-image>-->
      </div>
    </el-card>

    <!-- 统计卡片区域 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f0f7ff;">
              <el-icon color="#409EFF" :size="28">
                <Box />
              </el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-title">细胞库存</span>
              <span class="stat-value">{{ cell_number }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f0f9eb;">
              <el-icon color="#67C23A" :size="28">
                <ColdDrink />
              </el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-title">冰柜数量</span>
              <span class="stat-value">{{ freezer_number }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #fdf6ec;">
              <el-icon color="#E6A23C" :size="28">
                <Collection />
              </el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-title">细胞类型</span>
              <span class="stat-value">{{ cell_type }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #fef0f0;">
              <el-icon color="#F56C6C" :size="28">
                <User />
              </el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-title">系统用户</span>
              <span class="stat-value">{{ user_number }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 两栏布局 -->
    <el-row :gutter="20" class="main-row">
      <!-- 左侧：快速操作 -->
      <el-col :span="12">
        <el-card class="quick-actions">
          <template #header>
            <div class="card-header">
              <el-icon><MagicStick /></el-icon>
              <span>快速操作</span>
            </div>
          </template>
          <div class="action-buttons">
            <el-button style="margin-left: 12px" type="primary" icon="Plus" @click="goToCellInventory">新增细胞</el-button>
            <el-button type="success" icon="Download" @click="goToCellOut">细胞出库</el-button>
            <el-button type="warning" icon="Upload" @click="goToCellType">新增类型</el-button>
            <el-button type="info" icon="Setting" @click="goToFreezer">冰柜管理</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：最近活动 -->
      <el-col :span="12">
        <el-card class="recent-activity">
          <template #header>
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>最近活动</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in activities"
              :key="index"
              :timestamp="activity.time"
              :type="activity.type"
              :color="activity.color"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue'
import { useRouter } from 'vue-router'
import {
  Box,
  ColdDrink,
  Collection,
  User,
  MagicStick,
  Clock,
  Plus,
  Download,
  Upload,
  Setting
} from '@element-plus/icons-vue'
import api from "@/api/api.js";

const router = useRouter()

// 用户数据
const userName = ref('管理员')

// 当前日期
const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
})

// 最近活动数据
const activities = ref([
  {
    time: '2023-06-15 14:30',
    content: '张研究员 出库了细胞 CELL-2023-00125',
    type: 'primary',
    color: '#409EFF'
  },
  {
    time: '2023-06-15 10:15',
    content: '李技术员 新增了细胞类型 小鼠肝细胞',
    type: 'success',
    color: '#67C23A'
  },
  {
    time: '2023-06-14 16:45',
    content: '王助理 入库了细胞 CELL-2023-00124',
    type: 'warning',
    color: '#E6A23C'
  },
  {
    time: '2023-06-14 09:20',
    content: '张研究员 调整了细胞 CELL-2023-00098 的存储位置',
    type: 'info',
    color: '#909399'
  }
])

// 快速操作导航方法
const goToCellInventory = () => router.push('/cell/inventory')
const goToCellOut = () => router.push('/cell/out')
const goToCellType = () => router.push('/cell/type')
const goToFreezer = () => router.push('/storage/freezer')
// 修改这部分代码
const cell_number = ref(0)
const freezer_number = ref(0)
const cell_type = ref(0)
const user_number = ref(0)
onMounted(async () => {
  try {
    const response = await api.getUsers()
     user_number.value = response.data.length
    console.log('用户数量:',  user_number.value)
  } catch (error) {
    console.error('获取用户数量失败:', error)
  }
})
onMounted(async () => {
  try {
    const response = await api.getCellTypes()
     cell_type.value = response.data.length
    console.log('细胞类型数量:',  cell_type.value)
  } catch (error) {
    console.error('获取细胞类型数量失败:', error)
  }
})
onMounted(async () => {
  try {
    const response = await api.getFreezers()
    freezer_number.value = response.data.length
    console.log('冰柜数量:', freezer_number.value)
  } catch (error) {
    console.error('获取冰柜数量失败:', error)
  }
})
onMounted(async () => {
  try {
    const response = await api.getCells(1, 100000)
    cell_number.value = response.data.length
    console.log('细胞数量:', cell_number.value)
  } catch (error) {
    console.error('获取细胞数量失败:', error)
  }
})


</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
  border-radius: 8px;

  .welcome-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .welcome-text {
      h1 {
        margin: 0;
        font-size: 24px;
        color: #303133;
      }

      .sub-title {
        margin: 10px 0 0;
        font-size: 14px;
        color: #909399;
      }
    }

    .welcome-image {
      width: 120px;
      height: 80px;
    }
  }
}

.stats-row {
  margin-bottom: 20px;

  .stat-card {
    border-radius: 8px;

    .stat-content {
      display: flex;
      align-items: center;

      .stat-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 50px;
        height: 50px;
        border-radius: 8px;
        margin-right: 15px;
      }

      .stat-info {
        display: flex;
        flex-direction: column;

        .stat-title {
          font-size: 14px;
          color: #909399;
          margin-bottom: 5px;
        }

        .stat-value {
          font-size: 24px;
          font-weight: bold;
          color: #303133;
        }
      }
    }
  }
}

.main-row {
  .quick-actions, .recent-activity {
    border-radius: 8px;
    height: 100%;

    .card-header {
      display: flex;
      align-items: center;

      .el-icon {
        margin-right: 8px;
        font-size: 18px;
      }

      span {
        font-weight: bold;
      }
    }
  }

  .quick-actions {
    .action-buttons {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 15px;

      .el-button {
        width: 100%;
        height: 80px;
        font-size: 16px;

        .el-icon {
          font-size: 24px;
          margin-bottom: 8px;
        }
      }
    }
  }

  .recent-activity {
    .el-timeline {
      padding-left: 10px;

      .el-timeline-item {
        padding-bottom: 15px;
      }
    }
  }
}
</style>