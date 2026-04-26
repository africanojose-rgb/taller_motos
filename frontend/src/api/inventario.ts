import client from './client'
import type { Producto, Categoria } from '@/types'

export const inventarioApi = {
  listarProductos: () => client.get('/inventario/productos'),
  obtenerProducto: (id) => client.get(`/inventario/productos/${id}`),
  crearProducto: (data) => client.post('/inventario/productos', data),
  actualizarProducto: (id, data) => client.put(`/inventario/productos/${id}`, data),
  eliminarProducto: (id) => client.delete(`/inventario/productos/${id}`),
  listarCategorias: () => client.get('/inventario/categorias'),
  crearCategoria: (data) => client.post('/inventario/categorias', data),
  listarKardex: () => client.get('/inventario/kardex'),
  registrarMovimiento: (data) => client.post('/inventario/kardex', data),
  stockBajo: () => client.get('/inventario/stock-bajo')
}