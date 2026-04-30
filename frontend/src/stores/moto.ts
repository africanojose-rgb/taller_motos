import { defineStore } from 'pinia'
import { ref } from 'vue'
import { motocicletasApi } from '@/api/motocicletas'
import type { Motocicleta } from '@/types'

export const useMotoStore = defineStore('moto', () => {
  const motocicletas = ref<Motocicleta[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await motocicletasApi.listar()
      motocicletas.value = data
    } catch (e) {
      error.value = 'Error cargando motocicletas'
    } finally {
      loading.value = false
    }
  }

  async function crear(payload: any) {
    const { data } = await motocicletasApi.crear(payload)
    await fetchAll()
    return data.id_moto
  }

  async function eliminar(id: number) {
    await motocicletasApi.eliminar(id)
    await fetchAll()
  }

  async function actualizar(id: number, payload: any) {
    await motocicletasApi.actualizar(id, payload)
    await fetchAll()
  }

  return { motocicletas, loading, error, fetchAll, crear, actualizar, eliminar }
})
