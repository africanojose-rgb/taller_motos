<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Car, AlertCircle, Wifi, WifiOff } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const usuario = ref('')
const contrasena = ref('')
const error = ref('')
const loading = ref(false)
const serverStatus = ref<'checking' | 'online' | 'offline'>('checking')

watch([usuario, contrasena], () => {
  if (error.value) error.value = ''
})

onMounted(async () => {
  try {
    await fetch('/api/health', { signal: AbortSignal.timeout(3000) })
    serverStatus.value = 'online'
  } catch {
    serverStatus.value = 'offline'
  }
})

async function handleLogin() {
  if (!usuario.value || !contrasena.value) {
    error.value = 'Complete todos los campos'
    return
  }
  
  if (serverStatus.value === 'offline') {
    error.value = 'No se puede conectar al servidor. Verifique que el backend esté ejecutándose.'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    await auth.login(usuario.value, contrasena.value)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e?.response?.data?.error || e?.message || 'Error de red o servidor'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="card w-full max-w-md">
      <div class="text-center mb-8">
        <Car class="w-12 h-12 mx-auto text-secondary" />
        <h1 class="text-2xl font-bold mt-4">Taller Mecánico</h1>
        <p class="text-gray-500 mt-1">Ingrese sus credenciales</p>
        <div class="mt-2">
          <Wifi v-if="serverStatus === 'online'" class="w-5 h-5 inline text-green-500" />
          <WifiOff v-else-if="serverStatus === 'offline'" class="w-5 h-5 inline text-red-500" />
          <span v-if="serverStatus === 'offline'" class="text-red-500 text-sm ml-1">Servidor no disponible</span>
        </div>
      </div>
      
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div v-if="error" class="p-3 bg-red-100 text-red-700 rounded-lg flex items-center gap-2">
          <AlertCircle class="w-5 h-5" />
          {{ error }}
        </div>
        
        <div>
          <label class="label">Usuario</label>
          <input 
            v-model="usuario" 
            type="text" 
            class="input" 
            placeholder="admin"
            autocomplete="username"
            required
          />
        </div>
        
        <div>
          <label class="label">Contraseña</label>
          <input 
            v-model="contrasena" 
            type="password" 
            class="input" 
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>
        
        <button 
          type="submit" 
          class="btn btn-primary w-full"
          :disabled="loading || serverStatus === 'offline'"
        >
          {{ loading ? 'Ingresando...' : 'Ingresar' }}
        </button>
      </form>
    </div>
  </div>
</template>