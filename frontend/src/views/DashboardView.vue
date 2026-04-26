<script setup lang="ts">
import { onMounted } from 'vue'
import { useReportesStore } from '@/stores/reportes'
import StatsCard from '@/components/StatsCard.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Users, Bike, ClipboardList, Package } from 'lucide-vue-next'

const reportes = useReportesStore()

onMounted(() => {
  reportes.fetchResumen()
})

function formatCurrency(value: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value)
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Dashboard</h1>
    
    <LoadingSpinner v-if="reportes.loading" />
    
    <div v-else-if="reportes.resumen" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatsCard title="Clientes" :value="reportes.resumen.total_clientes" color="secondary">
        <template #default>
          <div class="flex items-center gap-2">
            <Users class="w-5 h-5 text-secondary" />
            <span class="text-sm text-gray-500">{{ reportes.resumen.total_clientes }}</span>
          </div>
        </template>
      </StatsCard>
      
      <div class="card border-l-4 border-l-success">
        <p class="text-sm text-gray-500 uppercase tracking-wide">Motociletas</p>
        <div class="flex items-center gap-2 mt-2">
          <Bike class="w-5 h-5 text-success" />
          <p class="text-2xl font-bold">{{ reportes.resumen.total_vehiculos }}</p>
        </div>
      </div>
      
      <div class="card border-l-4 border-l-warning">
        <p class="text-sm text-gray-500 uppercase tracking-wide">Órdenes Activas</p>
        <div class="flex items-center gap-2 mt-2">
          <ClipboardList class="w-5 h-5 text-warning" />
          <p class="text-2xl font-bold">{{ reportes.resumen.ordenes_activas }}</p>
        </div>
      </div>
      
      <div class="card border-l-4 border-l-danger">
        <p class="text-sm text-gray-500 uppercase tracking-wide">Inversión Repuestos</p>
        <div class="flex items-center gap-2 mt-2">
          <Package class="w-5 h-5 text-danger" />
          <p class="text-2xl font-bold">{{ formatCurrency(reportes.resumen.inversion_inventario) }}</p>
        </div>
      </div>
    </div>
    
    <div v-else class="text-center text-gray-500 py-8">
      No hay datos disponibles
    </div>
  </div>
</template>