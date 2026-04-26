from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes.auth import require_auth

bp = Blueprint('clientes', __name__, url_prefix='/api/clientes')


@bp.route('', methods=['GET'])
@require_auth
def listar_clientes():
    try:
        clientes = get_all("SELECT * FROM Clientes WHERE estado = 1 ORDER BY nombre")
        return jsonify(clientes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['GET'])
@require_auth
def obtener_cliente(id):
    try:
        cliente = get_one("SELECT * FROM Clientes WHERE id_cliente = ?", (id,))
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404
        return jsonify(cliente)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@require_auth
def crear_cliente():
    try:
        data = request.json
        if not data or not data.get('nombre') or not data.get('documento') or not data.get('tipo_documento'):
            return jsonify({'error': 'Campos requeridos: nombre, documento, tipo_documento'}), 400
        
        id_cliente = execute("""
            INSERT INTO Clientes (nombre, documento, tipo_documento, telefono, email, direccion, ciudad)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data['nombre'], data['documento'], data['tipo_documento'], 
             data.get('telefono'), data.get('email'), data.get('direccion'), data.get('ciudad')))
        return jsonify({'id_cliente': id_cliente}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['PUT'])
@require_auth
def actualizar_cliente(id):
    try:
        data = request.json
        execute("""
            UPDATE Clientes SET nombre=?, documento=?, tipo_documento=?, 
            telefono=?, email=?, direccion=?, ciudad=?
            WHERE id_cliente = ?
        """, (data['nombre'], data['documento'], data['tipo_documento'],
             data.get('telefono'), data.get('email'), data.get('direccion'), data.get('ciudad'), id))
        return jsonify({'message': 'Cliente actualizado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_cliente(id):
    try:
        execute("UPDATE Clientes SET estado = 0 WHERE id_cliente = ?", (id,))
        return jsonify({'message': 'Cliente eliminado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500