import client from './client'
import type { Cita } from '@/types'

export const citasApi = {
  listar: () => client.get<Cita[]>('/citas'),
  obtener: (id: number) => client.get<Cita>(`/citas/${id}`),
  crear: (data: { id_cliente: number; id_vehiculo: number; fecha_cita: string; hora_cita: string; servicio?: string; observaciones?: string }) => 
    client.post<{ id_cita: number }>('/citas', data),
  actualizar: (id: number, data: Partial<Cita>) => 
    client.put(`/citas/${id}`, data),
  eliminar: (id: number) => 
    client.delete(`/citas/${id}`)
}