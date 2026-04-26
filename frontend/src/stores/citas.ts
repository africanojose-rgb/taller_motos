import { defineStore } from 'pinia'
import { ref } from 'vue'
import { citasApi } from '@/api/citas'
import type { Cita } from '@/types'

export const useCitasStore = defineStore('citas', () => {
  const citas = ref<Cita[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await citasApi.listar()
      citas.value = data
    } catch (e) {
      error.value = 'Error cargando citas'
    } finally {
      loading.value = false
    }
  }

  async function crear(payload: { id_cliente: number; id_vehiculo: number; fecha_cita: string; hora_cita: string; servicio?: string; observaciones?: string }) {
    const { data } = await citasApi.crear(payload)
    await fetchAll()
    return data.id_cita
  }

  async function actualizar(id: number, payload: Partial<Cita>) {
    await citasApi.actualizar(id, payload)
    await fetchAll()
  }

  async function eliminar(id: number) {
    await citasApi.eliminar(id)
    await fetchAll()
  }

  return { citas, loading, error, fetchAll, crear, actualizar, eliminar }
})