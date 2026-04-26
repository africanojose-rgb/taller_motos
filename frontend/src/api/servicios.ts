import client from './client'
import type { Servicio } from '@/types'

export const serviciosApi = {
  listar: () => client.get<Servicio[]>('/servicios'),
  obtener: (id: number) => client.get<Servicio>(`/servicios/${id}`),
  crear: (data: { nombre: string; descripcion?: string; precio: number; duracion_estimada?: number }) => 
    client.post<{ id_servicio: number }>('/servicios', data),
  actualizar: (id: number, data: Partial<Servicio>) => 
    client.put(`/servicios/${id}`, data),
  eliminar: (id: number) => 
    client.delete(`/servicios/${id}`)
}