import { defineStore } from 'pinia'
import { ref } from 'vue'
import { motociletasApi } from '@/api/motociletas'
import type { Motocicleta } from '@/types'

export const useMotoStore = defineStore('moto', () => {
  const motociletas = ref<Motocicleta[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await motociletasApi.listar()
      motociletas.value = data
    } catch (e) {
      error.value = 'Error cargando motociletas'
    } finally {
      loading.value = false
    }
  }

  async function crear(payload: any) {
    const { data } = await motociletasApi.crear(payload)
    await fetchAll()
    return data.id_moto
  }

  async function eliminar(id: number) {
    await motociletasApi.eliminar(id)
    await fetchAll()
  }

  async function actualizar(id: number, payload: any) {
    await motociletasApi.actualizar(id, payload)
    await fetchAll()
  }

  return { motociletas, loading, error, fetchAll, crear, actualizar, eliminar }
})
