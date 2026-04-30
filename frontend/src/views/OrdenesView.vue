<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOrdenesStore } from '@/stores/ordenes'
import { useClientesStore } from '@/stores/clientes'
import { useMotoStore } from '@/stores/moto'
import { useServiciosStore } from '@/stores/servicios'
import { useInventarioStore } from '@/stores/inventario'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus, Search, Save } from 'lucide-vue-next'
import type { Orden } from '@/types'

const router = useRouter()
const ordenes = useOrdenesStore()
const clientes = useClientesStore()
const motocicletas = useMotoStore()
const servicios = useServiciosStore()
const inventarioStore = useInventarioStore()

const showModal = ref(false)
const showAddServicio = ref(false)
const viewingOrden = ref<Orden | null>(null)
const searchQuery = ref('')

const form = ref({
  id_moto: 0,
  id_cliente: 0,
  id_empleado: 0,
  kilometraje_ingreso: 0,
  observaciones: ''
})

const servicioForm = ref({
  id_servicio: 0,
  cantidad: 1
})

const productoForm = ref({
  id_producto: 0,
  cantidad: 1
})

onMounted(() => {
  ordenes.fetchAll()
  clientes.fetchAll()
  motocicletas.fetchAll()
  servicios.fetchAll()
  inventarioStore.fetchProductos()
})

function openCreate() {
  form.value = { id_moto: 0, id_cliente: 0, id_empleado: 0, kilometraje_ingreso: 0, observaciones: '' }
  showModal.value = true
}

async function save() {
  await ordenes.crear(form.value)
  showModal.value = false
  ordenes.fetchAll()
}

async function viewOrden(id: number) {
  const orden = await ordenes.obtener(id)
  viewingOrden.value = orden
  showAddServicio.value = true
}

async function addServicio() {
  if (!viewingOrden.value || !servicioForm.value.id_servicio) return
  await ordenes.agregarProducto(viewingOrden.value.id_orden, servicioForm.value.id_servicio, servicioForm.value.cantidad)
  await refreshOrden()
  servicioForm.value = { id_servicio: 0, cantidad: 1 }
}

async function addProducto() {
  if (!viewingOrden.value || !productoForm.value.id_producto) return
  const prod = inventarioStore.productos.find(p => p.id_producto === productoForm.value.id_producto)
  if (prod) {
    await ordenes.agregarProducto(viewingOrden.value.id_orden, null, productoForm.value.cantidad, prod.id_producto, prod.precio_venta)
    await refreshOrden()
    productoForm.value = { id_producto: 0, cantidad: 1 }
  }
}

async function refreshOrden() {
  if (!viewingOrden.value) return
  const updated = await ordenes.obtener(viewingOrden.value.id_orden)
  viewingOrden.value = updated
}

async function entregar(id: number) {
  if (confirm('¿Marcar como entregado?')) {
    await ordenes.entregar(id)
  }
}

function getStatusClass(estado: string) {
  const classes: Record<string, string> = {
    'Pendiente': 'badge-warning',
    'En Proceso': 'badge-info',
    'Completado': 'badge-success',
    'Entregado': 'bg-gray-100 text-gray-800',
    'Cancelado': 'badge-danger'
  }
  return classes[estado] || 'bg-gray-100'
}

function formatCurrency(value: number | undefined) {
  if (!value) return '$0'
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value)
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Órdenes de Trabajo</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Nueva Orden
      </button>
    </div>
    
    <LoadingSpinner v-if="ordenes.loading" />
    
    <div v-else class="card">
      <div class="mb-4">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input v-model="searchQuery" type="text" class="input pl-10" placeholder="Buscar orden..." />
        </div>
      </div>
      
      <table class="w-full">
        <thead>
          <tr class="table-header">
            <th class="table-cell">#</th>
            <th class="table-cell">Fecha</th>
            <th class="table-cell">Cliente</th>
            <th class="table-cell">Vehículo</th>
            <th class="table-cell">Estado</th>
            <th class="table-cell">Total</th>
            <th class="table-cell">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="orden in ordenes.ordenes" :key="orden.id_orden" class="border-b hover:bg-gray-50">
            <td class="table-cell font-medium">{{ orden.numero_orden }}</td>
            <td class="table-cell">{{ new Date(orden.fecha_ingreso).toLocaleDateString() }}</td>
            <td class="table-cell">{{ orden.cliente }}</td>
            <td class="table-cell">{{ orden.placa }}</td>
            <td class="table-cell">
              <span class="badge" :class="getStatusClass(orden.estado)">{{ orden.estado }}</span>
            </td>
            <td class="table-cell">{{ formatCurrency(orden.total) }}</td>
            <td class="table-cell">
              <TableActions 
                :actions="['view', 'complete']" 
                @view="viewOrden(orden.id_orden)"
                @complete="entregar(orden.id_orden)"
              />
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="ordenes.ordenes.length === 0" class="text-center py-8 text-gray-500">
        No hay órdenes registradas
      </div>
    </div>
    
    <Modal :open="showModal" title="Nueva Orden" @close="showModal = false">
      <form @submit.prevent="save" class="space-y-4">
        <div>
          <label class="label">Cliente *</label>
          <select v-model="form.id_cliente" class="input" required>
            <option value="0">Seleccionar cliente</option>
            <option v-for="c in clientes.clientes" :key="c.id_cliente" :value="c.id_cliente">
              {{ c.nombre }}
            </option>
          </select>
        </div>
        <div>
          <label class="label">Vehículo *</label>
<select v-model="form.id_moto" class="input" required>
            <option value="0">Seleccionar vehiculo</option>
            <option v-for="m in motocicletas.motocicletas" :key="m.id_moto" :value="m.id_moto">
              {{ m.placa }} - {{ m.cliente }}
            </option>
          </select>
        </div>
        <div>
          <label class="label">Kilometraje Ingreso</label>
          <input v-model.number="form.kilometraje_ingreso" type="number" class="input" />
        </div>
        <div>
          <label class="label">Observaciones</label>
          <textarea v-model="form.observaciones" class="input" rows="3"></textarea>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" class="btn btn-primary">Crear Orden</button>
        </div>
      </form>
    </Modal>
    
    <Modal :open="showAddServicio" :title="`Orden ${viewingOrden?.numero_orden}`" @close="showAddServicio = false" size="xl">
      <template v-if="viewingOrden">
        <div class="mb-4 flex justify-between items-start">
          <div class="space-y-1">
            <p><strong>Cliente:</strong> {{ viewingOrden.cliente }}</p>
            <p><strong>Vehiculo:</strong> {{ viewingOrden.placa }}</p>
            <p><strong>Fecha:</strong> {{ new Date(viewingOrden.fecha_ingreso).toLocaleDateString() }}</p>
            <p><strong>Estado:</strong> <span class="badge" :class="getStatusClass(viewingOrden.estado)">{{ viewingOrden.estado }}</span></p>
          </div>
          <button @click="refreshOrden" class="btn btn-secondary flex items-center gap-2">
            <Save class="w-4 h-4" /> Guardar
          </button>
        </div>
        
        <!-- Servicios -->
        <h4 class="font-semibold mb-2">Servicios / Mano de Obra</h4>
        <table class="w-full mb-4">
          <thead>
            <tr class="table-header">
              <th class="table-cell">Servicio</th>
              <th class="table-cell">Cant.</th>
              <th class="table-cell">Precio</th>
              <th class="table-cell">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in viewingOrden.servicios?.filter((x: any) => x.id_servicio)" :key="s.id_detalle" class="border-b">
              <td class="table-cell">{{ s.nombre }}</td>
              <td class="table-cell">{{ s.cantidad }}</td>
              <td class="table-cell">{{ formatCurrency(s.precio_unitario) }}</td>
              <td class="table-cell">{{ formatCurrency(s.subtotal) }}</td>
            </tr>
          </tbody>
        </table>
        
        <!-- Productos -->
        <h4 class="font-semibold mb-2">Productos / Repuestos</h4>
        <table class="w-full mb-4">
          <thead>
            <tr class="table-header">
              <th class="table-cell">Producto</th>
              <th class="table-cell">Cant.</th>
              <th class="table-cell">Precio</th>
              <th class="table-cell">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in viewingOrden.servicios?.filter((x: any) => x.id_producto)" :key="p.id_detalle" class="border-b">
              <td class="table-cell">{{ p.descripcion }}</td>
              <td class="table-cell">{{ p.cantidad }}</td>
              <td class="table-cell">{{ formatCurrency(p.precio_unitario) }}</td>
              <td class="table-cell">{{ formatCurrency(p.subtotal) }}</td>
            </tr>
            <tr v-if="!viewingOrden.servicios?.filter((x: any) => x.id_producto).length">
              <td colspan="4" class="text-center text-gray-400 py-2">No hay productos agregados</td>
            </tr>
          </tbody>
        </table>
        
        <div class="flex justify-between items-center p-4 bg-gray-50 rounded-lg mb-4">
          <span class="font-semibold">Total:</span>
          <span class="text-xl font-bold">{{ formatCurrency(viewingOrden.total) }}</span>
        </div>
        
        <!-- Agregar Servicio -->
        <form @submit.prevent="addServicio" class="mt-4 pt-4 border-t">
          <h4 class="font-semibold mb-2">Agregar Servicio</h4>
          <div class="flex gap-2">
            <select v-model="servicioForm.id_servicio" class="input flex-1">
              <option value="0">Seleccionar servicio</option>
              <option v-for="s in servicios.servicios" :key="s.id_servicio" :value="s.id_servicio">
                {{ s.nombre }} - {{ formatCurrency(s.precio) }}
              </option>
            </select>
            <input v-model.number="servicioForm.cantidad" type="number" class="input w-24" min="1" />
            <button type="submit" class="btn btn-primary">+</button>
          </div>
        </form>
        
        <!-- Agregar Producto -->
        <form @submit.prevent="addProducto" class="mt-4 pt-4 border-t">
          <h4 class="font-semibold mb-2">Agregar Repuesto</h4>
          <div class="flex gap-2">
            <select v-model="productoForm.id_producto" class="input flex-1">
              <option value="0">Seleccionar producto</option>
              <option v-for="p in inventarioStore.productos" :key="p.id_producto" :value="p.id_producto">
                {{ p.nombre }} - {{ formatCurrency(p.precio_venta) }} (Stock: {{ p.stock_actual }})
              </option>
            </select>
            <input v-model.number="productoForm.cantidad" type="number" class="input w-24" min="1" />
            <button type="submit" class="btn btn-primary">+</button>
          </div>
        </form>
      </template>
    </Modal>
  </div>
</template>