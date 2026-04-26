import client from './client'
import type { Motocicleta } from '@/types'

export const motocicletasApi = {
  listar: () => client.get('/motocicletas'),
  obtener: (id) => client.get(`/motocicletas/${id}`),
  crear: (data) => client.post('/motocicletas', data),
  actualizar: (id, data) => client.put(`/motocicletas/${id}`, data),
  eliminar: (id) => client.delete(`/motocicletas/${id}`)
}