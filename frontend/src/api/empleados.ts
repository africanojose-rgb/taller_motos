import client from './client'
import type { Empleado } from '@/types'

export const empleadosApi = {
  listar: () => client.get<Empleado[]>('/empleados'),
  obtener: (id: number) => client.get<Empleado>(`/empleados/${id}`),
  crear: (data: { documento: string; nombre: string; telefono?: string; email?: string; cargo: string; fecha_contrato?: string }) => 
    client.post<{ id_empleado: number }>('/empleados', data),
  actualizar: (id: number, data: Partial<Empleado>) => 
    client.put(`/empleados/${id}`, data),
  eliminar: (id: number) => 
    client.delete(`/empleados/${id}`)
}