import { defineStore } from 'pinia'
import { ref } from 'vue'
import { empleadosApi } from '@/api/empleados'
import type { Empleado } from '@/types'

export const useEmpleadosStore = defineStore('empleados', () => {
  const empleados = ref<Empleado[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await empleadosApi.listar()
      empleados.value = data
    } catch (e) {
      error.value = 'Error cargando empleados'
    } finally {
      loading.value = false
    }
  }

  async function crear(payload: { documento: string; nombre: string; telefono?: string; email?: string; cargo: string; fecha_contrato?: string }) {
    const { data } = await empleadosApi.crear(payload)
    await fetchAll()
    return data.id_empleado
  }

  async function actualizar(id: number, payload: Partial<Empleado>) {
    await empleadosApi.actualizar(id, payload)
    await fetchAll()
  }

  async function eliminar(id: number) {
    await empleadosApi.eliminar(id)
    await fetchAll()
  }

  return { empleados, loading, error, fetchAll, crear, actualizar, eliminar }
})