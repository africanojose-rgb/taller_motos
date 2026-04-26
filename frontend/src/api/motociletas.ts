import client from './client'
import type { Motocicleta } from '@/types'

export const motociletasApi = {
  listar: () => client.get<Motocicleta[]>('/motociletas'),
  obtener: (id: number) => client.get<Motocicleta>(`/motociletas/${id}`),
  crear: (data: any) => client.post('/motociletas', data),
  actualizar: (id: number, data: any) => client.put(`/motociletas/${id}`, data),
  eliminar: (id: number) => client.delete(`/motociletas/${id}`)
}