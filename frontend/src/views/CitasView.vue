<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCitasStore } from '@/stores/citas'
import { useClientesStore } from '@/stores/clientes'
import { useMotoStore } from '@/stores/moto'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus } from 'lucide-vue-next'
import type { Cita } from '@/types'

const store = useCitasStore()
const clientes = useClientesStore()
const motocicletas = useMotoStore()
const showModal = ref(false)
const editingCita = ref<Cita | null>(null)

const form = ref({
  id_cliente: 0,
  id_vehiculo: 0,
  fecha_cita: '',
  hora_cita: '',
  servicio: '',
  observaciones: ''
})

onMounted(() => {
  store.fetchAll()
  clientes.fetchAll()
  motocicletas.fetchAll()
})

function openCreate() {
  editingCita.value = null
  form.value = { id_cliente: 0, id_vehiculo: 0, fecha_cita: '', hora_cita: '', servicio: '', observaciones: '' }
  showModal.value = true
}

function openEdit(cita: Cita) {
  editingCita.value = cita
  form.value = { ...cita, fecha_cita: cita.fecha_cita.split(' ')[0] }
  showModal.value = true
}

async function save() {
  if (editingCita.value) {
    await store.actualizar(editingCita.value.id_cita, form.value)
  } else {
    await store.crear(form.value)
  }
  showModal.value = false
  store.fetchAll()
}

async function remove(id: number) {
  if (confirm('¿Está seguro de eliminar esta cita?')) {
    await store.eliminar(id)
  }
}

function getStatusClass(estado: string) {
  const classes: Record<string, string> = {
    'Programada': 'badge-warning',
    'Completada': 'badge-success',
    'Cancelada': 'badge-danger'
  }
  return classes[estado] || 'bg-gray-100'
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Citas</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Nueva Cita
      </button>
    </div>
    
    <LoadingSpinner v-if="store.loading" />
    
    <div v-else class="card">
      <table class="w-full">
        <thead>
          <tr class="table-header">
            <th class="table-cell">Fecha</th>
            <th class="table-cell">Hora</th>
            <th class="table-cell">Cliente</th>
            <th class="table-cell">Vehículo</th>
            <th class="table-cell">Servicio</th>
            <th class="table-cell">Estado</th>
            <th class="table-cell">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cita in store.citas" :key="cita.id_cita" class="border-b hover:bg-gray-50">
            <td class="table-cell">{{ new Date(cita.fecha_cita).toLocaleDateString() }}</td>
            <td class="table-cell">{{ cita.hora_cita }}</td>
            <td class="table-cell">{{ cita.cliente }}</td>
            <td class="table-cell">{{ cita.vehiculo }}</td>
            <td class="table-cell">{{ cita.servicio || '-' }}</td>
            <td class="table-cell">
              <span class="badge" :class="getStatusClass(cita.estado)">{{ cita.estado }}</span>
            </td>
            <td class="table-cell">
              <TableActions :actions="['edit', 'delete']" @edit="openEdit(cita)" @delete="remove(cita.id_cita)" />
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="store.citas.length === 0" class="text-center py-8 text-gray-500">
        No hay citas registradas
      </div>
    </div>
    
    <Modal :open="showModal" :title="editingCita ? 'Editar Cita' : 'Nueva Cita'" @close="showModal = false">
      <form @submit.prevent="save" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Cliente *</label>
            <select v-model="form.id_cliente" class="input" required>
              <option value="0">Seleccionar</option>
              <option v-for="c in clientes.clientes" :key="c.id_cliente" :value="c.id_cliente">
                {{ c.nombre }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Motocicleta *</label>
            <select v-model="form.id_moto" class="input" required>
              <option value="0">Seleccionar</option>
              <option v-for="m in motocicletas.motocicletas" :key="m.id_moto" :value="m.id_moto">
                {{ m.placa }}
              </option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Fecha *</label>
            <input v-model="form.fecha_cita" type="date" class="input" required />
          </div>
          <div>
            <label class="label">Hora *</label>
            <input v-model="form.hora_cita" type="time" class="input" required />
          </div>
        </div>
        <div>
          <label class="label">Servicio</label>
          <input v-model="form.servicio" class="input" />
        </div>
        <div>
          <label class="label">Observaciones</label>
          <textarea v-model="form.observaciones" class="input" rows="2"></textarea>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" class="btn btn-primary">Guardar</button>
        </div>
      </form>
    </Modal>
  </div>
</template>