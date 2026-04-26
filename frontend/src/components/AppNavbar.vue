<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { LogOut, User } from 'lucide-vue-next'

const auth = useAuthStore()
</script>

<template>
  <header class="h-16 bg-white border-b flex items-center justify-between px-6">
    <h2 class="text-lg font-semibold text-gray-700">Panel de Gestión</h2>
    <div class="flex items-center gap-4">
      <div class="flex items-center gap-2 text-gray-600">
        <User class="w-4 h-4" />
        <span class="text-sm">{{ auth.user?.nombre }}</span>
      </div>
      <button 
        @click="auth.logout()"
        class="btn btn-secondary flex items-center gap-2"
      >
        <LogOut class="w-4 h-4" />
        Salir
      </button>
    </div>
  </header>
</template>