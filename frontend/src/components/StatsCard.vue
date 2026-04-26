<script setup lang="ts">
defineProps<{
  title: string
  value: string | number
  color?: 'secondary' | 'success' | 'warning' | 'danger'
}>()
</script>

<template>
  <div class="card border-l-4" :class="`border-l-${color || 'secondary'}`">
    <p class="text-sm text-gray-500 uppercase tracking-wide">{{ title }}</p>
    <p class="text-2xl font-bold text-gray-800">{{ value }}</p>
  </div>
</template>