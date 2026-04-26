<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useReportesStore } from '@/stores/reportes'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const reportes = useReportesStore()
const periodo = ref('mes')
const customFechaInicio = ref('')
const customFechaFin = ref('')

onMounted(() => {
  reportes.fetchResumen()
  reportes.fetchServiciosPopulares()
  reportes.fetchClientesFrecuentes()
  loadIngresos()
})

function loadIngresos() {
  if (customFechaInicio.value && customFechaFin.value) {
    reportes.fetchIngresos(undefined, customFechaInicio.value, customFechaFin.value)
  } else {
    reportes.fetchIngresos(periodo.value)
  }
}

function onPeriodoChange() {
  reportes.fetchIngresos(periodo.value)
}

const ingresosChartData = computed(() => ({
  labels: ['Mano de Obra', 'Repuestos'],
  datasets: [{
    label: 'Ingresos',
    data: [
      reportes.ingresos?.mano_obra || 0,
      reportes.ingresos?.repuestos || 0
    ],
    backgroundColor: ['#3498db', '#e74c3c']
  }]
}))

const serviciosChartData = {
  labels: [] as string[],
  datasets: [{
    label: 'Servicios',
    data: [] as number[],
    backgroundColor: '#3498db'
  }]
}

const serviciosOptions = {
  responsive: true,
  maintainAspectRatio: false
}

const clientesChartData = {
  labels: [] as string[],
  datasets: [{
    label: 'Órdenes',
    data: [] as number[],
    backgroundColor: '#27ae60'
  }]
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value)
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Reportes BI</h1>
    
    <LoadingSpinner v-if="reportes.loading" />
    
    <div v-else class="space-y-6">
      <!-- Ingresos -->
      <div class="card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">Ingresos</h3>
          <div class="flex gap-2">
            <select v-model="periodo" @change="onPeriodoChange" class="input">
              <option value="mes">Mes Actual</option>
              <option value="anio">Año Actual</option>
            </select>
            <input v-model="customFechaInicio" type="date" class="input" placeholder="Desde" />
            <input v-model="customFechaFin" type="date" class="input" placeholder="Hasta" />
            <button @click="loadIngresos" class="btn btn-primary">Buscar</button>
          </div>
        </div>
        
        <div v-if="reportes.ingresos" class="grid grid-cols-3 gap-4">
          <div class="p-4 bg-blue-50 rounded-lg">
            <p class="text-sm text-gray-500">Mano de Obra</p>
            <p class="text-xl font-bold text-blue-600">{{ formatCurrency(reportes.ingresos.mano_obra) }}</p>
          </div>
          <div class="p-4 bg-red-50 rounded-lg">
            <p class="text-sm text-gray-500">Repuestos</p>
            <p class="text-xl font-bold text-red-600">{{ formatCurrency(reportes.ingresos.repuestos) }}</p>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-sm text-gray-500">Total</p>
            <p class="text-xl font-bold">{{ formatCurrency(reportes.ingresos.total) }}</p>
          </div>
        </div>
        
        <div v-if="reportes.ingresos" class="h-48 mt-4">
          <Bar :data="ingresosChartData" :options="serviciosOptions" />
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          No hay datos disponibles
        </div>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="card">
          <h3 class="text-lg font-semibold mb-4">Servicios Populares</h3>
          <div class="h-64">
            <Bar 
              v-if="reportes.serviciosPopulares.length > 0"
              :data="serviciosChartData"
              :options="serviciosOptions"
            />
            <div v-else class="flex items-center justify-center h-full text-gray-500">
              No hay datos disponibles
            </div>
          </div>
        </div>
        
        <div class="card">
          <h3 class="text-lg font-semibold mb-4">Top 10 Clientes</h3>
          <div class="h-64">
            <Bar 
              v-if="reportes.clientesFrecuentes.length > 0"
              :data="clientesChartData"
              :options="serviciosOptions"
            />
            <div v-else class="flex items-center justify-center h-full text-gray-500">
              No hay datos disponibles
            </div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">Top Clientes Frecuentes</h3>
        <table class="w-full">
          <thead>
            <tr class="table-header">
              <th class="table-cell">Cliente</th>
              <th class="table-cell">Vehículos</th>
              <th class="table-cell">Órdenes</th>
              <th class="table-cell">Total Gastado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cliente in reportes.clientesFrecuentes" :key="cliente.nombre" class="border-b">
              <td class="table-cell font-medium">{{ cliente.nombre }}</td>
              <td class="table-cell">{{ cliente.vehiculos }}</td>
              <td class="table-cell">{{ cliente.ordenes }}</td>
              <td class="table-cell">{{ formatCurrency(cliente.total_gastado) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="reportes.clientesFrecuentes.length === 0" class="text-center py-8 text-gray-500">
          No hay datos disponibles
        </div>
      </div>
    </div>
  </div>
</template>