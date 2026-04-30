<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMarcasMotosStore } from '@/stores/marcasMotos'
import { useClientesStore } from '@/stores/clientes'
import { useMotoStore } from '@/stores/moto'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus, Search } from 'lucide-vue-next'
import type { Motocicleta } from '@/types'

const marcasStore = useMarcasMotosStore()
const clientesStore = useClientesStore()
const store = useMotoStore()

const showModal = ref(false)
const editingMoto = ref<Motocicleta | null>(null)
const searchQuery = ref('')
const selectedMarca = ref<number | null>(null)

const form = ref({
  id_cliente: null as number | null,
  id_modelo: null as number | null,
  placa: '',
  color: '',
  kilometraje: 0,
  vin: '',
  num_serie: '',
  anio: new Date().getFullYear()
})

onMounted(() => {
  store.fetchAll()
  marcasStore.fetchMarcas()
  clientesStore.fetchAll()
})

function onMarcaChange() {
  if (selectedMarca.value) {
    marcasStore.fetchModelos(selectedMarca.value)
  }
}

function openCreate() {
  editingMoto.value = null
  selectedMarca.value = null
  marcasStore.modelos = []
  form.value = {
    id_cliente: null, id_modelo: null, placa: '', color: '',
    kilometraje: 0, vin: '', num_serie: '', anio: new Date().getFullYear()
  }
  showModal.value = true
}

function openEdit(moto: Motocicleta) {
  editingMoto.value = moto
  form.value = { ...moto }
  selectedMarca.value = moto.id_marca
  marcasStore.fetchModelos(moto.id_marca)
  showModal.value = true
}

async function save() {
  if (editingMoto.value) {
    await store.actualizar(editingMoto.value.id_moto, form.value)
  } else {
    await store.crear(form.value)
  }
  showModal.value = false
}

async function remove(id: number) {
  if (confirm('Eliminar esta motocileta?')) {
    await store.eliminar(id)
  }
}

const filtered = () => {
  if (!searchQuery.value) return store.motocicletas
  const q = searchQuery.value.toLowerCase()
  return store.motocicletas.filter(m => 
    m.placa.toLowerCase().includes(q) || m.cliente?.toLowerCase().includes(q)
  )
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Motocicletas</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Nueva Moto
      </button>
    </div>
    
    <LoadingSpinner v-if="store.loading" />
    
    <div v-else class="card">
      <div class="mb-4">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input v-model="searchQuery" type="text" class="input pl-10" placeholder="Buscar motocileta..." />
        </div>
      </div>
      
      <table class="w-full">
        <thead>
          <tr class="table-header">
            <th class="table-cell">Placa</th>
            <th class="table-cell">Marca/Modelo</th>
            <th class="table-cell">Cliente</th>
            <th class="table-cell">Color</th>
            <th class="table-cell">Anio</th>
            <th class="table-cell">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="moto in filtered()" :key="moto.id_moto" class="border-b hover:bg-gray-50">
            <td class="table-cell font-medium">{{ moto.placa }}</td>
            <td class="table-cell">{{ moto.marca }} {{ moto.modelo }}</td>
            <td class="table-cell">{{ moto.cliente }}</td>
            <td class="table-cell">{{ moto.color || '-' }}</td>
            <td class="table-cell">{{ moto.anio || '-' }}</td>
            <td class="table-cell">
              <TableActions :actions="['edit', 'delete']" @edit="openEdit(moto)" @delete="remove(moto.id_moto)" />
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="store.motocicletas.length === 0" class="text-center py-8 text-gray-500">
        No hay motocicletas registradas
      </div>
    </div>
    
    <Modal :open="showModal" :title="editingMoto ? 'Editar Motocileta' : 'Nueva Motocileta'" @close="showModal = false">
      <form @submit.prevent="save" class="space-y-4">
        <div>
          <label class="label">Cliente *</label>
          <select v-model="form.id_cliente" class="input" required>
            <option :value="null">Seleccionar cliente</option>
            <option v-for="c in clientesStore.clientes" :key="c.id_cliente" :value="c.id_cliente">
              {{ c.nombre }}
            </option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Marca *</label>
            <select v-model="selectedMarca" @change="onMarcaChange" class="input" required>
              <option :value="null">Seleccionar marca</option>
              <option v-for="m in marcasStore.marcas" :key="m.id_marca" :value="m.id_marca">
                {{ m.nombre }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Modelo *</label>
            <select v-model="form.id_modelo" class="input" required>
              <option :value="null">Seleccionar modelo</option>
              <option v-for="mo in marcasStore.modelos" :key="mo.id_modelo" :value="mo.id_modelo">
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
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="label">Anio</label>
            <input v-model.number="form.anio" type="number" class="input" />
          </div>
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