import client from './client'
import type { Orden, DetalleOrden } from '@/types'

export const ordenesApi = {
  listar: () => client.get<Orden[]>('/ordenes'),
  obtener: (id: number) => client.get<Orden>(`/ordenes/${id}`),
  crear: (data: { id_moto: number; id_cliente: number; id_empleado?: number; kilometraje_ingreso?: number; observaciones?: string }) => 
    client.post<{ id_orden: number; numero_orden: string }>('/ordenes', data),
  actualizar: (id: number, data: { estado?: string; observaciones?: string; descuento?: number }) => 
    client.put(`/ordenes/${id}`, data),
  agregarDetalle: (idOrden: number, data: { id_servicio?: number; id_producto?: number; cantidad?: number; precio_unitario?: number }) => 
    client.post(`/ordenes/${idOrden}/servicios`, data),
  entregar: (id: number, kilometraje_salida?: number) => 
    client.post(`/ordenes/${id}/entregar`, { kilometraje_salida })
}