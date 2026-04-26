<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useServiciosStore } from '@/stores/servicios'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus } from 'lucide-vue-next'
import type { Servicio } from '@/types'

const store = useServiciosStore()
const showModal = ref(false)
const editingServicio = ref<Servicio | null>(null)

const form = ref({
  nombre: '',
  descripcion: '',
  precio: 0,
  duracion_estimada: 30
})

onMounted(() => store.fetchAll())

function openCreate() {
  editingServicio.value = null
  form.value = { nombre: '', descripcion: '', precio: 0, duracion_estimada: 30 }
  showModal.value = true
}

function openEdit(servicio: Servicio) {
  editingServicio.value = servicio
  form.value = { ...servicio }
  showModal.value = true
}

async function save() {
  if (editingServicio.value) {
    await store.actualizar(editingServicio.value.id_servicio, form.value)
  } else {
    await store.crear(form.value)
  }
  showModal.value = false
}

async function remove(id: number) {
  if (confirm('¿Está seguro de eliminar este servicio?')) {
    await store.eliminar(id)
  }
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value)
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Servicios</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Nuevo Servicio
      </button>
    </div>
    
    <LoadingSpinner v-if="store.loading" />
    
    <div v-else class="card">
      <table class="w-full">
        <thead>
          <tr class="table-header">
            <th class="table-cell">Nombre</th>
            <th class="table-cell">Descripción</th>
            <th class="table-cell">Precio</th>
            <th class="table-cell">Duración (min)</th>
            <th class="table-cell">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="servicio in store.servicios" :key="servicio.id_servicio" class="border-b hover:bg-gray-50">
            <td class="table-cell font-medium">{{ servicio.nombre }}</td>
            <td class="table-cell">{{ servicio.descripcion || '-' }}</td>
            <td class="table-cell">{{ formatCurrency(servicio.precio) }}</td>
            <td class="table-cell">{{ servicio.duracion_estimada || '-' }}</td>
            <td class="table-cell">
              <TableActions :actions="['edit', 'delete']" @edit="openEdit(servicio)" @delete="remove(servicio.id_servicio)" />
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="store.servicios.length === 0" class="text-center py-8 text-gray-500">
        No hay servicios registrados
      </div>
    </div>
    
    <Modal :open="showModal" :title="editingServicio ? 'Editar Servicio' : 'Nuevo Servicio'" @close="showModal = false">
      <form @submit.prevent="save" class="space-y-4">
        <div>
          <label class="label">Nombre *</label>
          <input v-model="form.nombre" class="input" required />
        </div>
        <div>
          <label class="label">Descripción</label>
          <textarea v-model="form.descripcion" class="input" rows="2"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Precio *</label>
            <input v-model.number="form.precio" type="number" class="input" required />
          </div>
          <div>
            <label class="label">Duración (min)</label>
            <input v-model.number="form.duracion_estimada" type="number" class="input" />
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