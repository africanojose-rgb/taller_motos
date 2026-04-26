import client from './client'
import type { Factura } from '@/types'

export const facturasApi = {
  listar: () => client.get<Factura[]>('/facturas'),
  obtener: (id: number) => client.get<Factura>(`/facturas/${id}`),
  crear: (data: any) => client.post<{ id_factura: number; numero_factura: string }>('/facturas', data),
  eliminar: (id: number) => client.delete(`/facturas/${id}`),
  listarOrdenesDisponibles: () => client.get('/facturas/ordenes-disponibles'),
  obtenerDatosOrden: (id: number) => client.get(`/facturas/orden/${id}`),
  enviarEmail: (id: number, data: { email: string; asunto?: string }) => client.post(`/facturas/${id}/enviar`, data)
}