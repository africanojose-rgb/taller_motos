<script setup lang="ts">
import { Trash2, Edit, Eye, CheckCircle } from 'lucide-vue-next'

defineProps<{
  actions?: ('edit' | 'delete' | 'view' | 'complete')[]
}>()

const emit = defineEmits<{
  edit: []
  delete: []
  view: []
  complete: []
}>()
</script>

<template>
  <div class="flex gap-2">
    <button 
      v-if="actions?.includes('view')"
      @click="emit('view')"
      class="p-1.5 hover:bg-gray-100 rounded text-blue-600"
      title="Ver"
    >
      <Eye class="w-4 h-4" />
    </button>
    <button 
      v-if="actions?.includes('edit')"
      @click="emit('edit')"
      class="p-1.5 hover:bg-gray-100 rounded text-gray-600"
      title="Editar"
    >
      <Edit class="w-4 h-4" />
    </button>
    <button 
      v-if="actions?.includes('complete')"
      @click="emit('complete')"
      class="p-1.5 hover:bg-gray-100 rounded text-green-600"
      title="Completar"
    >
      <CheckCircle class="w-4 h-4" />
    </button>
    <button 
      v-if="actions?.includes('delete')"
      @click="emit('delete')"
      class="p-1.5 hover:bg-gray-100 rounded text-red-600"
      title="Eliminar"
    >
      <Trash2 class="w-4 h-4" />
    </button>
  </div>
</template>