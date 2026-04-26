import client from './client'
import type { Cliente } from '@/types'

export const clientesApi = {
  listar: () => client.get<Cliente[]>('/clientes'),
  obtener: (id: number) => client.get<Cliente>(`/clientes/${id}`),
  crear: (data: Omit<Cliente, 'id_cliente' | 'estado' | 'fecha_registro'>) => 
    client.post<{ id_cliente: number }>('/clientes', data),
  actualizar: (id: number, data: Partial<Cliente>) => 
    client.put(`/clientes/${id}`, data),
  eliminar: (id: number) => 
    client.delete(`/clientes/${id}`)
}