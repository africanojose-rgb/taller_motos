import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import type { Factura } from '@/types'

export async function generarPDF(factura: Factura, config: Record<string, string>) {
  const doc = new jsPDF()
  
  // Colores
  const primaryColor = '#1a1a1a'
  const secondaryColor = '#666666'
  
  // Encabezado
  doc.setFontSize(20)
  doc.setTextColor(primaryColor)
  doc.text(config.nombre_taller || 'Taller de Motos', 14, 22)
  
  doc.setFontSize(10)
  doc.setTextColor(secondaryColor)
  doc.text(`NIT: ${config.nit || ''}`, 14, 30)
  doc.text(`${config.direccion || ''}`, 14, 35)
  doc.text(`${config.ciudad || ''} - Tel: ${config.telefono || ''}`, 14, 40)
  
  // Título factura
  doc.setFontSize(16)
  doc.setTextColor(primaryColor)
  doc.text('FACTURA DE VENTA', 140, 22, { align: 'right' })
  
  doc.setFontSize(10)
  doc.text(`No: ${factura.numero_factura}`, 140, 30, { align: 'right' })
  doc.text(`Fecha: ${new Date(factura.fecha_factura).toLocaleDateString('es-CO')}`, 140, 35, { align: 'right' })
  doc.text(`Estado: ${factura.estado}`, 140, 40, { align: 'right' })
  
  // Línea separadora
  doc.setDrawColor(200, 200, 200)
  doc.line(14, 45, 196, 45)
  
  // Datos del cliente
  doc.setFontSize(11)
  doc.setTextColor(primaryColor)
  doc.text('CLIENTE', 14, 55)
  
  doc.setFontSize(10)
  doc.setTextColor(secondaryColor)
  doc.text(`Nombre: ${factura.cliente}`, 14, 62)
  if (factura.documento) {
    doc.text(`Documento: ${factura.documento}`, 14, 68)
  }
  if (factura.direccion) {
    doc.text(`Dirección: ${factura.direccion}`, 14, 74)
  }
  if (factura.telefono) {
    doc.text(`Teléfono: ${factura.telefono}`, 14, 80)
  }
  
  // Servicios / Mano de Obra
  const servicios = factura.servicios || []
  if (servicios.length > 0) {
    const servicioData = servicios.map((s: any) => [
      s.descripcion || s.nombre || 'Servicio',
      s.cantidad?.toString() || '1',
      formatCurrency(s.precio_unitario || 0),
      formatCurrency(s.subtotal || 0)
    ])
    
    autoTable(doc, {
      startY: 90,
      head: [['SERVICIOS / MANO DE OBRA', 'Cant.', 'P. Unitario', 'Subtotal']],
      body: servicioData,
      theme: 'striped',
      headStyles: { fillColor: [52, 152, 219], textColor: 255 },
      columnStyles: {
        0: { cellWidth: 100 },
        1: { cellWidth: 20, halign: 'center' },
        2: { cellWidth: 30, halign: 'right' },
        3: { cellWidth: 30, halign: 'right' }
      }
    })
  }
  
  // Productos / Repuestos
  const productos = factura.productos || []
  if (productos.length > 0) {
    const productoData = productos.map((p: any) => [
      p.descripcion || 'Producto',
      p.cantidad?.toString() || '1',
      formatCurrency(p.precio_unitario || 0),
      formatCurrency(p.subtotal || 0)
    ])
    
    const currentY = (doc as any).lastAutoTable?.finalY ? (doc as any).lastAutoTable.finalY + 10 : 120
    
    autoTable(doc, {
      startY: currentY,
      head: [['REPUESTOS / PRODUCTOS', 'Cant.', 'P. Unitario', 'Subtotal']],
      body: productoData,
      theme: 'striped',
      headStyles: { fillColor: [231, 76, 60], textColor: 255 },
      columnStyles: {
        0: { cellWidth: 100 },
        1: { cellWidth: 20, halign: 'center' },
        2: { cellWidth: 30, halign: 'right' },
        3: { cellWidth: 30, halign: 'right' }
      }
    })
  }
  
  // Totales
  const finalY = (doc as any).lastAutoTable?.finalY ? (doc as any).lastAutoTable.finalY + 15 : 150
  
  doc.setFontSize(10)
  doc.setTextColor(secondaryColor)
  doc.text('Subtotal:', 140, finalY, { align: 'right' })
  doc.setTextColor(primaryColor)
  doc.text(formatCurrency(factura.subtotal || 0), 196, finalY, { align: 'right' })
  
  const ivaPorcentaje = parseFloat(config.iva || '19')
  doc.setTextColor(secondaryColor)
  doc.text(`IVA (${ivaPorcentaje}%):`, 140, finalY + 6, { align: 'right' })
  doc.setTextColor(primaryColor)
  doc.text(formatCurrency(factura.iva || 0), 196, finalY + 6, { align: 'right' })
  
  if (factura.descuento && factura.descuento > 0) {
    doc.setTextColor(secondaryColor)
    doc.text('Descuento:', 140, finalY + 12, { align: 'right' })
    doc.setTextColor(46, 204, 113)
    doc.text(`-${formatCurrency(factura.descuento)}`, 196, finalY + 12, { align: 'right' })
  }
  
  doc.setFontSize(12)
  doc.setTextColor(primaryColor)
  doc.text('TOTAL:', 140, finalY + 20, { align: 'right' })
  doc.setFontSize(14)
  doc.text(formatCurrency(factura.total), 196, finalY + 20, { align: 'right' })
  
  // Método de pago
  if (factura.metodo_pago) {
    doc.setFontSize(10)
    doc.setTextColor(secondaryColor)
    doc.text(`Método de pago: ${factura.metodo_pago}`, 14, finalY + 35)
  }
  
  // Observaciones
  if (factura.observaciones) {
    doc.setTextColor(secondaryColor)
    doc.text(`Observaciones: ${factura.observaciones}`, 14, finalY + 42)
  }
  
  // Pie de página
  doc.setFontSize(8)
  doc.setTextColor(150, 150, 150)
  doc.text('Gracias por su preferencia', 105, 285, { align: 'center' })
  doc.text('Generado por Sistema de Gestión de Taller', 105, 290, { align: 'center' })
  
  return doc
}

export function descargarPDF(doc: jsPDF, numeroFactura: string) {
  doc.save(`Factura_${numeroFactura}.pdf`)
}

export function abrirImprimir(doc: jsPDF) {
  const pdfBlob = doc.output('blob')
  const pdfUrl = URL.createObjectURL(pdfBlob)
  const printWindow = window.open(pdfUrl, '_blank')
  if (printWindow) {
    printWindow.addEventListener('load', () => {
      printWindow.print()
    })
  }
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0
  }).format(value)
}