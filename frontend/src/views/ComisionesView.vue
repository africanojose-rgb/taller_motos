<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useEmpleadosStore } from '@/stores/empleados'
import { useNominaStore } from '@/stores/nomina'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus, Calculator } from 'lucide-vue-next'

const empleadosStore = useEmpleadosStore()
const nominaStore = useNominaStore()
const showModal = ref(false)
const selectedEmpleado = ref<any>(null)
const calculo = ref<any>(null)
const desde = ref('')
const hasta = ref('')

onMounted(() => {
  empleadosStore.fetchAll()
  nominaStore.fetchComisiones()
})

async function verComisiones(empleado: any) {
  selectedEmpleado.value = empleado
  showModal.value = true
}

async function calcular() {
  if (!selectedEmpleado.value) return
  desde.value = desde.value || '1900-01-01'
  hasta.value = hasta.value || '2100-12-31'
  calculo.value = await nominaStore.calcularComisiones(selectedEmpleado.value.id_empleado, { desde: desde.value, hasta: hasta.value })
}

async function guardarComision() {
  if (!selectedEmpleado.value) return
  await nominaStore.crearComision(selectedEmpleado.value.id_empleado, {
    tipo_comision: 'servicio',
    porcentaje: 10
  })
  nominaStore.fetchComisiones()
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value)
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Comisiones de Empleados</h1>
    </div>
    
    <LoadingSpinner v-if="empleadosStore.loading" />
    
    <div v-else class="space-y-6">
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">Empleados</h3>
        <table class="w-full">
          <thead>
            <tr class="table-header">
              <th class="table-cell">Nombre</th>
              <th class="table-cell">Cargo</th>
              <th class="table-cell">% Servicio</th>
              <th class="table-cell">% Repuesto</th>
              <th class="table-cell">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="emp in empleadosStore.empleados" :key="emp.id_empleado" class="border-b">
              <td class="table-cell font-medium">{{ emp.nombre }}</td>
              <td class="table-cell">{{ emp.cargo }}</td>
              <td class="table-cell">10%</td>
              <td class="table-cell">5%</td>
              <td class="table-cell">
                <button @click="verComisiones(emp)" class="btn btn-primary text-sm py-1 px-3 flex items-center gap-1">
                  <Calculator class="w-4 h-4" />
                  Calcular
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">Resumen Comisiones</h3>
        <table class="w-full">
          <thead>
            <tr class="table-header">
              <th class="table-cell">Empleado</th>
              <th class="table-cell">Tipo</th>
              <th class="table-cell">Porcentaje</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="com in nominaStore.comisiones" :key="com.id_comision" class="border-b">
              <td class="table-cell">{{ com.empleado }}</td>
              <td class="table-cell">{{ com.tipo_comision }}</td>
              <td class="table-cell">{{ com.porcentaje }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <Modal :open="showModal" :title="`Comisiones - ${selectedEmpleado?.nombre}`" @close="showModal = false">
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Desde</label>
            <input v-model="desde" type="date" class="input" />
          </div>
          <div>
            <label class="label">Hasta</label>
            <input v-model="hasta" type="date" class="input" />
          </div>
        </div>
        
        <button @click="calcular" class="btn btn-primary w-full">
          <Calculator class="w-4 h-4 inline mr-2" />
          Calcular Comisiones
        </button>
        
        <div v-if="calculo" class="mt-4 p-4 bg-gray-50 rounded-lg">
          <h4 class="font-semibold mb-2">Resultado</h4>
          <div class="flex justify-between text-lg">
            <span>Total Comisiones:</span>
            <span class="font-bold text-green-600">{{ formatCurrency(calculo.total_comisiones) }}</span>
          </div>
          
          <div v-if="calculo.detalle?.length > 0" class="mt-4">
            <h5 class="font-medium mb-2">Detalle</h5>
            <table class="w-full text-sm">
              <thead>
                <tr class="table-header">
                  <th>Orden</th>
                  <th>Base</th>
                  <th>%</th>
                  <th>Comisión</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="d in calculo.detalle" :key="d.id_orden" class="border-b">
                  <td>#{{ d.id_orden }}</td>
                  <td>{{ formatCurrency(d.base) }}</td>
                  <td>{{ d.porcentaje }}%</td>
                  <td>{{ formatCurrency(d.comision) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>