<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/AppSidebar.vue'
import AppNavbar from '@/components/AppNavbar.vue'

const route = useRoute()
</script>

<template>
  <div class="flex min-h-screen">
    <AppSidebar />
    <div class="flex-1 flex flex-col">
      <AppNavbar />
      <main class="flex-1 p-6 overflow-auto">
        <RouterView />
      </main>
    </div>
  </div>
</template>