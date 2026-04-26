import client from './client'
import type { Pago } from '@/types'

export const pagosApi = {
  listar: () => client.get<Pago[]>('/pagos'),
  pagosPorOrden: (idOrden: number) => client.get<Pago[]>(`/pagos/orden/${idOrden}`),
  registrar: (data: { id_orden: number; monto: number; metodo_pago?: string; numero_referencia?: string; observaciones?: string }) => 
    client.post<{ id_pago: number }>('/pagos', data),
  eliminar: (id: number) => 
    client.delete(`/pagos/${id}`)
}