import { defineStore } from 'pinia'
import { ref } from 'vue'
import { clientesApi } from '@/api/clientes'
import type { Cliente } from '@/types'

export const useClientesStore = defineStore('clientes', () => {
  const clientes = ref<Cliente[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const { data } = await clientesApi.listar()
      clientes.value = data
    } catch (e) {
      error.value = 'Error cargando clientes'
    } finally {
      loading.value = false
    }
  }

  async function crear(payload: Omit<Cliente, 'id_cliente' | 'estado' | 'fecha_registro'>) {
    const { data } = await clientesApi.crear(payload)
    await fetchAll()
    return data.id_cliente
  }

  async function actualizar(id: number, payload: Partial<Cliente>) {
    await clientesApi.actualizar(id, payload)
    await fetchAll()
  }

  async function eliminar(id: number) {
    await clientesApi.eliminar(id)
    await fetchAll()
  }

  return { clientes, loading, error, fetchAll, crear, actualizar, eliminar }
})