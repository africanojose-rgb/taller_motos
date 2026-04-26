<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useVehiculosStore } from '@/stores/vehiculos'
import { useClientesStore } from '@/stores/clientes'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus, Search } from 'lucide-vue-next'
import type { Vehiculo } from '@/types'

const vehiculos = useVehiculosStore()
const clientes = useClientesStore()
const showModal = ref(false)
const editingVehiculo = ref<Vehiculo | null>(null)
const searchQuery = ref('')

const form = ref({
  id_cliente: 0,
  id_modelo: 0,
  placa: '',
  color: '',
  kilometraje: 0,
  vin: ''
})

const selectedMarca = ref(0)

onMounted(() => {
  vehiculos.fetchVehiculos()
  vehiculos.fetchMarcas()
  clientes.fetchAll()
})

watch(selectedMarca, async (marcaId) => {
  if (marcaId) {
    vehiculos.fetchModelos(marcaId)
  }
})

function openCreate() {
  editingVehiculo.value = null
  selectedMarca.value = 0
  form.value = { id_cliente: 0, id_modelo: 0, placa: '', color: '', kilometraje: 0, vin: '' }
  showModal.value = true
}

function openEdit(vehiculo: Vehiculo) {
  editingVehiculo.value = vehiculo
  form.value = { ...vehiculo }
  showModal.value = true
}

async function save() {
  if (editingVehiculo.value) {
    await vehiculos.actualizar(editingVehiculo.value.id_vehiculo, form.value)
  } else {
    await vehiculos.crear(form.value)
  }
  showModal.value = false
}

async function remove(id: number) {
  if (confirm('¿Está seguro de eliminar este vehículo?')) {
    await vehiculos.eliminar(id)
  }
}

const filteredVehiculos = () => {
  if (!searchQuery.value) return vehiculos.vehiculos
  const q = searchQuery.value.toLowerCase()
  return vehiculos.vehiculos.filter(v => 
    v.placa.toLowerCase().includes(q) || 
    v.cliente?.toLowerCase().includes(q)
  )
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Vehículos</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Nuevo Vehículo
      </button>
    </div>
    
    <LoadingSpinner v-if="vehiculos.loading" />
    
    <div v-else class="card">
      <div class="mb-4">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input v-model="searchQuery" type="text" class="input pl-10" placeholder="Buscar vehículo..." />
        </div>
      </div>
      
      <table class="w-full">
        <thead>
          <tr class="table-header">
            <th class="table-cell">Placa</th>
            <th class="table-cell">Marca/Modelo</th>
            <th class="table-cell">Cliente</th>
            <th class="table-cell">Color</th>
            <th class="table-cell">Kilometraje</th>
            <th class="table-cell">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="vehiculo in filteredVehiculos()" :key="vehiculo.id_vehiculo" class="border-b hover:bg-gray-50">
            <td class="table-cell font-medium">{{ vehiculo.placa }}</td>
            <td class="table-cell">{{ vehiculo.marca }} {{ vehiculo.modelo }}</td>
            <td class="table-cell">{{ vehiculo.cliente }}</td>
            <td class="table-cell">{{ vehiculo.color || '-' }}</td>
            <td class="table-cell">{{ vehiculo.kilometraje?.toLocaleString() || '-' }}</td>
            <td class="table-cell">
              <TableActions :actions="['edit', 'delete']" @edit="openEdit(vehiculo)" @delete="remove(vehiculo.id_vehiculo)" />
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="vehiculos.vehiculos.length === 0" class="text-center py-8 text-gray-500">
        No hay vehículos registrados
      </div>
    </div>
    
    <Modal :open="showModal" :title="editingVehiculo ? 'Editar Vehículo' : 'Nuevo Vehículo'" @close="showModal = false">
      <form @submit.prevent="save" class="space-y-4">
        <div>
          <label class="label">Cliente *</label>
          <select v-model="form.id_cliente" class="input" required>
            <option value="0">Seleccionar cliente</option>
            <option v-for="c in clientes.clientes" :key="c.id_cliente" :value="c.id_cliente">
              {{ c.nombre }}
            </option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Marca *</label>
            <select v-model="selectedMarca" class="input" required>
              <option value="0">Seleccionar marca</option>
              <option v-for="m in vehiculos.marcas" :key="m.id_marca" :value="m.id_marca">
                {{ m.nombre }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Modelo *</label>
            <select v-model="form.id_modelo" class="input" required>
              <option value="0">Seleccionar modelo</option>
              <option v-for="mo in vehiculos.modelos" :key="mo.id_modelo" :value="mo.id_modelo">
                {{ mo.nombre }}
              </option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Placa *</label>
            <input v-model="form.placa" class="input uppercase" required />
          </div>
          <div>
            <label class="label">Color</label>
            <input v-model="form.color" class="input" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Kilometraje</label>
            <input v-model.number="form.kilometraje" type="number" class="input" />
          </div>
          <div>
            <label class="label">VIN</label>
            <input v-model="form.vin" class="input uppercase" />
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