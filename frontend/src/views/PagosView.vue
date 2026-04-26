<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { pagosApi } from '@/api/pagos'
import { ordenesApi } from '@/api/ordenes'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus } from 'lucide-vue-next'
import type { Pago, Orden } from '@/types'

const pagos = ref<Pago[]>([])
const ordenes = ref<Orden[]>([])
const loading = ref(false)
const showModal = ref(false)

const form = ref({
  id_orden: 0,
  monto: 0,
  metodo_pago: 'Efectivo',
  numero_referencia: '',
  observaciones: ''
})

onMounted(async () => {
  loading.value = true
  try {
    const [pagosRes, ordenesRes] = await Promise.all([
      pagosApi.listar(),
      ordenesApi.listar()
    ])
    pagos.value = pagosRes.data
    ordenes.value = ordenesRes.data
  } catch (e) {
    console.error('Error cargando datos', e)
  } finally {
    loading.value = false
  }
})

function openCreate() {
  form.value = { id_orden: 0, monto: 0, metodo_pago: 'Efectivo', numero_referencia: '', observaciones: '' }
  showModal.value = true
}

async function save() {
  await pagosApi.registrar(form.value)
  showModal.value = false
  const { data } = await pagosApi.listar()
  pagos.value = data
}

async function remove(id: number) {
  if (confirm('¿Está seguro de eliminar este pago?')) {
    await pagosApi.eliminar(id)
    const { data } = await pagosApi.listar()
    pagos.value = data
  }
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value)
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Pagos</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Registrar Pago
      </button>
    </div>
    
    <LoadingSpinner v-if="loading" />
    
    <div v-else class="card">
      <table class="w-full">
        <thead>
          <tr class="table-header">
            <th class="table-cell">Fecha</th>
            <th class="table-cell">Orden</th>
            <th class="table-cell">Cliente</th>
            <th class="table-cell">Monto</th>
            <th class="table-cell">Método</th>
            <th class="table-cell">Referencia</th>
            <th class="table-cell">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pago in pagos" :key="pago.id_pago" class="border-b hover:bg-gray-50">
            <td class="table-cell">{{ new Date(pago.fecha_pago).toLocaleDateString() }}</td>
            <td class="table-cell font-medium">{{ pago.numero_orden }}</td>
            <td class="table-cell">{{ pago.cliente }}</td>
            <td class="table-cell text-green-600 font-medium">{{ formatCurrency(pago.monto) }}</td>
            <td class="table-cell">{{ pago.metodo_pago }}</td>
            <td class="table-cell">{{ pago.numero_referencia || '-' }}</td>
            <td class="table-cell">
              <TableActions :actions="['delete']" @delete="remove(pago.id_pago)" />
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="pagos.length === 0" class="text-center py-8 text-gray-500">
        No hay pagos registrados
      </div>
    </div>
    
    <Modal :open="showModal" title="Registrar Pago" @close="showModal = false">
      <form @submit.prevent="save" class="space-y-4">
        <div>
          <label class="label">Orden *</label>
          <select v-model="form.id_orden" class="input" required>
            <option value="0">Seleccionar orden</option>
            <option v-for="o in ordenes" :key="o.id_orden" :value="o.id_orden">
              {{ o.numero_orden }} - {{ o.cliente }} - {{ formatCurrency(o.total) }}
            </option>
          </select>
        </div>
        <div>
          <label class="label">Monto *</label>
          <input v-model.number="form.monto" type="number" class="input" required />
        </div>
        <div>
          <label class="label">Método de Pago</label>
          <select v-model="form.metodo_pago" class="input">
            <option>Efectivo</option>
            <option>Tarjeta</option>
            <option>Transferencia</option>
            <option>Consignación</option>
          </select>
        </div>
        <div>
          <label class="label">Número de Referencia</label>
          <input v-model="form.numero_referencia" class="input" />
        </div>
        <div>
          <label class="label">Observaciones</label>
          <textarea v-model="form.observaciones" class="input" rows="2"></textarea>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" class="btn btn-primary">Registrar</button>
        </div>
      </form>
    </Modal>
  </div>
</template>