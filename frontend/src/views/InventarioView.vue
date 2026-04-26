<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useInventarioStore } from '@/stores/inventario'
import Modal from '@/components/Modal.vue'
import TableActions from '@/components/TableActions.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { Plus, Search, AlertTriangle } from 'lucide-vue-next'
import type { Producto } from '@/types'

const store = useInventarioStore()
const showModal = ref(false)
const showMovimiento = ref(false)
const editingProducto = ref<Producto | null>(null)
const searchQuery = ref('')
const selectedCategoria = ref<number | null>(null)

const form = ref({
  id_categoria: null as number | null,
  codigo: '',
  nombre: '',
  descripcion: '',
  marca: '',
  presentacion: '',
  stock_actual: 0,
  stock_minimo: 5,
  precio_compra: 0,
  precio_venta: 0
})

const movimiento = ref({
  id_producto: null as number | null,
  tipo_movimiento: 'entrada',
  cantidad: 1,
  precio_unitario: 0,
  observaciones: ''
})

onMounted(() => {
  store.fetchProductos()
  store.fetchCategorias()
})

function openCreate() {
  editingProducto.value = null
  form.value = {
    id_categoria: null, codigo: '', nombre: '', descripcion: '',
    marca: '', presentacion: '', stock_actual: 0, stock_minimo: 5,
    precio_compra: 0, precio_venta: 0
  }
  showModal.value = true
}

function openEdit(producto: Producto) {
  editingProducto.value = producto
  form.value = { ...producto }
  showModal.value = true
}

function openMovimiento(producto: Producto) {
  editingProducto.value = producto
  movimiento.value = {
    id_producto: producto.id_producto,
    tipo_movimiento: 'entrada',
    cantidad: 1,
    precio_unitario: producto.precio_compra,
    observaciones: ''
  }
  showMovimiento.value = true
}

async function save() {
  if (editingProducto.value) {
    await store.actualizarProducto(editingProducto.value.id_producto, form.value)
  } else {
    await store.crearProducto(form.value)
  }
  showModal.value = false
}

async function saveMovimiento() {
  await store.registrarMovimiento(movimiento.value)
  showMovimiento.value = false
  store.fetchProductos()
}

async function remove(id: number) {
  if (confirm('¿Eliminar este producto?')) {
    await store.eliminarProducto(id)
  }
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value)
}

const filteredProductos = computed(() => {
  let result = store.productos
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p => 
      p.nombre.toLowerCase().includes(q) || 
      p.codigo?.toLowerCase().includes(q)
    )
  }
  if (selectedCategoria.value) {
    result = result.filter(p => p.id_categoria === selectedCategoria.value)
  }
  return result
})

const stockBajo = computed(() => store.productos.filter(p => p.stock_actual <= p.stock_minimo))
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Inventario</h1>
      <button @click="openCreate" class="btn btn-primary flex items-center gap-2">
        <Plus class="w-5 h-5" />
        Nuevo Producto
      </button>
    </div>
    
    <div v-if="stockBajo.length > 0" class="card mb-6 border-l-4 border-l-warning">
      <div class="flex items-center gap-2 text-yellow-800">
        <AlertTriangle class="w-5 h-5" />
        <span class="font-medium">Stock bajo: {{ stockBajo.length }} productos</span>
      </div>
    </div>
    
    <LoadingSpinner v-if="store.loading" />
    
    <div v-else class="card">
      <div class="flex gap-4 mb-4">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input v-model="searchQuery" type="text" class="input pl-10" placeholder="Buscar producto..." />
        </div>
        <select v-model="selectedCategoria" class="input w-48">
          <option :value="null">Todas las categorías</option>
          <option v-for="cat in store.categorias" :key="cat.id_categoria" :value="cat.id_categoria">
            {{ cat.nombre }}
          </option>
        </select>
      </div>
      
      <table class="w-full">
        <thead>
          <tr class="table-header">
            <th class="table-cell">Código</th>
            <th class="table-cell">Producto</th>
            <th class="table-cell">Categoría</th>
            <th class="table-cell">Stock</th>
            <th class="table-cell">P. Compra</th>
            <th class="table-cell">P. Venta</th>
            <th class="table-cell">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="producto in filteredProductos" :key="producto.id_producto" 
              class="border-b hover:bg-gray-50"
              :class="{ 'bg-yellow-50': producto.stock_actual <= producto.stock_minimo }">
            <td class="table-cell font-mono text-sm">{{ producto.codigo }}</td>
            <td class="table-cell">
              <div>{{ producto.nombre }}</div>
              <div class="text-xs text-gray-500">{{ producto.marca || '' }}</div>
            </td>
            <td class="table-cell">{{ producto.categoria || '-' }}</td>
            <td class="table-cell">
              <span :class="producto.stock_actual <= producto.stock_minimo ? 'text-red-600 font-medium' : ''">
                {{ producto.stock_actual }}
              </span>
            </td>
            <td class="table-cell">{{ formatCurrency(producto.precio_compra) }}</td>
            <td class="table-cell">{{ formatCurrency(producto.precio_venta) }}</td>
            <td class="table-cell">
              <div class="flex gap-1">
                <button @click="openMovimiento(producto)" class="btn btn-secondary text-xs py-1 px-2">±</button>
                <TableActions :actions="['edit', 'delete']" @edit="openEdit(producto)" @delete="remove(producto.id_producto)" />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="store.productos.length === 0" class="text-center py-8 text-gray-500">
        No hay productos registrados
      </div>
    </div>
    
    <Modal :open="showModal" :title="editingProducto ? 'Editar Producto' : 'Nuevo Producto'" @close="showModal = false">
      <form @submit.prevent="save" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Código *</label>
            <input v-model="form.codigo" class="input uppercase" required />
          </div>
          <div>
            <label class="label">Categoría</label>
            <select v-model="form.id_categoria" class="input">
              <option :value="null">Sin categoría</option>
              <option v-for="cat in store.categorias" :key="cat.id_categoria" :value="cat.id_categoria">
                {{ cat.nombre }}
              </option>
            </select>
          </div>
        </div>
        <div>
          <label class="label">Nombre *</label>
          <input v-model="form.nombre" class="input" required />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Marca</label>
            <input v-model="form.marca" class="input" />
          </div>
          <div>
            <label class="label">Presentación</label>
            <input v-model="form.presentacion" class="input" placeholder="1 Litro, Pieza, etc." />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="label">Stock Actual</label>
            <input v-model.number="form.stock_actual" type="number" class="input" />
          </div>
          <div>
            <label class="label">Stock Mínimo</label>
            <input v-model.number="form.stock_minimo" type="number" class="input" />
          </div>
          <div>
            <label class="label">Margen %</label>
            <input :value="form.precio_compra > 0 ? Math.round((form.precio_venta - form.precio_compra) / form.precio_compra * 100) : 0" 
                   type="number" class="input bg-gray-100" readonly />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Precio Compra</label>
            <input v-model.number="form.precio_compra" type="number" class="input" />
          </div>
          <div>
            <label class="label">Precio Venta</label>
            <input v-model.number="form.precio_venta" type="number" class="input" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" class="btn btn-primary">Guardar</button>
        </div>
      </form>
    </Modal>
    
    <Modal :open="showMovimiento" title="Registrar Movimiento" @close="showMovimiento = false">
      <form @submit.prevent="saveMovimiento" class="space-y-4">
        <div>
          <label class="label">Producto</label>
          <input :value="editingProducto?.nombre" class="input bg-gray-100" readonly />
        </div>
        <div>
          <label class="label">Tipo de Movimiento</label>
          <select v-model="movimiento.tipo_movimiento" class="input">
            <option value="entrada">Entrada (Compra)</option>
            <option value="salida">Salida (Venta)</option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Cantidad</label>
            <input v-model.number="movimiento.cantidad" type="number" min="1" class="input" required />
          </div>
          <div>
            <label class="label">P. Unitario</label>
            <input v-model.number="movimiento.precio_unitario" type="number" class="input" />
          </div>
        </div>
        <div>
          <label class="label">Observaciones</label>
          <input v-model="movimiento.observaciones" class="input" />
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showMovimiento = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" class="btn btn-primary">Registrar</button>
        </div>
      </form>
    </Modal>
  </div>
</template>