import client from './client'

export const configApi = {
  listar: () => client.get('/config'),
  listarDict: () => client.get<Record<string, string>>('/config/dict'),
  obtener: (clave: string) => client.get(`/config/${clave}`),
  guardar: (data: { clave: string; valor: string; descripcion?: string }) => client.post('/config', data),
  guardarBulk: (data: { clave: string; valor: string }[]) => client.post('/config/bulk', data)
}