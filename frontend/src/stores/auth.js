import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('ce_token') || null)
  const loading = ref(false)
  const error = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  async function fetchMe() {
    if (!token.value) return
    try {
      const { data } = await authApi.me()
      user.value = data
    } catch {
      logout()
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const { data } = await authApi.login({ email, password })
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('ce_token', data.access_token)
    } catch (e) {
      error.value = e.response?.data?.detail || 'Login failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function register(username, email, password) {
    loading.value = true
    error.value = null
    try {
      const { data } = await authApi.register({ username, email, password })
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('ce_token', data.access_token)
    } catch (e) {
      error.value = e.response?.data?.detail || 'Registration failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('ce_token')
  }

  return { user, token, loading, error, isLoggedIn, fetchMe, login, register, logout }
})
