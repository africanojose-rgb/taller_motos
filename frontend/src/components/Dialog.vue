<script setup lang="ts">
import { ref, computed } from 'vue'

const props = withDefaults(defineProps<{
  show: boolean
  title: string
  loading?: boolean
}>(), {
  loading: false
})

const emit = defineEmits<{
  submit: []
  cancel: []
}>()

const dialogRef = ref<HTMLDialogElement | null>(null)

const isOpen = computed({
  get: () => props.show,
  set: (val) => { if (!val) emit('cancel') }
})
</script>

<template>
  <dialog 
    ref="dialogRef"
    :open="isOpen"
    class="fixed inset-0 z-50 w-full max-w-lg mx-auto rounded-xl shadow-2xl"
    @click.self="emit('cancel')"
  >
    <div class="p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">{{ title }}</h3>
        <button @click="emit('cancel')" class="p-1 hover:bg-gray-100 rounded">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <form @submit.prevent="emit('submit')">
        <slot></slot>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="emit('cancel')" class="btn btn-secondary">
            Cancelar
          </button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </form>
    </div>
  </dialog>
  <div v-if="isOpen" class="fixed inset-0 bg-black/50 z-40" @click="emit('cancel')"></div>
</template>