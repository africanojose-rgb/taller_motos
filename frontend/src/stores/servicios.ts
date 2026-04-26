import { defineStore } from 'pinia'
import { ref } from 'vue'
import { serviciosApi } from '@/api/servicios'
import type { Servicio } from '@/types'

export const useServiciosStore = defineStore('servicios', () => {
  const servicios = ref<Servicio[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await serviciosApi.listar()
      servicios.value = data
    } catch (e) {
      error.value = 'Error cargando servicios'
    } finally {
      loading.value = false
    }
  }

  async function crear(payload: { nombre: string; descripcion?: string; precio: number; duracion_estimada?: number }) {
    const { data } = await serviciosApi.crear(payload)
    await fetchAll()
    return data.id_servicio
  }

  async function actualizar(id: number, payload: Partial<Servicio>) {
    await serviciosApi.actualizar(id, payload)
    await fetchAll()
  }

  async function eliminar(id: number) {
    await serviciosApi.eliminar(id)
    await fetchAll()
  }

  return { servicios, loading, error, fetchAll, crear, actualizar, eliminar }
})