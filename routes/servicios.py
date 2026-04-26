from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth

bp = Blueprint('servicios', __name__, url_prefix='/api/servicios')


@bp.route('', methods=['GET'])
@require_auth
def listar_servicios():
    try:
        servicios = get_all("SELECT * FROM Servicios WHERE estado = 1 ORDER BY nombre")
        return jsonify(servicios)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['GET'])
@require_auth
def obtener_servicio(id):
    try:
        servicio = get_one("SELECT * FROM Servicios WHERE id_servicio = ?", (id,))
        if not servicio:
            return jsonify({'error': 'Servicio no encontrado'}), 404
        return jsonify(servicio)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@require_auth
def crear_servicio():
    try:
        data = request.json
        if not data or not data.get('nombre') or not data.get('precio'):
            return jsonify({'error': 'Campos requeridos: nombre, precio'}), 400
        
        id_servicio = execute("""
            INSERT INTO Servicios (nombre, descripcion, precio, duracion_estimada)
            VALUES (?, ?, ?, ?)
        """, (data['nombre'], data.get('descripcion'), data['precio'], data.get('duracion_estimada')))
        return jsonify({'id_servicio': id_servicio}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['PUT'])
@require_auth
def actualizar_servicio(id):
    try:
        data = request.json
        execute("""
            UPDATE Servicios SET nombre=?, descripcion=?, precio=?, duracion_estimada=?
            WHERE id_servicio = ?
        """, (data['nombre'], data.get('descripcion'), data['precio'], data.get('duracion_estimada'), id))
        return jsonify({'message': 'Servicio actualizado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_servicio(id):
    try:
        execute("UPDATE Servicios SET estado = 0 WHERE id_servicio = ?", (id,))
        return jsonify({'message': 'Servicio eliminado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500