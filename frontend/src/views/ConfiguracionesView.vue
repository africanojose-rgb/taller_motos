<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useConfigStore } from '@/stores/config'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Save, Settings, Mail } from 'lucide-vue-next'

const store = useConfigStore()
const saving = ref(false)
const message = ref('')

const form = ref({
  nombre_taller: '',
  nit: '',
  direccion: '',
  telefono: '',
  ciudad: '',
  iva: '19',
  porc_comision_servicio: '10',
  porc_comision_repuesto: '5',
  email_smtp: '',
  email_usuario: '',
  email_password: '',
  email_destino: ''
})

onMounted(async () => {
  await store.fetchAll()
  form.value = {
    nombre_taller: store.config.nombre_taller || '',
    nit: store.config.nit || '',
    direccion: store.config.direccion || '',
    telefono: store.config.telefono || '',
    ciudad: store.config.ciudad || '',
    iva: store.config.iva || '19',
    porc_comision_servicio: store.config.porc_comision_servicio || '10',
    porc_comision_repuesto: store.config.porc_comision_repuesto || '5',
    email_smtp: store.config.email_smtp || '',
    email_usuario: store.config.email_usuario || '',
    email_password: store.config.email_password || '',
    email_destino: store.config.email_destino || ''
  }
})

async function save() {
  saving.value = true
  message.value = ''
  try {
    const items = Object.entries(form.value).map(([clave, valor]) => ({ clave, valor }))
    await store.guardarBulk(items)
    message.value = 'Configuración guardada correctamente'
  } catch (e) {
    message.value = 'Error al guardar'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Configuración del Taller</h1>
    
    <LoadingSpinner v-if="store.loading" />
    
    <div v-else class="card max-w-2xl">
      <div class="flex items-center gap-2 mb-6">
        <Settings class="w-5 h-5" />
        <h2 class="text-lg font-semibold">Datos del Taller</h2>
      </div>
      
      <form @submit.prevent="save" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Nombre del Taller</label>
            <input v-model="form.nombre_taller" class="input" />
          </div>
          <div>
            <label class="label">NIT</label>
            <input v-model="form.nit" class="input" />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Dirección</label>
            <input v-model="form.direccion" class="input" />
          </div>
          <div>
            <label class="label">Teléfono</label>
            <input v-model="form.telefono" class="input" />
          </div>
        </div>
        
        <div>
          <label class="label">Ciudad</label>
          <input v-model="form.ciudad" class="input max-w-xs" />
        </div>
        
        <hr class="my-6">
        
        <h3 class="font-semibold mb-4">Parámetros</h3>
        
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="label">IVA (%)</label>
            <input v-model="form.iva" type="number" class="input" />
          </div>
          <div>
            <label class="label">% Comisión Servicio</label>
            <input v-model="form.porc_comision_servicio" type="number" step="0.5" class="input" />
          </div>
          <div>
            <label class="label">% Comisión Repuesto</label>
            <input v-model="form.porc_comision_repuesto" type="number" step="0.5" class="input" />
          </div>
        </div>
        
        <hr class="my-6">
        
        <div class="flex items-center gap-2 mb-4">
          <Mail class="w-5 h-5" />
          <h3 class="font-semibold">Configuración SMTP (Envío de Emails)</h3>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Servidor SMTP</label>
            <input v-model="form.email_smtp" class="input" placeholder="smtp.gmail.com" />
          </div>
          <div>
            <label class="label">Usuario / Email</label>
            <input v-model="form.email_usuario" class="input" placeholder="correo@example.com" />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Password</label>
            <input v-model="form.email_password" type="password" class="input" />
          </div>
          <div>
            <label class="label">Email Remitente</label>
            <input v-model="form.email_destino" class="input" placeholder="taller@example.com" />
          </div>
        </div>
        
        <p class="text-sm text-gray-500 mt-2">
          Para Gmail, usa una contraseña de aplicación. Configúrala en tu cuenta de Google &gt; Seguridad &gt; Verificación en 2 pasos &gt; Contraseñas de aplicación.
        </p>
        
        <div v-if="message" class="p-3 bg-green-100 text-green-700 rounded-lg">
          {{ message }}
        </div>
        
        <div class="flex justify-end gap-3 mt-6">
          <button type="submit" class="btn btn-primary flex items-center gap-2" :disabled="saving">
            <Save class="w-4 h-4" />
            {{ saving ? 'Guardando...' : 'Guardar Configuración' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>