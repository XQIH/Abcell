import store from '@/store'

export default {
  mounted(el, binding) {
    const { value } = binding
    const hasPermission = store.getters.hasPermission(value)
    if (!hasPermission) {
      el.parentNode?.removeChild(el)
    }
  }
}