import { defineStore } from 'pinia'
import { ref } from 'vue'
import { inventarioApi } from '@/api/inventario'
import type { Producto, Categoria } from '@/types'

export const useInventarioStore = defineStore('inventario', () => {
  const productos = ref<Producto[]>([])
  const categorias = ref<Categoria[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchProductos() {
    loading.value = true
    try {
      const { data } = await inventarioApi.listarProductos()
      productos.value = data
    } catch (e) {
      error.value = 'Error cargando productos'
    } finally {
      loading.value = false
    }
  }

  async function fetchCategorias() {
    const { data } = await inventarioApi.listarCategorias()
    categorias.value = data
  }

  async function crearProducto(payload: Partial<Producto>) {
    const { data } = await inventarioApi.crearProducto(payload)
    await fetchProductos()
    return data.id_producto
  }

  async function actualizarProducto(id: number, payload: Partial<Producto>) {
    await inventarioApi.actualizarProducto(id, payload)
    await fetchProductos()
  }

  async function eliminarProducto(id: number) {
    await inventarioApi.eliminarProducto(id)
    await fetchProductos()
  }

  async function registrarMovimiento(payload: any) {
    await inventarioApi.registrarMovimiento(payload)
    await fetchProductos()
  }

  async function fetchStockBajo() {
    const { data } = await inventarioApi.stockBajo()
    return data
  }

  return { productos, categorias, loading, error, fetchProductos, fetchCategorias, crearProducto, actualizarProducto, eliminarProducto, registrarMovimiento, fetchStockBajo }
})