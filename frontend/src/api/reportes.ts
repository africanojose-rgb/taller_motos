import client from './client'
import type { ResumenGeneral, ServicioPopular, ClienteFrecuente, Ingresos } from '@/types'

export const reportesApi = {
  resumenGeneral: () => client.get<ResumenGeneral>('/reportes/resumen-general'),
  serviciosPopulares: () => client.get<ServicioPopular[]>('/reportes/servicios-populares'),
  clientesFrecuentes: () => client.get<ClienteFrecuente[]>('/reportes/clientes-frecuentes'),
  ingresosMensuales: () => client.get<{ mes: string; anio: string; ingresos: number; transacciones: number }[]>('/reportes/ingresos-mensuales'),
  estadoOrdenes: () => client.get<{ estado: string; cantidad: number }[]>('/reportes/estado-ordenes'),
  topMecanicos: () => client.get<{ nombre: string; ordenes_completadas: number; ingresos_generados: number }[]>('/reportes/top-mecanicos'),
  ingresos: (periodo?: string, fechaInicio?: string, fechaFin?: string) => 
    client.get<Ingresos>('/reportes/ingresos', { params: { periodo, fecha_inicio: fechaInicio, fecha_fin: fechaFin } })
}