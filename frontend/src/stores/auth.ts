import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { Usuario } from '@/types'

function parseUser(): Usuario | null {
  try {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  } catch {
    localStorage.removeItem('user')
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<Usuario | null>(parseUser())
  const token = ref<string | null>(localStorage.getItem('token'))
  
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => {
    const rol = (user.value?.rol || '').toLowerCase()
    return rol === 'admin' || rol === 'administrador'
  })
  
  async function login(usuario: string, contrasena: string) {
    const response = await authApi.login(usuario, contrasena)
    const data = response.data
    user.value = data
    token.value = data.token
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data))
    return data
  }
  
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  return { user, token, isAuthenticated, isAdmin, login, logout }
})