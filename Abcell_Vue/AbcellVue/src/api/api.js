// src/api/api.js
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',  // 确保这是Django服务器的地址
  timeout: 5000
})

// 请求拦截器
// 在axios实例配置中添加请求拦截器
// 修正请求拦截器
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器
// 修改响应拦截器避免循环引用
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('refreshToken')
        if (error.response?.status === 403) {
          ElMessage.error('无权限执行此操作')
        }
        if (!refreshToken) throw new Error('No refresh token')
        
        const response = await apiClient.post('/api/token/refresh/', {
          refresh: refreshToken
        })
        
        localStorage.setItem('token', response.data.access)
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`
        return apiClient(originalRequest)
      } catch (e) {
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)


export default {
  getRecentActivities() {
    return apiClient.get('/api/activity-logs/')
  },
  // 细胞库存相关 API
  getCells(page, pageSize, filters = {}) {
    return apiClient.get('/cells/', {
      params: {
        page,
        page_size: pageSize,
        ...filters
      }
    })
  },

  getCell(id) {
    return apiClient.get(`/cells/${id}/`)
  },

  createCell(cellData) {
    return apiClient.post('/cells/', cellData)
  },

  updateCell(id, cellData) {
    return apiClient.put(`/cells/${id}/`, cellData)
  },

  deleteCell(id) {
    return apiClient.delete(`/cells/${id}/`)
  },

  // 细胞出库相关API
  getCellOutRecords(params) {
    return apiClient.get('/cell-out-records/', { params })
  },

  searchAvailableCells(query) {
    return apiClient.get('/cell-out-records/available-cells-by-id', {
      params: { search: query }
    })
  },

  createCellOutRecord(data) {
    return apiClient.post('/cell-out-records/', data)  // 修改为新的端点
  },

  // 细胞类型相关API
  getCellTypes(params) {
    return apiClient.get('/cell-types1/', { params })
  },

  createCellType(data) {
    return apiClient.post('/cell-types1/', data)
  },

  updateCellType(id, data) {
    return apiClient.put(`/cell-types1/${id}/`, data)
  },

  deleteCellType(id) {
    return apiClient.delete(`/cell-types1/${id}/`)
  },

  // 冰柜相关API
  getFreezers(params) {
    return apiClient.get('/storage/freezers/', { params })
  },

  createFreezer(data) {
    return apiClient.post('/storage/freezers/', data)
  },

  updateFreezer(id, data) {
    return apiClient.put(`/storage/freezers/${id}/`, data)
  },

  deleteFreezer(id) {
    return apiClient.delete(`/storage/freezers/${id}/`)
  },
  // 存储位置相关API
  getLocationTree() {
    return apiClient.get('/storage/locations/tree/')
  },

  // 冰柜
  createFreezer1(data) {
    return apiClient.post('/storage/freezers1/', data)
  },
  updateFreezer1(data) {
    return apiClient.put(`/storage/freezers1/${data.id}/`, data)
  },
  deleteFreezer1(id) {
    return apiClient.delete(`/storage/freezers1/${id}/`)
  },

  // 层级
  createLevel(data) {
    return apiClient.post('/storage/levels/', data)
  },
  updateLevel(data) {
    return apiClient.put(`/storage/levels/${data.id}/`, data)
  },
  deleteLevel(id) {
    return apiClient.delete(`/storage/levels/${id}/`)
  },

  // 列
  createColumn(data) {
    return apiClient.post('/storage/columns/', data)
  },
  updateColumn(data) {
    return apiClient.put(`/storage/columns/${data.id}/`, data)
  },
  deleteColumn(id) {
    return apiClient.delete(`/storage/columns/${id}/`)
  },

  // 抽屉
  createDrawer(data) {
    return apiClient.post('/storage/drawers/', data)
  },
  updateDrawer(data) {
    return apiClient.put(`/storage/drawers/${data.id}/`, data)
  },
  deleteDrawer(id) {
    return apiClient.delete(`/storage/drawers/${id}/`)
  },

  // 盒子
  createBox(data) {
    return apiClient.post('/storage/boxes/', data)
  },
  updateBox(data) {
    return apiClient.put(`/storage/boxes/${data.id}/`, data)
  },
  deleteBox(id) {
    return apiClient.delete(`/storage/boxes/${id}/`)
  },

  // 格子
  createCell1(data) {
    return apiClient.post('/storage/cells/', data)
  },
  updateCell1(data) {
    return apiClient.put(`/storage/cells/${data.id}/`, data)
  },
  deleteCell1(id) {
    return apiClient.delete(`/storage/cells/${id}/`)
  },
  // 用户登录
  // 检查登录调用
  login(credentials) {
      return apiClient.post('/api/sysuser/login/', {
          email: credentials.email,
          password: credentials.password
      })
  },
  
  // 检查注册调用 
  register(data) {
      return apiClient.post('/api/sysuser/register/', data)
  },  // 这里添加了缺少的逗号

  // 用户管理
  getUsers(params) {
    return apiClient.get('/api/sysuser/users/', { params })
  },

  getUser(id) {
    return apiClient.get(`/api/sysuser/users/${id}/`)
  },

  createUser(userData) {
    return apiClient.post('/api/sysuser/users/', userData)
  },

  updateUser(id, userData) {
    return apiClient.put(`/api/sysuser/users/${id}/`, userData)
  },

  deleteUser(id) {
    return apiClient.delete(`/api/sysuser/users/${id}/`)
  },

  resetPassword(userId, newPassword, confirmPassword) {
    return apiClient.post(`/api/sysuser/users/${userId}/reset_password/`, {
      user_id: userId,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  },

  // 存储token
  setToken(token) {
    localStorage.setItem('token', token)
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },

  // 清除token
  clearToken() {
    localStorage.removeItem('token')
    delete apiClient.defaults.headers.common['Authorization']
  },

  refreshToken(refreshToken) {
    return apiClient.post('/api/token/refresh/', {
      refresh: refreshToken
    })
  },
  
}
// 添加store导入
import store from '@/store'
