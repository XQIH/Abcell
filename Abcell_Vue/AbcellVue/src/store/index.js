import { createStore } from 'vuex'
// import createPersistedState from 'vuex-persistedstate'

export default createStore({
  // plugins: [createPersistedState()],
  state: {
    user: {
      token: localStorage.getItem('token') || null,
      id: localStorage.getItem('userId') || null,
      username: localStorage.getItem('username') || null,
      avatar: localStorage.getItem('avatar') || null,
      permission_level: parseInt(localStorage.getItem('permissionLevel')) || 3
    }
  },
  mutations: {
    setToken(state, {token, expiresIn = 3600}) {
      state.user.token = token
      state.user.tokenExpires = Date.now() + expiresIn * 1000
    },
    setUserId(state, id) {  // 添加这行
      state.user.id = id
    },
    setUserData(state, data) {
      console.log(data)
      state.user.id = data.user_id
      state.user.username = data.username
      state.user.avatar = data.avatar
      state.user.permission_level = data.permission_level
    
    // 保存到localStorage
    localStorage.setItem('userId', data.user_id)
    localStorage.setItem('username', data.username)
    localStorage.setItem('avatar', data.avatar)
    localStorage.setItem('permissionLevel', data.permission_level)
    },
    clearUser(state) {
      state.user.token = null
      state.user.id = null
      state.user.permission_level = 3
      state.user.tokenExpires = null
      state.user.avatar = null
    }
  },
  getters: {
    hasPermission: (state) => (requiredLevel) => {
      // 修改判断逻辑，数字越小权限越高
      return state.user.permission_level <= requiredLevel
    }
  }
})