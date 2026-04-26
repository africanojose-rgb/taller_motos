<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps<{
  open: boolean
  title: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl'
}>()

const emit = defineEmits<{
  close: []
}>()

const isOpen = computed({
  get: () => props.open,
  set: (val) => { if (!val) emit('close') }
})

const sizeClass = computed(() => {
  const sizes = {
    'sm': 'max-w-sm',
    'md': 'max-w-lg',
    'lg': 'max-w-2xl',
    'xl': 'max-w-4xl',
    '2xl': 'max-w-5xl',
    '3xl': 'max-w-6xl'
  }
  return sizes[props.size || 'md']
})
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <dialog 
      :open="isOpen"
      class="bg-white rounded-xl shadow-2xl w-full mx-4 max-h-[90vh] overflow-auto"
      :class="sizeClass"
      @click.stop
    >
      <div class="p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">{{ title }}</h3>
          <button @click="emit('close')" class="p-1 hover:bg-gray-100 rounded">
            <X class="w-5 h-5" />
          </button>
        </div>
        <slot></slot>
      </div>
    </dialog>
  </div>
</template>

<style scoped>
dialog {
  padding: 0;
}
</style>