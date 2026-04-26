from flask import Blueprint, request, jsonify
from db import get_all, get_one
from routes import require_auth

bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')


@bp.route('/servicios-populares', methods=['GET'])
@require_auth
def servicios_populares():
    try:
        servicios = get_all("""
            SELECT s.nombre, COUNT(d.id_detalle) AS cantidad, SUM(d.subtotal) AS ingresos
            FROM DetalleOrden d
            INNER JOIN Servicios s ON d.id_servicio = s.id_servicio
            GROUP BY s.id_servicio, s.nombre
            ORDER BY cantidad DESC
        """)
        return jsonify(servicios)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/clientes-frecuentes', methods=['GET'])
@require_auth
def clientes_frecuentes():
    try:
        clientes = get_all("""
            SELECT c.nombre, COUNT(DISTINCT m.id_moto) AS vehiculos, 
                   COUNT(DISTINCT o.id_orden) AS ordenes,
                   COALESCE(SUM(o.total), 0) AS total_gastado
            FROM Clientes c
            LEFT JOIN Motociletas m ON c.id_cliente = m.id_cliente
            LEFT JOIN OrdenesTrabajo o ON c.id_cliente = o.id_cliente
            WHERE c.estado = 1
            GROUP BY c.id_cliente, c.nombre
            ORDER BY ordenes DESC
            LIMIT 10
        """)
        return jsonify(clientes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ingresos-mensuales', methods=['GET'])
@require_auth
def ingresos_mensuales():
    try:
        ingresos = get_all("""
            SELECT strftime('%m', fecha_pago) AS mes, strftime('%Y', fecha_pago) AS anio, 
                   SUM(monto) AS ingresos, COUNT(*) AS transacciones
            FROM Pagos
            GROUP BY strftime('%m', fecha_pago), strftime('%Y', fecha_pago)
            ORDER BY anio DESC, mes DESC
        """)
        return jsonify(ingresos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/estado-ordenes', methods=['GET'])
@require_auth
def estado_ordenes():
    try:
        estados = get_all("""
            SELECT estado, COUNT(*) AS cantidad
            FROM OrdenesTrabajo
            GROUP BY estado
        """)
        return jsonify(estados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/resumen-general', methods=['GET'])
@require_auth
def resumen_general():
    try:
        total_clientes = get_one("SELECT COUNT(*) AS total FROM Clientes WHERE estado = 1")
        total_motociletas = get_one("SELECT COUNT(*) AS total FROM Motociletas WHERE estado = 1")
        total_ordenes = get_one("SELECT COUNT(*) AS total FROM OrdenesTrabajo")
        ordenes_activas = get_one("""
            SELECT COUNT(*) AS total FROM OrdenesTrabajo 
            WHERE estado IN ('Pendiente', 'En Proceso')
        """)
        inversion_inventario = get_one("""
            SELECT COALESCE(SUM(stock_actual * precio_compra), 0) AS total 
            FROM Productos WHERE estado = 1 AND stock_actual > 0
        """)
        
        return jsonify({
            'total_clientes': total_clientes['total'] if total_clientes else 0,
            'total_vehiculos': total_motociletas['total'] if total_motociletas else 0,
            'total_ordenes': total_ordenes['total'] if total_ordenes else 0,
            'ordenes_activas': ordenes_activas['total'] if ordenes_activas else 0,
            'inversion_inventario': inversion_inventario['total'] if inversion_inventario else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/top-mecanicos', methods=['GET'])
@require_auth
def top_mecanicos():
    try:
        mecanicos = get_all("""
            SELECT e.nombre, COUNT(o.id_orden) AS ordenes_completadas,
                   COALESCE(SUM(o.total), 0) AS total_gastado
            FROM Empleados e
            INNER JOIN OrdenesTrabajo o ON e.id_empleado = o.id_empleado
            WHERE o.estado = 'Completado'
            GROUP BY e.id_empleado, e.nombre
            ORDER BY ordenes_completadas DESC
        """)
        return jsonify(mecanicos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ingresos', methods=['GET'])
@require_auth
def ingresos():
    try:
        periodo = request.args.get('periodo', 'mes')
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            mano_obra = get_one("""
                SELECT COALESCE(SUM(df.subtotal), 0) AS total
                FROM DetalleFactura df
                INNER JOIN Facturas f ON df.id_factura = f.id_factura
                WHERE df.id_servicio IS NOT NULL
                AND DATE(f.fecha_factura) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            repuestos = get_one("""
                SELECT COALESCE(SUM(df.subtotal), 0) AS total
                FROM DetalleFactura df
                INNER JOIN Facturas f ON df.id_factura = f.id_factura
                WHERE df.id_producto IS NOT NULL
                AND DATE(f.fecha_factura) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
        elif periodo == 'anio':
            mano_obra = get_one("""
                SELECT COALESCE(SUM(df.subtotal), 0) AS total
                FROM DetalleFactura df
                INNER JOIN Facturas f ON df.id_factura = f.id_factura
                WHERE df.id_servicio IS NOT NULL
                AND strftime('%Y', f.fecha_factura) = strftime('%Y', 'now')
            """)
            
            repuestos = get_one("""
                SELECT COALESCE(SUM(df.subtotal), 0) AS total
                FROM DetalleFactura df
                INNER JOIN Facturas f ON df.id_factura = f.id_factura
                WHERE df.id_producto IS NOT NULL
                AND strftime('%Y', f.fecha_factura) = strftime('%Y', 'now')
            """)
        else:
            mano_obra = get_one("""
                SELECT COALESCE(SUM(df.subtotal), 0) AS total
                FROM DetalleFactura df
                INNER JOIN Facturas f ON df.id_factura = f.id_factura
                WHERE df.id_servicio IS NOT NULL
                AND strftime('%Y-%m', f.fecha_factura) = strftime('%Y-%m', 'now')
            """)
            
            repuestos = get_one("""
                SELECT COALESCE(SUM(df.subtotal), 0) AS total
                FROM DetalleFactura df
                INNER JOIN Facturas f ON df.id_factura = f.id_factura
                WHERE df.id_producto IS NOT NULL
                AND strftime('%Y-%m', f.fecha_factura) = strftime('%Y-%m', 'now')
            """)
        
        mo_total = mano_obra['total'] if mano_obra else 0
        rep_total = repuestos['total'] if repuestos else 0
        
        return jsonify({
            'mano_obra': mo_total,
            'repuestos': rep_total,
            'total': mo_total + rep_total
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500