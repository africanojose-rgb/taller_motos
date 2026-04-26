import client from './client'

export const nominaApi = {
  listarComisiones: () => client.get('/nomina/empleados/comisiones'),
  comisionesEmpleado: (id) => client.get(`/nomina/empleados/${id}/comisiones`),
  crearComision: (id, data) => client.post(`/nomina/empleados/${id}/comisiones`, data),
  actualizarComision: (id, data) => client.put(`/nomina/comisiones/${id}`, data),
  eliminarComision: (id) => client.delete(`/nomina/comisiones/${id}`),
  calcularComisiones: (id, params) => client.get(`/nomina/empleados/${id}/calcular`, { params }),
  listarNominas: () => client.get('/nomina/periodos'),
  crearNomina: (id, data) => client.post(`/nomina/empleados/${id}/nominas`, data)
}