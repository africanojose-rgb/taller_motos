export interface Usuario {
  id_usuario: number
  usuario: string
  nombre: string
  email?: string
  rol: string
  token?: string
}

export interface Cliente {
  id_cliente: number
  nombre: string
  documento: string
  tipo_documento: string
  telefono?: string
  email?: string
  direccion?: string
  ciudad?: string
  estado: number
  fecha_registro: string
}

export interface Motocicleta {
  id_moto: number
  id_cliente: number
  id_marca: number
  id_modelo: number
  placa: string
  color?: string
  kilometraje?: number
  vin?: string
  num_serie?: string
  anio?: number
  estado: number
  cliente?: string
  modelo?: string
  marca?: string
}

export interface Marca {
  id_marca: number
  nombre: string
  logo?: string
  estado: number
}

export interface Modelo {
  id_modelo: number
  id_marca: number
  nombre: string
  cilindrada?: number
  anio_inicio?: number
  anio_fin?: number
  estado: number
}

export interface Empleado {
  id_empleado: number
  documento: string
  nombre: string
  telefono?: string
  email?: string
  cargo: string
  fecha_contrato?: string
  estado: number
  salario_base?: number
}

export interface Servicio {
  id_servicio: number
  nombre: string
  descripcion?: string
  precio: number
  duracion_estimada?: number
  estado: number
}

export interface Orden {
  id_orden: number
  id_moto: number
  id_cliente: number
  id_empleado?: number
  numero_orden: string
  fecha_ingreso: string
  fecha_entrega_estimada?: string
  fecha_entrega?: string
  kilometraje_ingreso?: number
  kilometraje_salida?: number
  estado: string
  observaciones?: string
  subtotal?: number
  descuento?: number
  total?: number
  estado_pago: number
  placa?: string
  cliente?: string
  mecanico?: string
  servicios?: DetalleOrden[]
}

export interface DetalleOrden {
  id_detalle: number
  id_orden: number
  id_servicio?: number
  id_producto?: number
  cantidad: number
  precio_unitario: number
  subtotal: number
  nombre?: string
  descripcion?: string
}

export interface Cita {
  id_cita: number
  id_cliente: number
  id_moto: number
  fecha_cita: string
  hora_cita: string
  servicio?: string
  observaciones?: string
  estado: string
  cliente?: string
  vehiculo?: string
}

export interface Pago {
  id_pago: number
  id_orden: number
  monto: number
  metodo_pago?: string
  numero_referencia?: string
  observaciones?: string
  fecha_pago: string
  numero_orden?: string
  cliente?: string
}

export interface Categoria {
  id_categoria: number
  nombre: string
  descripcion?: string
  estado: number
}

export interface Producto {
  id_producto: number
  id_categoria: number | null
  codigo: string
  nombre: string
  descripcion?: string
  marca?: string
  presentacion?: string
  stock_actual: number
  stock_minimo: number
  precio_compra: number
  precio_venta: number
  margen_ganancia?: number
  estado: number
  categoria?: string
}

export interface Factura {
  id_factura: number
  numero_factura: string
  id_cliente: number
  id_empleado?: number
  fecha_factura: string
  mano_obra: number
  subtotal: number
  descuento: number
  iva: number
  total: number
  metodo_pago?: string
  estado: string
  observaciones?: string
  cliente?: string
  documento?: string
  direccion?: string
  telefono?: string
  email?: string
  servicios?: any[]
  productos?: any[]
  empleado?: string
  empleado_cargo?: string
}

export interface ResumenGeneral {
  total_clientes: number
  total_vehiculos: number
  total_ordenes: number
  ordenes_activas: number
  inversion_inventario: number
}

export interface ServicioPopular {
  nombre: string
  cantidad: number
  ingresos: number
}

export interface ClienteFrecuente {
  nombre: string
  vehiculos: number
  ordenes: number
  total_gastado: number
}

export interface Ingresos {
  mano_obra: number
  repuestos: number
  total: number
}