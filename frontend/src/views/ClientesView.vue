<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useClientesStore } from '@/stores/clientes'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus, Search } from 'lucide-vue-next'
import type { Cliente } from '@/types'

const store = useClientesStore()
const showModal = ref(false)
const editingCliente = ref<Cliente | null>(null)
const searchQuery = ref('')

const form = ref({
  nombre: '',
  documento: '',
  tipo_documento: 'CC',
  telefono: '',
  email: '',
  direccion: '',
  ciudad: ''
})

onMounted(() => store.fetchAll())

function openCreate() {
  editingCliente.value = null
  form.value = { nombre: '', documento: '', tipo_documento: 'CC', telefono: '', email: '', direccion: '', ciudad: '' }
  showModal.value = true
}

function openEdit(cliente: Cliente) {
  editingCliente.value = cliente
  form.value = { ...cliente }
  showModal.value = true
}

async function save() {
  if (editingCliente.value) {
    await store.actualizar(editingCliente.value.id_cliente, form.value)
  } else {
    await store.crear(form.value)
  }
  showModal.value = false
}

async function remove(id: number) {
  if (confirm('¿Está seguro de eliminar este cliente?')) {
    await store.eliminar(id)
  }
}

const filteredClientes = () => {
  if (!searchQuery.value) return store.clientes
  const q = searchQuery.value.toLowerCase()
  return store.clientes.filter(c => 
    c.nombre.toLowerCase().includes(q) || 
    c.documento.includes(q) ||
    c.telefono?.toLowerCase().includes(q)
  )
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Clientes</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Nuevo Cliente
      </button>
    </div>
    
    <LoadingSpinner v-if="store.loading" />
    
    <div v-else class="card">
      <div class="mb-4">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input 
            v-model="searchQuery"
            type="text" 
            class="input pl-10" 
            placeholder="Buscar cliente..."
          />
        </div>
      </div>
      
      <table class="w-full">
        <thead>
          <tr class="table-header">
            <th class="table-cell">Nombre</th>
            <th class="table-cell">Documento</th>
            <th class="table-cell">Teléfono</th>
            <th class="table-cell">Email</th>
            <th class="table-cell">Ciudad</th>
            <th class="table-cell">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cliente in filteredClientes()" :key="cliente.id_cliente" class="border-b hover:bg-gray-50">
            <td class="table-cell">{{ cliente.nombre }}</td>
            <td class="table-cell">{{ cliente.tipo_documento }} {{ cliente.documento }}</td>
            <td class="table-cell">{{ cliente.telefono || '-' }}</td>
            <td class="table-cell">{{ cliente.email || '-' }}</td>
            <td class="table-cell">{{ cliente.ciudad || '-' }}</td>
            <td class="table-cell">
              <TableActions 
                :actions="['edit', 'delete']"
                @edit="openEdit(cliente)"
                @delete="remove(cliente.id_cliente)"
              />
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="store.clientes.length === 0" class="text-center py-8 text-gray-500">
        No hay clientes registrados
      </div>
    </div>
    
    <Modal :open="showModal" :title="editingCliente ? 'Editar Cliente' : 'Nuevo Cliente'" @close="showModal = false">
      <form @submit.prevent="save" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Nombre *</label>
            <input v-model="form.nombre" class="input" required />
          </div>
          <div class="flex gap-2">
            <div class="flex-1">
              <label class="label">Tipo Doc *</label>
              <select v-model="form.tipo_documento" class="input">
                <option value="CC">CC</option>
                <option value="NIT">NIT</option>
                <option value="CE">CE</option>
                <option value="PP">PP</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="label">Documento *</label>
              <input v-model="form.documento" class="input" required />
            </div>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Teléfono</label>
            <input v-model="form.telefono" class="input" />
          </div>
          <div>
            <label class="label">Email</label>
            <input v-model="form.email" type="email" class="input" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Dirección</label>
            <input v-model="form.direccion" class="input" />
          </div>
          <div>
            <label class="label">Ciudad</label>
            <input v-model="form.ciudad" class="input" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" class="btn btn-primary">Guardar</button>
        </div>
      </form>
    </Modal>
  </div>
</template>