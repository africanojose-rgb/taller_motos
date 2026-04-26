import { defineStore } from 'pinia'
import { ref } from 'vue'
import { vehiculosApi } from '@/api/vehiculos'
import type { Vehiculo, Marca, Modelo } from '@/types'

export const useVehiculosStore = defineStore('vehiculos', () => {
  const vehiculos = ref<Vehiculo[]>([])
  const marcas = ref<Marca[]>([])
  const modelos = ref<Modelo[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchVehiculos() {
    loading.value = true
    try {
      const { data } = await vehiculosApi.listar()
      vehiculos.value = data
    } catch (e) {
      error.value = 'Error cargando vehículos'
    } finally {
      loading.value = false
    }
  }

  async function fetchMarcas() {
    const { data } = await vehiculosApi.listarMarcas()
    marcas.value = data
  }

  async function fetchModelos(idMarca: number) {
    const { data } = await vehiculosApi.listarModelos(idMarca)
    modelos.value = data
  }

  async function crear(payload: Omit<Vehiculo, 'id_vehiculo' | 'estado' | 'cliente' | 'modelo' | 'marca'>) {
    const { data } = await vehiculosApi.crear(payload)
    await fetchVehiculos()
    return data.id_vehiculo
  }

  async function actualizar(id: number, payload: Partial<Vehiculo>) {
    await vehiculosApi.actualizar(id, payload)
    await fetchVehiculos()
  }

  async function eliminar(id: number) {
    await vehiculosApi.eliminar(id)
    await fetchVehiculos()
  }

  return { vehiculos, marcas, modelos, loading, error, fetchVehiculos, fetchMarcas, fetchModelos, crear, actualizar, eliminar }
})