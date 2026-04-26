from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth

bp = Blueprint('inventario', __name__, url_prefix='/api/inventario')


@bp.route('/productos', methods=['GET'])
@require_auth
def listar_productos():
    try:
        productos = get_all("""
            SELECT p.*, c.nombre AS categoria
            FROM Productos p
            LEFT JOIN CategoriasProducto c ON p.id_categoria = c.id_categoria
            WHERE p.estado = 1
            ORDER BY p.nombre
        """)
        return jsonify(productos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/productos/<int:id>', methods=['GET'])
@require_auth
def obtener_producto(id):
    try:
        producto = get_one("""
            SELECT p.*, c.nombre AS categoria
            FROM Productos p
            LEFT JOIN CategoriasProducto c ON p.id_categoria = c.id_categoria
            WHERE p.id_producto = ?
        """, (id,))
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        return jsonify(producto)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/productos', methods=['POST'])
@require_auth
def crear_producto():
    try:
        data = request.json
        if not data or not data.get('nombre') or not data.get('codigo'):
            return jsonify({'error': 'Nombre y codigo requeridos'}), 400
        
        precio_venta = data.get('precio_venta', 0)
        precio_compra = data.get('precio_compra', 0)
        margen = ((precio_venta - precio_compra) / precio_compra * 100) if precio_compra > 0 else 0
        
        id_producto = execute("""
            INSERT INTO Productos (id_categoria, codigo, nombre, descripcion, marca, presentacion,
            stock_actual, stock_minimo, precio_compra, precio_venta, margen_ganancia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data.get('id_categoria'), data['codigo'], data['nombre'], data.get('descripcion'),
             data.get('marca'), data.get('presentacion'), data.get('stock_actual', 0), data.get('stock_minimo', 0),
             precio_compra, precio_venta, margen))
        return jsonify({'id_producto': id_producto}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/productos/<int:id>', methods=['PUT'])
@require_auth
def actualizar_producto(id):
    try:
        data = request.json
        precio_venta = data.get('precio_venta', 0)
        precio_compra = data.get('precio_compra', 0)
        margen = ((precio_venta - precio_compra) / precio_compra * 100) if precio_compra > 0 else 0
        
        execute("""
            UPDATE Productos SET id_categoria=?, codigo=?, nombre=?, descripcion=?, marca=?,
            presentacion=?, stock_actual=?, stock_minimo=?, precio_compra=?, precio_venta=?, margen_ganancia=?
            WHERE id_producto = ?
        """, (data.get('id_categoria'), data.get('codigo'), data['nombre'], data.get('descripcion'),
             data.get('marca'), data.get('presentacion'), data.get('stock_actual'), data.get('stock_minimo'),
             precio_compra, precio_venta, margen, id))
        return jsonify({'message': 'Producto actualizado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/productos/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_producto(id):
    try:
        execute("UPDATE Productos SET estado = 0 WHERE id_producto = ?", (id,))
        return jsonify({'message': 'Producto eliminado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/categorias', methods=['GET'])
@require_auth
def listar_categorias():
    try:
        categorias = get_all("SELECT * FROM CategoriasProducto WHERE estado = 1 ORDER BY nombre")
        return jsonify(categorias)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/categorias', methods=['POST'])
@require_auth
def crear_categoria():
    try:
        data = request.json
        if not data or not data.get('nombre'):
            return jsonify({'error': 'Nombre requerido'}), 400
        
        id_categoria = execute("INSERT INTO CategoriasProducto (nombre, descripcion) VALUES (?, ?)",
            (data['nombre'], data.get('descripcion')))
        return jsonify({'id_categoria': id_categoria}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/kardex', methods=['GET'])
@require_auth
def listar_kardex():
    try:
        kardex = get_all("""
            SELECT k.*, p.nombre AS producto, p.codigo, u.nombre AS usuario
            FROM Kardex k
            INNER JOIN Productos p ON k.id_producto = p.id_producto
            LEFT JOIN Usuarios u ON k.id_usuario = u.id_usuario
            ORDER BY k.fecha_movimiento DESC
            LIMIT 100
        """)
        return jsonify(kardex)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/kardex', methods=['POST'])
@require_auth
def registrar_movimiento():
    try:
        data = request.json
        if not data or not data.get('id_producto') or not data.get('tipo_movimiento') or not data.get('cantidad'):
            return jsonify({'error': 'Campos requeridos'}), 400
        
        cantidad = data['cantidad']
        precio_unitario = data.get('precio_unitario', 0)
        total = cantidad * precio_unitario
        
        execute("""
            INSERT INTO Kardex (id_producto, tipo_movimiento, cantidad, precio_unitario, total, observaciones, id_usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data['id_producto'], data['tipo_movimiento'], cantidad, precio_unitario, total,
             data.get('observaciones'), data.get('id_usuario')))
        
        if data['tipo_movimiento'] == 'entrada':
            execute("UPDATE Productos SET stock_actual = stock_actual + ? WHERE id_producto = ?",
                (cantidad, data['id_producto']))
        elif data['tipo_movimiento'] == 'salida':
            execute("UPDATE Productos SET stock_actual = stock_actual - ? WHERE id_producto = ?",
                (cantidad, data['id_producto']))
        
        return jsonify({'message': 'Movimiento registrado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stock-bajo', methods=['GET'])
@require_auth
def stock_bajo():
    try:
        productos = get_all("""
            SELECT p.*, c.nombre AS categoria
            FROM Productos p
            LEFT JOIN CategoriasProducto c ON p.id_categoria = c.id_categoria
            WHERE p.stock_actual <= p.stock_minimo AND p.estado = 1
            ORDER BY p.stock_actual ASC
        """)
        return jsonify(productos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500