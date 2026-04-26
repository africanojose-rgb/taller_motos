import { defineStore } from 'pinia'
import { ref } from 'vue'
import { configApi } from '@/api/config'

export const useConfigStore = defineStore('config', () => {
  const config = ref<Record<string, string>>({})
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await configApi.listar()
      data.forEach((item: any) => {
        config.value[item.clave] = item.valor
      })
    } finally {
      loading.value = false
    }
  }

  async function fetchDict() {
    const { data } = await configApi.listarDict()
    config.value = data
  }

  async function guardar(clave: string, valor: string, descripcion?: string) {
    await configApi.guardar({ clave, valor, descripcion })
    config.value[clave] = valor
  }

  async function guardarBulk(items: Array<{ clave: string; valor: string }>) {
    await configApi.guardarBulk(items)
    items.forEach(item => {
      config.value[item.clave] = item.valor
    })
  }

  return { config, loading, fetchAll, fetchDict, guardar, guardarBulk }
})