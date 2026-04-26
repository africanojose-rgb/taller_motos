import { defineStore } from 'pinia'
import { ref } from 'vue'
import { nominaApi } from '@/api/nomina'

export const useNominaStore = defineStore('nomina', () => {
  const comisiones = ref<any[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchComisiones() {
    loading.value = true
    try {
      const { data } = await nominaApi.listarComisiones()
      comisiones.value = data
    } catch (e) {
      error.value = 'Error cargando comisiones'
    } finally {
      loading.value = false
    }
  }

  async function crearComision(idEmpleado: number, payload: any) {
    const { data } = await nominaApi.crearComision(idEmpleado, payload)
    await fetchComisiones()
    return data.id_comision
  }

  async function actualizarComision(id: number, payload: any) {
    await nominaApi.actualizarComision(id, payload)
    await fetchComisiones()
  }

  async function eliminarComision(id: number) {
    await nominaApi.eliminarComision(id)
    await fetchComisiones()
  }

  async function calcularComisiones(idEmpleado: number, params?: any) {
    const { data } = await nominaApi.calcularComisiones(idEmpleado, params)
    return data
  }

  return { comisiones, loading, error, fetchComisiones, crearComision, actualizarComision, eliminarComision, calcularComisiones }
})