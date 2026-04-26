from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth

bp = Blueprint('pagos', __name__, url_prefix='/api/pagos')


@bp.route('', methods=['GET'])
@require_auth
def listar_pagos():
    try:
        pagos = get_all("""
            SELECT p.*, o.numero_orden, c.nombre AS cliente
            FROM Pagos p
            INNER JOIN OrdenesTrabajo o ON p.id_orden = o.id_orden
            INNER JOIN Clientes c ON o.id_cliente = c.id_cliente
            ORDER BY p.fecha_pago DESC
        """)
        return jsonify(pagos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/orden/<int:id_orden>', methods=['GET'])
@require_auth
def pagos_por_orden(id_orden):
    try:
        pagos = get_all("""
            SELECT * FROM Pagos WHERE id_orden = ? ORDER BY fecha_pago DESC
        """, (id_orden,))
        return jsonify(pagos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@require_auth
def registrar_pago():
    try:
        data = request.json
        if not data or not data.get('id_orden') or not data.get('monto'):
            return jsonify({'error': 'Campos requeridos: id_orden, monto'}), 400
        
        id_pago = execute("""
            INSERT INTO Pagos (id_orden, monto, metodo_pago, numero_referencia, observaciones)
            VALUES (?, ?, ?, ?, ?)
        """, (data['id_orden'], data['monto'], data.get('metodo_pago'), 
             data.get('numero_referencia'), data.get('observaciones')))
        
        total_orden = get_one("SELECT total FROM OrdenesTrabajo WHERE id_orden = ?", (data['id_orden'],))
        if total_orden and total_orden['total']:
            total_pagado = get_one("""
                SELECT COALESCE(SUM(monto), 0) AS total FROM Pagos WHERE id_orden = ?
            """, (data['id_orden'],))
            if total_pagado and total_pagado['total'] >= total_orden['total']:
                execute("UPDATE OrdenesTrabajo SET estado_pago = 1 WHERE id_orden = ?", (data['id_orden'],))
        
        return jsonify({'id_pago': id_pago}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_pago(id):
    try:
        execute("DELETE FROM Pagos WHERE id_pago = ?", (id,))
        return jsonify({'message': 'Pago eliminado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500