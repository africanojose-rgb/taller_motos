import client from './client'
import type { Vehiculo, Marca, Modelo } from '@/types'

export const vehiculosApi = {
  listar: () => client.get<Vehiculo[]>('/vehiculos'),
  obtener: (id: number) => client.get<Vehiculo>(`/vehiculos/${id}`),
  crear: (data: Omit<Vehiculo, 'id_vehiculo' | 'estado' | 'cliente' | 'modelo' | 'marca'>) => 
    client.post<{ id_vehiculo: number }>('/vehiculos', data),
  actualizar: (id: number, data: Partial<Vehiculo>) => 
    client.put(`/vehiculos/${id}`, data),
  eliminar: (id: number) => 
    client.delete(`/vehiculos/${id}`),
  listarMarcas: () => client.get<Marca[]>('/vehiculos/marcas'),
  listarModelos: (idMarca: number) => client.get<Modelo[]>(`/vehiculos/modelos/${idMarca}`)
}