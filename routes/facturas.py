from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth
from datetime import datetime

bp = Blueprint('facturas', __name__, url_prefix='/api/facturas')


@bp.route('', methods=['GET'])
@require_auth
def listar_facturas():
    try:
        facturas = get_all("""
            SELECT f.*, c.nombre AS cliente, c.documento, e.nombre AS empleado, e.cargo AS empleado_cargo,
                   o.numero_orden AS orden_numero,
                   'FAC-' || printf('%05d', f.id_factura) AS numero_control
            FROM Facturas f
            LEFT JOIN Clientes c ON f.id_cliente = c.id_cliente
            LEFT JOIN Empleados e ON f.id_empleado = e.id_empleado
            LEFT JOIN OrdenesTrabajo o ON f.id_orden = o.id_orden
            ORDER BY f.fecha_factura DESC
        """)
        return jsonify(facturas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ordenes-disponibles', methods=['GET'])
@require_auth
def listar_ordenes_sin_factura():
    try:
        ordenes = get_all("""
            SELECT o.id_orden, o.numero_orden, o.fecha_ingreso, o.total, o.estado,
                   c.nombre AS cliente, m.placa,
                   (SELECT SUM(subtotal) FROM DetalleOrden WHERE id_orden = o.id_orden AND id_servicio IS NOT NULL) AS mano_obra
            FROM OrdenesTrabajo o
            INNER JOIN Clientes c ON o.id_cliente = c.id_cliente
            INNER JOIN Motocicletas m ON o.id_moto = m.id_moto
            LEFT JOIN Facturas f ON o.id_orden = f.id_orden
            WHERE o.estado IN ('Completado', 'Entregado') AND f.id_factura IS NULL
            ORDER BY o.fecha_ingreso DESC
        """)
        return jsonify(ordenes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/orden/<int:id_orden>', methods=['GET'])
@require_auth
def obtener_datos_orden(id_orden):
    try:
        orden = get_one("""
            SELECT o.*, c.nombre AS cliente, c.id_cliente, m.placa, m.id_moto, o.id_empleado
            FROM OrdenesTrabajo o
            INNER JOIN Clientes c ON o.id_cliente = c.id_cliente
            INNER JOIN Motocicletas m ON o.id_moto = m.id_moto
            WHERE o.id_orden = ?
        """, (id_orden,))
        
        if not orden:
            return jsonify({'error': 'Orden no encontrada'}), 404
        
        servicios = get_all("""
            SELECT do.*, s.nombre AS servicio_nombre, s.precio AS precio_servicio
            FROM DetalleOrden do
            INNER JOIN Servicios s ON do.id_servicio = s.id_servicio
            WHERE do.id_orden = ? AND do.id_servicio IS NOT NULL
        """, (id_orden,))
        
        productos = get_all("""
            SELECT do.*, p.nombre AS producto_nombre, p.precio_venta
            FROM DetalleOrden do
            INNER JOIN Productos p ON do.id_producto = p.id_producto
            WHERE do.id_orden = ? AND do.id_producto IS NOT NULL
        """, (id_orden,))
        
        return jsonify({
            'orden': orden,
            'servicios': servicios,
            'productos': productos
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['GET'])
@require_auth
def obtener_factura(id):
    try:
        factura = get_one("""
            SELECT f.*, c.nombre AS cliente, c.documento, c.telefono, c.direccion, c.email,
                   e.nombre AS empleado, e.cargo AS empleado_cargo,
                   o.numero_orden AS orden_numero
            FROM Facturas f
            LEFT JOIN Clientes c ON f.id_cliente = c.id_cliente
            LEFT JOIN Empleados e ON f.id_empleado = e.id_empleado
            LEFT JOIN OrdenesTrabajo o ON f.id_orden = o.id_orden
            WHERE f.id_factura = ?
        """, (id,))
        if not factura:
            return jsonify({'error': 'Factura no encontrada'}), 404
        
        detalle_productos = get_all("""
            SELECT df.*, p.nombre AS producto, p.codigo
            FROM DetalleFactura df
            LEFT JOIN Productos p ON df.id_producto = p.id_producto
            WHERE df.id_factura = ? AND df.id_producto IS NOT NULL
        """, (id,))
        
        detalle_servicios = get_all("""
            SELECT df.*, s.nombre AS servicio
            FROM DetalleFactura df
            LEFT JOIN Servicios s ON df.id_servicio = s.id_servicio
            WHERE df.id_factura = ? AND df.id_servicio IS NOT NULL
        """, (id,))
        
        factura['productos'] = detalle_productos
        factura['servicios'] = detalle_servicios
        return jsonify(factura)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@require_auth
def crear_factura():
    try:
        data = request.json
        if not data or not data.get('id_cliente'):
            return jsonify({'error': 'Cliente requerido'}), 400
        
        numero = generar_numero_factura()
        
        # Calcular mano de obra desde servicios
        mano_obra = 0
        if data.get('detalle'):
            for item in data['detalle']:
                if item.get('id_servicio'):
                    mano_obra += item.get('subtotal', 0)
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        id_factura = execute("""
            INSERT INTO Facturas (numero_factura, id_cliente, id_orden, id_empleado, mano_obra, subtotal, descuento, iva, total, metodo_pago, estado, observaciones, fecha_factura)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (numero, data['id_cliente'], data.get('id_orden'), data.get('id_empleado'), mano_obra, 
             data.get('subtotal', 0), data.get('descuento', 0), data.get('iva', 0), data.get('total', 0), 
             data.get('metodo_pago'), data.get('estado', 'Pagada'), data.get('observaciones'), 
             fecha_actual))
        
        # Actualizar numero_control
        execute("UPDATE Facturas SET numero_control = ? WHERE id_factura = ?", (f'FAC-{id_factura:05d}', id_factura))
        
        if data.get('detalle'):
            for item in data['detalle']:
                # Guardar servicio
                if item.get('id_servicio'):
                    execute("""
                        INSERT INTO DetalleFactura (id_factura, id_servicio, descripcion, cantidad, precio_unitario, subtotal)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (id_factura, item.get('id_servicio'), item.get('descripcion', 'Servicio'),
                         item.get('cantidad', 1), item.get('precio_unitario'), item.get('subtotal')))
                
                # Guardar producto y descontar stock
                if item.get('id_producto'):
                    execute("""
                        INSERT INTO DetalleFactura (id_factura, id_producto, descripcion, cantidad, precio_unitario, subtotal)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (id_factura, item.get('id_producto'), item.get('descripcion'),
                         item.get('cantidad', 1), item.get('precio_unitario'), item.get('subtotal')))
                    
                    execute("UPDATE Productos SET stock_actual = stock_actual - ? WHERE id_producto = ?",
                        (item.get('cantidad', 1), item.get('id_producto')))
        
        # Si hay orden, marcarla como facturada
        if data.get('id_orden'):
            execute("UPDATE OrdenesTrabajo SET estado_pago = 1 WHERE id_orden = ?", (data['id_orden'],))
        
        return jsonify({
            'id_factura': id_factura, 
            'numero_factura': numero,
            'numero_control': f'FAC-{id_factura:05d}'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_factura(id):
    try:
        detalle = get_all("SELECT id_producto, cantidad FROM DetalleFactura WHERE id_factura = ?", (id,))
        for item in detalle:
            if item['id_producto']:
                execute("UPDATE Productos SET stock_actual = stock_actual + ? WHERE id_producto = ?",
                    (item['cantidad'], item['id_producto']))
        
        execute("DELETE FROM DetalleFactura WHERE id_factura = ?", (id,))
        execute("DELETE FROM Facturas WHERE id_factura = ?", (id,))
        return jsonify({'message': 'Factura eliminada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ventas', methods=['GET'])
@require_auth
def reporte_ventas():
    try:
        ventas = get_all("""
            SELECT f.numero_factura, f.fecha_factura, f.total, f.metodo_pago,
                   c.nombre AS cliente, c.documento
            FROM Facturas f
            LEFT JOIN Clientes c ON f.id_cliente = c.id_cliente
            WHERE f.estado = 'Pagada'
            ORDER BY f.fecha_factura DESC
        """)
        return jsonify(ventas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/resumen', methods=['GET'])
@require_auth
def resumen_ventas():
    try:
        total_ventas = get_one("SELECT COALESCE(SUM(total), 0) AS total FROM Facturas WHERE estado = 'Pagada'")
        cantidad = get_one("SELECT COUNT(*) AS cantidad FROM Facturas WHERE estado = 'Pagada'")
        promedio = get_one("SELECT COALESCE(AVG(total), 0) AS promedio FROM Facturas WHERE estado = 'Pagada'")
        
        return jsonify({
            'total_ventas': total_ventas['total'] if total_ventas else 0,
            'cantidad_facturas': cantidad['cantidad'] if cantidad else 0,
            'promedio': promedio['promedio'] if promedio else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generar_numero_factura():
    from datetime import datetime
    year = datetime.now().year
    last = get_one("SELECT numero_factura FROM Facturas ORDER BY id_factura DESC LIMIT 1")
    if last and last['numero_factura']:
        try:
            # Formato: FATT2026000001
            num_str = last['numero_factura'].replace('FATT', '')
            seq = int(num_str) + 1
        except:
            seq = 1
    else:
        seq = 1
    return f"FATT{year}{seq:06d}"


@bp.route('/<int:id>/enviar', methods=['POST'])
@require_auth
def enviar_factura_email(id):
    try:
        data = request.json
        if not data or not data.get('email'):
            return jsonify({'error': 'Email requerido'}), 400
        
        # Obtener configuración SMTP
        config_smtp = get_all("SELECT clave, valor FROM Config WHERE clave LIKE 'email_%'")
        config = {c['clave']: c['valor'] for c in config_smtp}
        
        smtp_server = config.get('email_smtp', '')
        smtp_user = config.get('email_usuario', '')
        smtp_password = config.get('email_password', '')
        email_from = config.get('email_destino', smtp_user)
        
        if not smtp_server or not smtp_user or not smtp_password:
            return jsonify({'error': 'Configuración SMTP no configurada'}), 400
        
        # Obtener factura
        factura = get_one("SELECT * FROM Facturas WHERE id_factura = ?", (id,))
        if not factura:
            return jsonify({'error': 'Factura no encontrada'}), 404
        
        # Generar PDF (simple - sin附件 para evitar complicaciones)
        # En su lugar,enviamos un email con la información de la factura
        
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = data['email']
        msg['Subject'] = data.get('asunto', f"Factura {factura['numero_factura']}")
        
        body = f"""
Estimado cliente,

Adjuntamos los detalles de su factura #{factura['numero_factura']}

Fecha: {factura['fecha_factura']}
Total: ${factura['total']:,.2f}
Método de pago: {factura.get('metodo_pago', 'No especificado')}

Por favor, revisar los datos y realizar el pago según las condiciones acordadas.

Att.
Taller de Motos
"""
        msg.attach(MIMEText(body, 'plain'))
        
        # Enviar
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return jsonify({'message': 'Email enviado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500