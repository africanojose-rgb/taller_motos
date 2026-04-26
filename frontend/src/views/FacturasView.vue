<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useFacturasStore } from '@/stores/facturas'
import { useClientesStore } from '@/stores/clientes'
import { useInventarioStore } from '@/stores/inventario'
import { useEmpleadosStore } from '@/stores/empleados'
import { useServiciosStore } from '@/stores/servicios'
import { useConfigStore } from '@/stores/config'
import { facturasApi } from '@/api/facturas'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus, Eye, Download, Printer, Mail, X } from 'lucide-vue-next'
import type { Factura } from '@/types'
import { generarPDF, descargarPDF, abrirImprimir } from '@/utils/facturaPDF'

const store = useFacturasStore()
const clientesStore = useClientesStore()
const inventarioStore = useInventarioStore()
const empleadosStore = useEmpleadosStore()
const serviciosStore = useServiciosStore()
const configStore = useConfigStore()

const showModal = ref(false)
const verDetalleModal = ref(false)
const enviandoEmail = ref(false)
const ordenesDisponibles = ref<any[]>([])
const selectedOrden = ref<number | null>(null)
const ordenData = ref<any>(null)
const viewingFactura = ref<Factura | null>(null)
const emailDestino = ref('')

const form = ref({
  id_cliente: null as number | null,
  id_orden: null as number | null,
  id_empleado: null as number | null,
  subtotal: 0,
  descuento: 0,
  iva: 0,
  total: 0,
  metodo_pago: 'Efectivo',
  observaciones: ''
})

const serviciosDetalle = ref<any[]>([])
const productosDetalle = ref<any[]>([])

onMounted(async () => {
  store.fetchAll()
  clientesStore.fetchAll()
  inventarioStore.fetchProductos()
  empleadosStore.fetchAll()
  serviciosStore.fetchAll()
  configStore.fetchDict()
})

async function verFactura(factura: Factura) {
  try {
    const { data } = await facturasApi.obtener(factura.id_factura)
    viewingFactura.value = data
    emailDestino.value = data.email || ''
    verDetalleModal.value = true
  } catch (e) {
    console.error('Error cargando factura:', e)
  }
}

async function descargarFacturaPDF() {
  if (!viewingFactura.value) return
  const doc = await generarPDF(viewingFactura.value, configStore.config)
  descargarPDF(doc, viewingFactura.value.numero_factura)
}

function imprimirFactura() {
  if (!viewingFactura.value) return
  generarPDF(viewingFactura.value, configStore.config).then(doc => {
    abrirImprimir(doc)
  })
}

async function enviarEmail() {
  if (!viewingFactura.value || !emailDestino.value) return
  if (!confirm(`Enviar factura a ${emailDestino.value}?`)) return
  
  enviandoEmail.value = true
  try {
    await facturasApi.enviarEmail(viewingFactura.value.id_factura, {
      email: emailDestino.value,
      asunto: `Factura ${viewingFactura.value.numero_factura}`
    })
    alert('Factura enviada correctamente')
    verDetalleModal.value = false
  } catch (e) {
    console.error('Error enviando email:', e)
    alert('Error al enviar email')
  } finally {
    enviandoEmail.value = false
  }
}

async function loadOrdenesDisponibles() {
  try {
    const { data } = await facturasApi.listarOrdenesDisponibles()
    ordenesDisponibles.value = data
  } catch (e) {
    console.error('Error cargando órdenes:', e)
  }
}

async function onOrdenChange() {
  if (!selectedOrden.value) {
    ordenData.value = null
    serviciosDetalle.value = []
    productosDetalle.value = []
    return
  }
  
  try {
    const { data } = await facturasApi.obtenerDatosOrden(selectedOrden.value)
    ordenData.value = data.orden
    form.value.id_cliente = data.orden.id_cliente
    form.value.id_empleado = data.orden.id_empleado
    
    // Cargar servicios de la orden
    serviciosDetalle.value = data.servicios.map((s: any) => ({
      id_servicio: s.id_servicio,
      descripcion: s.servicio_nombre,
      cantidad: s.cantidad,
      precio_unitario: s.precio_servicio,
      subtotal: s.subtotal
    }))
    
    // Cargar productos de la orden
    productosDetalle.value = data.productos.map((p: any) => ({
      id_producto: p.id_producto,
      descripcion: p.producto_nombre,
      cantidad: p.cantidad,
      precio_unitario: p.precio_venta,
      subtotal: p.cantidad * p.precio_venta
    }))
    
    calcularTotal()
  } catch (e) {
    console.error('Error cargando datos de orden:', e)
  }
}

function addServicio() {
  serviciosDetalle.value.push({
    id_servicio: null,
    descripcion: '',
    cantidad: 1,
    precio_unitario: 0,
    subtotal: 0
  })
}

function addProducto() {
  productosDetalle.value.push({
    id_producto: null,
    descripcion: '',
    cantidad: 1,
    precio_unitario: 0,
    subtotal: 0
  })
}

function removeServicio(index: number) {
  serviciosDetalle.value.splice(index, 1)
  calcularTotal()
}

function removeProducto(index: number) {
  productosDetalle.value.splice(index, 1)
  calcularTotal()
}

function onServicioChange(index: number) {
  const item = serviciosDetalle.value[index]
  if (item.id_servicio) {
    const svc = serviciosStore.servicios.find(s => s.id_servicio === item.id_servicio)
    if (svc) {
      item.descripcion = svc.nombre
      item.precio_unitario = svc.precio
      item.subtotal = item.cantidad * svc.precio
    }
  }
  calcularTotal()
}

function onProductoChange(index: number) {
  const item = productosDetalle.value[index]
  if (item.id_producto) {
    const prod = inventarioStore.productos.find(p => p.id_producto === item.id_producto)
    if (prod) {
      item.descripcion = prod.nombre
      item.precio_unitario = prod.precio_venta
      item.subtotal = item.cantidad * prod.precio_venta
    }
  }
  calcularTotal()
}

function calcularTotal() {
  const serviciosTotal = serviciosDetalle.value.reduce((sum, item) => sum + (item.subtotal || 0), 0)
  const productosTotal = productosDetalle.value.reduce((sum, item) => sum + (item.subtotal || 0), 0)
  
  form.value.subtotal = serviciosTotal + productosTotal
  form.value.iva = Math.round(Number(form.value.subtotal) * 0.19)
  form.value.total = Number(form.value.subtotal) - Number(form.value.descuento) + Number(form.value.iva)
}

async function save() {
  try {
    const detalle = [
      ...serviciosDetalle.value.filter(s => s.id_servicio).map(s => ({
        id_servicio: s.id_servicio,
        descripcion: s.descripcion,
        cantidad: s.cantidad,
        precio_unitario: s.precio_unitario,
        subtotal: s.subtotal
      })),
      ...productosDetalle.value.filter(p => p.id_producto).map(p => ({
        id_producto: p.id_producto,
        descripcion: p.descripcion,
        cantidad: p.cantidad,
        precio_unitario: p.precio_unitario,
        subtotal: p.subtotal
      }))
    ]
    
    console.log('Enviando factura:', { ...form.value, detalle })
    
    await store.crear({
      ...form.value,
      id_orden: selectedOrden.value,
      detalle
    })
    
    showModal.value = false
    store.fetchAll()
  } catch (e: any) {
    console.error('Error al crear factura:', e)
    alert('Error al crear factura: ' + (e.response?.data?.error || e.message))
  }
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value)
}

function openCreate() {
  selectedOrden.value = null
  ordenData.value = null
  serviciosDetalle.value = []
  productosDetalle.value = []
  form.value = {
    id_cliente: null,
    id_orden: null,
    id_empleado: null,
    subtotal: 0,
    descuento: 0,
    iva: 0,
    total: 0,
    metodo_pago: 'Efectivo',
    observaciones: ''
  }
  loadOrdenesDisponibles()
  showModal.value = true
}

const manoObraTotal = computed(() => {
  return serviciosDetalle.value.reduce((sum, item) => sum + (item.subtotal || 0), 0)
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Facturas</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Nueva Factura
      </button>
    </div>
    
    <LoadingSpinner v-if="store.loading" />
    
    <div v-else class="card">
      <table class="w-full">
        <thead>
          <tr class="table-header">
            <th class="table-cell">Numero</th>
            <th class="table-cell">Fecha</th>
            <th class="table-cell">Cliente</th>
            <th class="table-cell">Mano Obra</th>
            <th class="table-cell">Total</th>
            <th class="table-cell">Estado</th>
            <th class="table-cell">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="factura in store.facturas" :key="factura.id_factura" class="border-b hover:bg-gray-50">
            <td class="table-cell font-mono">{{ factura.numero_factura }}</td>
            <td class="table-cell">{{ new Date(factura.fecha_factura).toLocaleDateString() }}</td>
            <td class="table-cell">{{ factura.cliente }}</td>
            <td class="table-cell">{{ formatCurrency(factura.mano_obra || 0) }}</td>
            <td class="table-cell font-medium">{{ formatCurrency(factura.total) }}</td>
            <td class="table-cell">
              <span class="badge" :class="factura.estado === 'Pagada' ? 'badge-success' : 'badge-warning'">
                {{ factura.estado }}
              </span>
            </td>
            <td class="table-cell">
              <div class="flex gap-1">
                <button @click="verFactura(factura)" class="btn-icon" title="Ver">
                  <Eye class="w-4 h-4" />
                </button>
                <button @click="verFactura(factura); descargarFacturaPDF()" class="btn-icon" title="PDF">
                  <Download class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="store.facturas.length === 0" class="text-center py-8 text-gray-500">
        No hay facturas registradas
      </div>
    </div>
    
    <Modal :open="showModal" title="Nueva Factura" @close="showModal = false" :size="'3xl'">
      <form @submit.prevent="save" class="space-y-4">
        <!-- Selector de Orden -->
        <div>
          <label class="label">Orden de Trabajo (opcional)</label>
          <select v-model="selectedOrden" @change="onOrdenChange" class="input">
            <option :value="null">Sin orden - Crear factura manual</option>
            <option v-for="o in ordenesDisponibles" :key="o.id_orden" :value="o.id_orden">
              {{ o.numero_orden }} - {{ o.cliente }} ({{ o.placa }}) - {{ formatCurrency(o.mano_obra || 0) }}
            </option>
          </select>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Cliente *</label>
            <select v-model="form.id_cliente" class="input" required>
              <option :value="null">Seleccionar cliente</option>
              <option v-for="c in clientesStore.clientes" :key="c.id_cliente" :value="c.id_cliente">
                {{ c.nombre }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Empleado (Responsable) *</label>
            <select v-model="form.id_empleado" class="input" required>
              <option :value="null">Seleccionar empleado</option>
              <option v-for="e in empleadosStore.empleados" :key="e.id_empleado" :value="e.id_empleado">
                {{ e.nombre }} - {{ e.cargo }}
              </option>
            </select>
          </div>
        </div>
        
        <!-- Servicios -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="label">Servicios / Mano de Obra</label>
            <button type="button" @click="addServicio" class="text-secondary text-sm">+ Agregar Servicio</button>
          </div>
          <table v-if="serviciosDetalle.length > 0" class="w-full text-sm">
            <thead>
              <tr class="table-header">
                <th>Servicio</th>
                <th>Cant.</th>
                <th>P. Unit.</th>
                <th>Subtotal</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in serviciosDetalle" :key="'svc-'+index" class="border-b">
                <td class="p-1">
                  <select v-model="item.id_servicio" @change="onServicioChange(index)" class="input text-sm py-1">
                    <option :value="null">Seleccionar</option>
                    <option v-for="s in serviciosStore.servicios" :key="s.id_servicio" :value="s.id_servicio">
                      {{ s.nombre }} - {{ formatCurrency(s.precio) }}
                    </option>
                  </select>
                </td>
                <td class="p-1"><input v-model.number="item.cantidad" type="number" min="1" class="input text-sm py-1 w-16" @input="() => { item.subtotal = item.cantidad * item.precio_unitario; calcularTotal() }" /></td>
                <td class="p-1">{{ formatCurrency(item.precio_unitario) }}</td>
                <td class="p-1 font-medium">{{ formatCurrency(item.subtotal) }}</td>
                <td class="p-1"><button type="button" @click="removeServicio(index)" class="text-red-500">X</button></td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-gray-400 text-sm italic">No hay servicios agregados</div>
        </div>
        
        <!-- Productos -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="label">Productos</label>
            <button type="button" @click="addProducto" class="text-secondary text-sm">+ Agregar Producto</button>
          </div>
          <table v-if="productosDetalle.length > 0" class="w-full text-sm">
            <thead>
              <tr class="table-header">
                <th>Producto</th>
                <th>Cant.</th>
                <th>P. Unit.</th>
                <th>Subtotal</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in productosDetalle" :key="'prod-'+index" class="border-b">
                <td class="p-1">
                  <select v-model="item.id_producto" @change="onProductoChange(index)" class="input text-sm py-1">
                    <option :value="null">Seleccionar</option>
                    <option v-for="p in inventarioStore.productos" :key="p.id_producto" :value="p.id_producto">
                      {{ p.nombre }}
                    </option>
                  </select>
                </td>
                <td class="p-1"><input v-model.number="item.cantidad" type="number" min="1" class="input text-sm py-1 w-16" @input="() => { item.subtotal = item.cantidad * item.precio_unitario; calcularTotal() }" /></td>
                <td class="p-1"><input v-model.number="item.precio_unitario" type="number" class="input text-sm py-1 w-24" @input="() => { item.subtotal = item.cantidad * item.precio_unitario; calcularTotal() }" /></td>
                <td class="p-1 font-medium">{{ formatCurrency(item.subtotal) }}</td>
                <td class="p-1"><button type="button" @click="removeProducto(index)" class="text-red-500">X</button></td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Descuento</label>
            <input v-model.number="form.descuento" type="number" class="input" @input="calcularTotal" />
          </div>
          <div>
            <label class="label">Metodo de Pago</label>
            <select v-model="form.metodo_pago" class="input">
              <option>Efectivo</option>
              <option>Tarjeta</option>
              <option>Transferencia</option>
              <option>Consignacion</option>
            </select>
          </div>
        </div>
        
        <div class="bg-gray-50 p-4 rounded-lg space-y-2">
          <div class="flex justify-between">
            <span>Mano de Obra (Servicios):</span>
            <span class="font-medium">{{ formatCurrency(manoObraTotal) }}</span>
          </div>
          <div class="flex justify-between">
            <span>Subtotal:</span>
            <span>{{ formatCurrency(form.subtotal) }}</span>
          </div>
          <div class="flex justify-between">
            <span>IVA (19%):</span>
            <span>{{ formatCurrency(form.iva) }}</span>
          </div>
          <div class="flex justify-between">
            <span>Descuento:</span>
            <span>-{{ formatCurrency(form.descuento) }}</span>
          </div>
          <div class="flex justify-between font-bold text-lg border-t pt-2">
            <span>Total:</span>
            <span>{{ formatCurrency(form.total) }}</span>
          </div>
        </div>
        
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" class="btn btn-primary">Crear Factura</button>
        </div>
      </form>
    </Modal>
    
    <Modal :open="verDetalleModal" :title="`Factura ${viewingFactura?.numero_factura}`" @close="verDetalleModal = false" size="lg">
      <template v-if="viewingFactura">
        <div class="space-y-4">
          <div class="flex justify-between items-start">
            <div class="space-y-1">
              <p><strong>Cliente:</strong> {{ viewingFactura.cliente }}</p>
              <p><strong>Documento:</strong> {{ viewingFactura.documento || '-' }}</p>
              <p><strong>Fecha:</strong> {{ new Date(viewingFactura.fecha_factura).toLocaleDateString() }}</p>
              <p><strong>Estado:</strong> <span class="badge" :class="viewingFactura.estado === 'Pagada' ? 'badge-success' : 'badge-warning'">{{ viewingFactura.estado }}</span></p>
            </div>
            <div class="flex gap-2">
              <button @click="descargarFacturaPDF" class="btn btn-primary flex items-center gap-2">
                <Download class="w-4 h-4" /> PDF
              </button>
              <button @click="imprimirFactura" class="btn btn-secondary flex items-center gap-2">
                <Printer class="w-4 h-4" /> Imprimir
              </button>
            </div>
          </div>
          
          <!-- Servicios -->
          <div v-if="viewingFactura.servicios?.length">
            <h4 class="font-semibold mb-2">Servicios / Mano de Obra</h4>
            <table class="w-full text-sm">
              <thead>
                <tr class="table-header">
                  <th class="table-cell">Descripción</th>
                  <th class="table-cell">Cant.</th>
                  <th class="table-cell">P. Unitario</th>
                  <th class="table-cell">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in viewingFactura.servicios" :key="s.id_detalle" class="border-b">
                  <td class="table-cell">{{ s.descripcion || s.servicio }}</td>
                  <td class="table-cell">{{ s.cantidad }}</td>
                  <td class="table-cell">{{ formatCurrency(s.precio_unitario) }}</td>
                  <td class="table-cell font-medium">{{ formatCurrency(s.subtotal) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Productos -->
          <div v-if="viewingFactura.productos?.length">
            <h4 class="font-semibold mb-2">Repuestos / Productos</h4>
            <table class="w-full text-sm">
              <thead>
                <tr class="table-header">
                  <th class="table-cell">Descripción</th>
                  <th class="table-cell">Cant.</th>
                  <th class="table-cell">P. Unitario</th>
                  <th class="table-cell">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in viewingFactura.productos" :key="p.id_detalle" class="border-b">
                  <td class="table-cell">{{ p.descripcion || p.producto }}</td>
                  <td class="table-cell">{{ p.cantidad }}</td>
                  <td class="table-cell">{{ formatCurrency(p.precio_unitario) }}</td>
                  <td class="table-cell font-medium">{{ formatCurrency(p.subtotal) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Totales -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="flex justify-between">
              <span>Subtotal:</span>
              <span>{{ formatCurrency(viewingFactura.subtotal) }}</span>
            </div>
            <div class="flex justify-between">
              <span>IVA:</span>
              <span>{{ formatCurrency(viewingFactura.iva) }}</span>
            </div>
            <div class="flex justify-between" v-if="viewingFactura.descuento > 0">
              <span>Descuento:</span>
              <span class="text-green-600">-{{ formatCurrency(viewingFactura.descuento) }}</span>
            </div>
            <div class="flex justify-between font-bold text-lg border-t pt-2">
              <span>Total:</span>
              <span>{{ formatCurrency(viewingFactura.total) }}</span>
            </div>
          </div>
          
          <!-- Enviar Email -->
          <div class="border-t pt-4">
            <h4 class="font-semibold mb-2">Enviar por Email</h4>
            <div class="flex gap-2">
              <input v-model="emailDestino" type="email" class="input flex-1" placeholder="correo@cliente.com" />
              <button @click="enviarEmail" class="btn btn-primary flex items-center gap-2" :disabled="enviandoEmail || !emailDestino">
                <Mail class="w-4 h-4" /> {{ enviandoEmail ? 'Enviando...' : 'Enviar' }}
              </button>
            </div>
          </div>
        </div>
      </template>
    </Modal>
  </div>
</template>