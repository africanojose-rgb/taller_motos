import client from './client'

export const authApi = {
  login: (usuario: string, contrasena: string) => 
    client.post('/auth/login', { usuario, contrasena }),
  registro: (payload: { usuario: string; contrasena: string; nombre: string; email?: string; rol?: string }) => 
    client.post('/auth/registro', payload)
}