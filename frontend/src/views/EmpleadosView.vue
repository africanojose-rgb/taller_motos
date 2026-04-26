<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useEmpleadosStore } from '@/stores/empleados'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus } from 'lucide-vue-next'
import type { Empleado } from '@/types'

const store = useEmpleadosStore()
const showModal = ref(false)
const editingEmpleado = ref<Empleado | null>(null)

const form = ref({
  documento: '',
  nombre: '',
  telefono: '',
  email: '',
  cargo: '',
  fecha_contrato: ''
})

onMounted(() => store.fetchAll())

function openCreate() {
  editingEmpleado.value = null
  form.value = { documento: '', nombre: '', telefono: '', email: '', cargo: '', fecha_contrato: '' }
  showModal.value = true
}

function openEdit(empleado: Empleado) {
  editingEmpleado.value = empleado
  form.value = { ...empleado }
  showModal.value = true
}

async function save() {
  if (editingEmpleado.value) {
    await store.actualizar(editingEmpleado.value.id_empleado, form.value)
  } else {
    await store.crear(form.value)
  }
  showModal.value = false
}

async function remove(id: number) {
  if (confirm('¿Está seguro de eliminar este empleado?')) {
    await store.eliminar(id)
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Empleados</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Nuevo Empleado
      </button>
    </div>
    
    <LoadingSpinner v-if="store.loading" />
    
    <div v-else class="card">
      <table class="w-full">
        <thead>
          <tr class="table-header">
            <th class="table-cell">Documento</th>
            <th class="table-cell">Nombre</th>
            <th class="table-cell">Teléfono</th>
            <th class="table-cell">Email</th>
            <th class="table-cell">Cargo</th>
            <th class="table-cell">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="empleado in store.empleados" :key="empleado.id_empleado" class="border-b hover:bg-gray-50">
            <td class="table-cell">{{ empleado.documento }}</td>
            <td class="table-cell font-medium">{{ empleado.nombre }}</td>
            <td class="table-cell">{{ empleado.telefono || '-' }}</td>
            <td class="table-cell">{{ empleado.email || '-' }}</td>
            <td class="table-cell">{{ empleado.cargo }}</td>
            <td class="table-cell">
              <TableActions :actions="['edit', 'delete']" @edit="openEdit(empleado)" @delete="remove(empleado.id_empleado)" />
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="store.empleados.length === 0" class="text-center py-8 text-gray-500">
        No hay empleados registrados
      </div>
    </div>
    
    <Modal :open="showModal" :title="editingEmpleado ? 'Editar Empleado' : 'Nuevo Empleado'" @close="showModal = false">
      <form @submit.prevent="save" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Documento *</label>
            <input v-model="form.documento" class="input" required />
          </div>
          <div>
            <label class="label">Nombre *</label>
            <input v-model="form.nombre" class="input" required />
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
            <label class="label">Cargo *</label>
            <input v-model="form.cargo" class="input" required />
          </div>
          <div>
            <label class="label">Fecha Contrato</label>
            <input v-model="form.fecha_contrato" type="date" class="input" />
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