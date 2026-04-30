<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import { FileText, Settings, Bike, Users, Wrench, Package, Receipt, Calendar, User, Percent, BarChart } from 'lucide-vue-next'
import { computed } from 'vue'

const route = useRoute()

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: FileText },
  { path: '/configuraciones', label: 'Configuraciones', icon: Settings },
  { path: '/marcas', label: 'Marcas', icon: Bike },
  { path: '/clientes', label: 'Clientes', icon: Users },
  { path: '/motocicletas', label: 'Motocicletas', icon: Bike },
  { path: '/ordenes', label: 'Ordenes', icon: Wrench },
  { path: '/servicios', label: 'Servicios', icon: Wrench },
  { path: '/inventario', label: 'Inventario', icon: Package },
  { path: '/facturas', label: 'Facturas', icon: Receipt },
  { path: '/citas', label: 'Citas', icon: Calendar },
  { path: '/empleados', label: 'Empleados', icon: User },
  { path: '/comisiones', label: 'Comisiones', icon: Percent },
  { path: '/reportes', label: 'Reportes', icon: BarChart }
]

const isActive = (path: string) => computed(() => route.path === path)
</script>

<template>
  <aside class="w-64 min-h-screen bg-primary text-white flex flex-col">
    <div class="p-6 border-b border-gray-700">
      <h1 class="text-xl font-bold flex items-center gap-2">
        <Bike class="w-6 h-6" />
        Taller Motos
      </h1>
    </div>
    <nav class="flex-1 py-4 overflow-auto">
      <RouterLink 
        v-for="item in navItems" 
        :key="item.path"
        :to="item.path"
        class="sidebar-link"
        :class="{ 'active': isActive(item.path).value }"
      >
        <component :is="item.icon" class="w-5 h-5" />
        {{ item.label }}
      </RouterLink>
    </nav>
  </aside>
</template>