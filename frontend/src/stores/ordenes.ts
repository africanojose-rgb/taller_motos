import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ordenesApi } from '@/api/ordenes'
import type { Orden } from '@/types'

export const useOrdenesStore = defineStore('ordenes', () => {
  const ordenes = ref<Orden[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await ordenesApi.listar()
      ordenes.value = data
    } catch (e) {
      error.value = 'Error cargando órdenes'
    } finally {
      loading.value = false
    }
  }

  async function obtener(id: number) {
    const { data } = await ordenesApi.obtener(id)
    return data
  }

  async function crear(payload: { id_moto: number; id_cliente: number; id_empleado?: number; kilometraje_ingreso?: number; observaciones?: string }) {
    const { data } = await ordenesApi.crear(payload)
    await fetchAll()
    return data
  }

  async function agregarServicio(idOrden: number, idServicio: number, cantidad = 1) {
    await ordenesApi.agregarDetalle(idOrden, { id_servicio: idServicio, cantidad })
  }

  async function agregarProducto(idOrden: number, idServicio: number | null, cantidad: number, idProducto: number | null = null, precioUnitario: number = 0) {
    if (idProducto) {
      await ordenesApi.agregarDetalle(idOrden, { id_producto: idProducto, cantidad, precio_unitario: precioUnitario })
    } else {
      await ordenesApi.agregarDetalle(idOrden, { id_servicio: idServicio, cantidad })
    }
  }

  async function entregar(id: number, kilometrajeSalida?: number) {
    await ordenesApi.entregar(id, kilometrajeSalida)
    await fetchAll()
  }

  return { ordenes, loading, error, fetchAll, obtener, crear, agregarServicio, agregarProducto, entregar }
})