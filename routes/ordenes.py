from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth
import random

bp = Blueprint('ordenes', __name__, url_prefix='/api/ordenes')


@bp.route('', methods=['GET'])
@require_auth
def listar_ordenes():
    try:
        ordenes = get_all("""
            SELECT o.*, m.placa, c.nombre AS cliente, e.nombre AS mecanico
            FROM OrdenesTrabajo o
            INNER JOIN Motocicletas m ON o.id_moto = m.id_moto
            INNER JOIN Clientes c ON o.id_cliente = c.id_cliente
            LEFT JOIN Empleados e ON o.id_empleado = e.id_empleado
            ORDER BY o.fecha_ingreso DESC
        """)
        return jsonify(ordenes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['GET'])
@require_auth
def obtener_orden(id):
    try:
        orden = get_one("""
            SELECT o.*, m.placa, c.nombre AS cliente, e.nombre AS mecanico
            FROM OrdenesTrabajo o
            INNER JOIN Motocicletas m ON o.id_moto = m.id_moto
            INNER JOIN Clientes c ON o.id_cliente = c.id_cliente
            LEFT JOIN Empleados e ON o.id_empleado = e.id_empleado
            WHERE o.id_orden = ?
        """, (id,))
        if not orden:
            return jsonify({'error': 'Orden no encontrada'}), 404
        
        servicios = get_all("""
            SELECT d.*, s.nombre, s.descripcion
            FROM DetalleOrden d
            INNER JOIN Servicios s ON d.id_servicio = s.id_servicio
            WHERE d.id_orden = ?
        """, (id,))
        orden['servicios'] = servicios
        return jsonify(orden)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@require_auth
def crear_orden():
    try:
        data = request.json
        if not data or not data.get('id_moto') or not data.get('id_cliente'):
            return jsonify({'error': 'Campos requeridos: id_moto, id_cliente'}), 400
        
        ultimo = get_one("SELECT MAX(id_orden) as max_id FROM OrdenesTrabajo")
        siguiente = (ultimo['max_id'] or 0) + 1
        numero_orden = "OT-{0:04d}".format(siguiente)
        id_orden = execute("""
            INSERT INTO OrdenesTrabajo (id_moto, id_cliente, id_empleado, numero_orden, 
            kilometraje_ingreso, observaciones, estado)
            VALUES (?, ?, ?, ?, ?, ?, 'Pendiente')
        """, (data['id_moto'], data['id_cliente'], data.get('id_empleado'), 
             numero_orden, data.get('kilometraje_ingreso'), data.get('observaciones')))
        return jsonify({'id_orden': id_orden, 'numero_orden': numero_orden}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/servicios', methods=['POST'])
@require_auth
def agregar_servicio(id):
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        cantidad = data.get('cantidad', 1)
        precio_unitario = data.get('precio_unitario', 0)
        subtotal = precio_unitario * cantidad
        
        # Si es un servicio
        if data.get('id_servicio'):
            precio = get_one("SELECT precio FROM Servicios WHERE id_servicio = ?", (data['id_servicio'],))
            if precio:
                precio_unitario = precio['precio']
                subtotal = precio_unitario * cantidad
                execute("""
                    INSERT INTO DetalleOrden (id_orden, id_servicio, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (id, data['id_servicio'], cantidad, precio_unitario, subtotal))
        
        # Si es un producto
        elif data.get('id_producto'):
            producto = get_one("SELECT precio_venta FROM Productos WHERE id_producto = ?", (data['id_producto'],))
            if producto:
                precio_unitario = producto['precio_venta']
                subtotal = precio_unitario * cantidad
                execute("""
                    INSERT INTO DetalleOrden (id_orden, id_producto, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (id, data['id_producto'], cantidad, precio_unitario, subtotal))
        
        # Actualizar total de la orden
        execute("""
            UPDATE OrdenesTrabajo
            SET total = (SELECT COALESCE(SUM(subtotal), 0) FROM DetalleOrden WHERE id_orden = ?) - descuento
            WHERE id_orden = ?
        """, (id, id))
        
        return jsonify({'message': 'Detalle agregado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['PUT'])
@require_auth
def actualizar_orden(id):
    try:
        data = request.json
        execute("""
            UPDATE OrdenesTrabajo SET estado=?, observaciones=?, descuento=?
            WHERE id_orden = ?
        """, (data.get('estado'), data.get('observaciones'), data.get('descuento', 0), id))
        return jsonify({'message': 'Orden actualizada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/entregar', methods=['POST'])
@require_auth
def entrega_orden(id):
    try:
        data = request.json
        execute("""
            UPDATE OrdenesTrabajo 
            SET estado='Entregado', fecha_entrega=datetime('now'), kilometraje_salida=?
            WHERE id_orden = ?
        """, (data.get('kilometraje_salida'), id))
        return jsonify({'message': 'Orden entregada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500