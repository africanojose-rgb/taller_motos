from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth

bp = Blueprint('citas', __name__, url_prefix='/api/citas')


@bp.route('', methods=['GET'])
@require_auth
def listar_citas():
    try:
        citas = get_all("""
            SELECT c.*, cl.nombre AS cliente, m.placa AS vehiculo
            FROM Citas c
            INNER JOIN Clientes cl ON c.id_cliente = cl.id_cliente
            INNER JOIN Motociletas m ON c.id_moto = m.id_moto
            ORDER BY c.fecha_cita DESC
        """)
        return jsonify(citas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['GET'])
@require_auth
def obtener_cita(id):
    try:
        cita = get_one("SELECT * FROM Citas WHERE id_cita = ?", (id,))
        if not cita:
            return jsonify({'error': 'Cita no encontrada'}), 404
        return jsonify(cita)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@require_auth
def crear_cita():
    try:
        data = request.json
        if not data or not data.get('id_cliente') or not data.get('id_moto') or not data.get('fecha_cita') or not data.get('hora_cita'):
            return jsonify({'error': 'Campos requeridos: id_cliente, id_moto, fecha_cita, hora_cita'}), 400
        
        id_cita = execute("""
            INSERT INTO Citas (id_cliente, id_moto, fecha_cita, hora_cita, servicio, observaciones, estado)
            VALUES (?, ?, ?, ?, ?, ?, 'Programada')
        """, (data['id_cliente'], data['id_moto'], data['fecha_cita'], 
             data['hora_cita'], data.get('servicio'), data.get('observaciones')))
        return jsonify({'id_cita': id_cita}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['PUT'])
@require_auth
def actualizar_cita(id):
    try:
        data = request.json
        execute("""
            UPDATE Citas SET fecha_cita=?, hora_cita=?, servicio=?, 
            observaciones=?, estado=? WHERE id_cita = ?
        """, (data.get('fecha_cita'), data.get('hora_cita'), data.get('servicio'),
             data.get('observaciones'), data.get('estado'), id))
        return jsonify({'message': 'Cita actualizada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_cita(id):
    try:
        execute("DELETE FROM Citas WHERE id_cita = ?", (id,))
        return jsonify({'message': 'Cita eliminada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500