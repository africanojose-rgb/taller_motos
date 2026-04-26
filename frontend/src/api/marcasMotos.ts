import client from './client'
import type { Marca, Modelo } from '@/types'

export const marcasMotosApi = {
  listar: () => client.get('/marcas-motos'),
  obtener: (id) => client.get(`/marcas-motos/${id}`),
  crear: (data) => client.post('/marcas-motos', data),
  actualizar: (id, data) => client.put(`/marcas-motos/${id}`, data),
  eliminar: (id) => client.delete(`/marcas-motos/${id}`),
  listarModelos: (id) => client.get(`/marcas-motos/${id}/modelos`),
  crearModelo: (id, data) => client.post(`/marcas-motos/${id}/modelos`, data),
  eliminarModelo: (id) => client.delete(`/marcas-motos/modelos/${id}`)
}