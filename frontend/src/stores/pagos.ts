import { defineStore } from 'pinia'
import { ref } from 'vue'
import { pagosApi } from '@/api/pagos'
import type { Pago } from '@/types'

export const usePagosStore = defineStore('pagos', () => {
  const pagos = ref<Pago[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await pagosApi.listar()
      pagos.value = data
    } catch (e) {
      error.value = 'Error cargando pagos'
    } finally {
      loading.value = false
    }
  }

  async function fetchByOrden(idOrden: number) {
    const { data } = await pagosApi.pagosPorOrden(idOrden)
    return data
  }

  async function registrar(payload: { id_orden: number; monto: number; metodo_pago?: string; numero_referencia?: string; observaciones?: string }) {
    const { data } = await pagosApi.registrar(payload)
    await fetchAll()
    return data.id_pago
  }

  async function eliminar(id: number) {
    await pagosApi.eliminar(id)
    await fetchAll()
  }

  return { pagos, loading, error, fetchAll, fetchByOrden, registrar, eliminar }
})