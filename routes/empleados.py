from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth

bp = Blueprint('empleados', __name__, url_prefix='/api/empleados')


@bp.route('', methods=['GET'])
@require_auth
def listar_empleados():
    try:
        empleados = get_all("SELECT * FROM Empleados WHERE estado = 1 ORDER BY nombre")
        return jsonify(empleados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['GET'])
@require_auth
def obtener_empleado(id):
    try:
        empleado = get_one("SELECT * FROM Empleados WHERE id_empleado = ?", (id,))
        if not empleado:
            return jsonify({'error': 'Empleado no encontrado'}), 404
        return jsonify(empleado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@require_auth
def crear_empleado():
    try:
        data = request.json
        if not data or not data.get('documento') or not data.get('nombre') or not data.get('cargo'):
            return jsonify({'error': 'Campos requeridos: documento, nombre, cargo'}), 400
        
        id_empleado = execute("""
            INSERT INTO Empleados (documento, nombre, telefono, email, cargo, fecha_contrato)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data['documento'], data['nombre'], data.get('telefono'), 
             data.get('email'), data['cargo'], data.get('fecha_contrato')))
        return jsonify({'id_empleado': id_empleado}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['PUT'])
@require_auth
def actualizar_empleado(id):
    try:
        data = request.json
        execute("""
            UPDATE Empleados SET documento=?, nombre=?, telefono=?, email=?, cargo=?,
            fecha_contrato=? WHERE id_empleado = ?
        """, (data.get('documento'), data['nombre'], data.get('telefono'), data.get('email'), 
             data.get('cargo'), data.get('fecha_contrato'), id))
        return jsonify({'message': 'Empleado actualizado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_empleado(id):
    try:
        execute("UPDATE Empleados SET estado = 0 WHERE id_empleado = ?", (id,))
        return jsonify({'message': 'Empleado eliminado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500