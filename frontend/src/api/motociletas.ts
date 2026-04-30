import client from './client'
import type { Motocicleta } from '@/types'

export const motocciletasApi = {
  listar: () => client.get<Motocicleta[]>('/motocicletas'),
  obtener: (id: number) => client.get<Motocicleta>(`/motocicletas/${id}`),
  crear: (data: any) => client.post('/motocicletas', data),
  actualizar: (id: number, data: any) => client.put(`/motocicletas/${id}`, data),
  eliminar: (id: number) => client.delete(`/motocicletas/${id}`)
}