import { defineStore } from 'pinia'
import { ref } from 'vue'
import { facturasApi } from '@/api/facturas'
import type { Factura } from '@/types'

export const useFacturasStore = defineStore('facturas', () => {
  const facturas = ref<Factura[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await facturasApi.listar()
      facturas.value = data
    } catch (e) {
      error.value = 'Error cargando facturas'
    } finally {
      loading.value = false
    }
  }

  async function crear(payload: any) {
    const { data } = await facturasApi.crear(payload)
    await fetchAll()
    return data
  }

  async function eliminar(id: number) {
    await facturasApi.eliminar(id)
    await fetchAll()
  }

  async function fetchResumen() {
    const { data } = await facturasApi.resumen()
    return data
  }

  return { facturas, loading, error, fetchAll, crear, eliminar, fetchResumen }
})