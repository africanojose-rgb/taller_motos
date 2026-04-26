import { defineStore } from 'pinia'
import { ref } from 'vue'
import { reportesApi } from '@/api/reportes'
import type { ResumenGeneral, ServicioPopular, ClienteFrecuente, Ingresos } from '@/types'

export const useReportesStore = defineStore('reportes', () => {
  const resumen = ref<ResumenGeneral | null>(null)
  const serviciosPopulares = ref<ServicioPopular[]>([])
  const clientesFrecuentes = ref<ClienteFrecuente[]>([])
  const ingresos = ref<Ingresos | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchResumen() {
    loading.value = true
    try {
      const { data } = await reportesApi.resumenGeneral()
      resumen.value = data
    } catch (e) {
      error.value = 'Error cargando resumen'
    } finally {
      loading.value = false
    }
  }

  async function fetchServiciosPopulares() {
    const { data } = await reportesApi.serviciosPopulares()
    serviciosPopulares.value = data
  }

  async function fetchClientesFrecuentes() {
    const { data } = await reportesApi.clientesFrecuentes()
    clientesFrecuentes.value = data
  }

  async function fetchIngresos(periodo?: string, fechaInicio?: string, fechaFin?: string) {
    try {
      const { data } = await reportesApi.ingresos(periodo, fechaInicio, fechaFin)
      ingresos.value = data
    } catch (e) {
      error.value = 'Error cargando ingresos'
    }
  }

  return { resumen, serviciosPopulares, clientesFrecuentes, ingresos, loading, error, fetchResumen, fetchServiciosPopulares, fetchClientesFrecuentes, fetchIngresos }
})