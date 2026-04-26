<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMarcasMotosStore } from '@/stores/marcasMotos'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus, Bike, X } from 'lucide-vue-next'
import type { Marca } from '@/types'

const store = useMarcasMotosStore()
const showModal = ref(false)
const showModelosModal = ref(false)
const editingMarca = ref<Marca | null>(null)
const selectedMarca = ref<Marca | null>(null)

const form = ref({
  nombre: '',
  logo: ''
})

const modeloForm = ref({
  nombre: '',
  cilindrada: '',
  anio_inicio: new Date().getFullYear(),
  anio_fin: null as number | null
})

onMounted(() => store.fetchMarcas())

function openCreate() {
  editingMarca.value = null
  form.value = { nombre: '', logo: '' }
  showModal.value = true
}

function openEdit(marca: Marca) {
  editingMarca.value = marca
  form.value = { ...marca }
  showModal.value = true
}

async function save() {
  await store.crearMarca(form.value)
  showModal.value = false
  store.fetchMarcas()
}

async function remove(id: number) {
  if (confirm('¿Eliminar esta marca?')) {
    await store.eliminarMarca(id)
  }
}

function openModelos(marca: Marca) {
  selectedMarca.value = marca
  store.fetchModelos(marca.id_marca)
  modeloForm.value = { nombre: '', cilindrada: '', anio_inicio: new Date().getFullYear(), anio_fin: null }
  showModelosModal.value = true
}

async function addModelo() {
  if (!selectedMarca.value || !modeloForm.value.nombre) return
  await store.crearModelo(selectedMarca.value.id_marca, {
    nombre: modeloForm.value.nombre,
    cilindrada: modeloForm.value.cilindrada || null,
    anio_inicio: modeloForm.value.anio_inicio,
    anio_fin: modeloForm.value.anio_fin
  })
  await store.fetchModelos(selectedMarca.value.id_marca)
  modeloForm.value = { nombre: '', cilindrada: '', anio_inicio: new Date().getFullYear(), anio_fin: null }
}

async function removeModelo(id: number) {
  if (!selectedMarca.value) return
  if (confirm('¿Eliminar este modelo?')) {
    await store.eliminarModelo(id)
    await store.fetchModelos(selectedMarca.value.id_marca)
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Marcas de Motos</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Nueva Marca
      </button>
    </div>
    
    <LoadingSpinner v-if="store.loading" />
    
    <div v-else class="card">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div 
          v-for="marca in store.marcas" 
          :key="marca.id_marca"
          class="p-4 border rounded-lg hover:bg-gray-50"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Bike class="w-5 h-5 text-secondary" />
              <span class="font-medium">{{ marca.nombre }}</span>
            </div>
            <div class="flex items-center gap-1">
              <button @click="openModelos(marca)" class="text-secondary hover:text-primary text-sm">
                Modelos
              </button>
              <button @click="remove(marca.id_marca)" class="text-red-500 hover:text-red-700">
                <X class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="store.marcas.length === 0" class="text-center py-8 text-gray-500">
        No hay marcas registradas
      </div>
    </div>
    
    <Modal :open="showModal" :title="editingMarca ? 'Editar Marca' : 'Nueva Marca'" @close="showModal = false">
      <form @submit.prevent="save" class="space-y-4">
        <div>
          <label class="label">Nombre *</label>
          <input v-model="form.nombre" class="input" required />
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" class="btn btn-primary">Guardar</button>
        </div>
      </form>
    </Modal>
    
    <Modal :open="showModelosModal" :title="`Modelos - ${selectedMarca?.nombre}`" @close="showModelosModal = false" size="lg">
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="label">Nombre Modelo *</label>
            <input v-model="modeloForm.nombre" class="input" placeholder="Ej: Duke 390" />
          </div>
          <div>
            <label class="label">Cilindrada</label>
            <input v-model="modeloForm.cilindrada" class="input" placeholder="Ej: 390cc" />
          </div>
          <div>
            <label class="label">Año Inicio</label>
            <input v-model.number="modeloForm.anio_inicio" type="number" class="input" />
          </div>
          <div>
            <label class="label">Año Fin</label>
            <input v-model.number="modeloForm.anio_fin" type="number" class="input" placeholder="Vacío = actual" />
          </div>
        </div>
        <button @click="addModelo" class="btn btn-primary">Agregar Modelo</button>
        
        <div v-if="store.modelos.length > 0" class="mt-4">
          <h4 class="font-semibold mb-2">Modelos registrados</h4>
          <table class="w-full text-sm">
            <thead>
              <tr class="table-header">
                <th class="table-cell">Nombre</th>
                <th class="table-cell">Cilindrada</th>
                <th class="table-cell">Años</th>
                <th class="table-cell w-10"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in store.modelos" :key="m.id_modelo" class="border-b">
                <td class="table-cell">{{ m.nombre }}</td>
                <td class="table-cell">{{ m.cilindrada || '-' }}</td>
                <td class="table-cell">{{ m.anio_inicio }}{{ m.anio_fin ? '-' + m.anio_fin : '' }}</td>
                <td class="table-cell">
                  <button @click="removeModelo(m.id_modelo)" class="text-red-500 hover:text-red-700">
                    <X class="w-4 h-4" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-4 text-gray-500">
          No hay modelos registrados para esta marca
        </div>
      </div>
    </Modal>
  </div>
</template>