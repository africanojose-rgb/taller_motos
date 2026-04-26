import { defineStore } from 'pinia'
import { ref } from 'vue'
import { marcasMotosApi } from '@/api/marcasMotos'
import type { Marca, Modelo } from '@/types'

export const useMarcasMotosStore = defineStore('marcasMotos', () => {
  const marcas = ref<Marca[]>([])
  const modelos = ref<Modelo[]>([])
  const loading = ref(false)

  async function fetchMarcas() {
    loading.value = true
    try {
      const { data } = await marcasMotosApi.listar()
      marcas.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchModelos(idMarca: number) {
    const { data } = await marcasMotosApi.listarModelos(idMarca)
    modelos.value = data
  }

  async function crearMarca(payload: { nombre: string; logo?: string }) {
    const { data } = await marcasMotosApi.crear(payload)
    await fetchMarcas()
    return data.id_marca
  }

  async function crearModelo(idMarca: number, payload: any) {
    const { data } = await marcasMotosApi.crearModelo(idMarca, payload)
    await fetchModelos(idMarca)
    return data.id_modelo
  }

  async function eliminarMarca(id: number) {
    await marcasMotosApi.eliminar(id)
    await fetchMarcas()
  }

  async function eliminarModelo(id: number) {
    await marcasMotosApi.eliminarModelo(id)
  }

  return { marcas, modelos, loading, fetchMarcas, fetchModelos, crearMarca, crearModelo, eliminarMarca, eliminarModelo }
})