from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth

bp = Blueprint('motocicletas', __name__, url_prefix='/api/motocicletas')


@bp.route('', methods=['GET'])
@require_auth
def listar_motocicletas():
    try:
        motos = get_all("""
            SELECT m.*, c.nombre AS cliente, mo.nombre AS modelo, ma.nombre AS marca
            FROM Motociletas m
            INNER JOIN Clientes c ON m.id_cliente = c.id_cliente
            INNER JOIN ModelosMoto mo ON m.id_modelo = mo.id_modelo
            INNER JOIN MarcasMoto ma ON mo.id_marca = ma.id_marca
            WHERE m.estado = 1
            ORDER BY m.placa
        """)
        return jsonify(motos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['GET'])
@require_auth
def obtener_motocicleta(id):
    try:
        moto = get_one("""
            SELECT m.*, c.nombre AS cliente, mo.nombre AS modelo, ma.nombre AS marca
            FROM Motociletas m
            INNER JOIN Clientes c ON m.id_cliente = c.id_cliente
            INNER JOIN ModelosMoto mo ON m.id_modelo = mo.id_modelo
            INNER JOIN MarcasMoto ma ON mo.id_marca = ma.id_marca
            WHERE m.id_moto = ?
        """, (id,))
        if not moto:
            return jsonify({'error': 'Motocicleta no encontrada'}), 404
        return jsonify(moto)
    except Exception as e:
        return jsonify({'error': 'Error interno'}), 500


@bp.route('', methods=['POST'])
@require_auth
def crear_motocicleta():
    try:
        data = request.json
        if not data or not data.get('id_cliente') or not data.get('id_modelo') or not data.get('placa'):
            return jsonify({'error': 'Campos requeridos: id_cliente, id_modelo, placa'}), 400
        
        id_moto = execute("""
            INSERT INTO Motociletas (id_cliente, id_marca, id_modelo, placa, color, kilometraje, vin, num_serie, anio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data['id_cliente'], data.get('id_marca'), data['id_modelo'], data['placa'],
             data.get('color'), data.get('kilometraje'), data.get('vin'),
             data.get('num_serie'), data.get('anio')))
        return jsonify({'id_moto': id_moto}), 201
    except Exception as e:
        return jsonify({'error': 'Error interno'}), 500


@bp.route('/<int:id>', methods=['PUT'])
@require_auth
def actualizar_motocicleta(id):
    try:
        data = request.json
        execute("""
            UPDATE Motociletas SET id_cliente=?, id_marca=?, id_modelo=?, placa=?,
            color=?, kilometraje=?, vin=?, num_serie=?, anio=?
            WHERE id_moto = ?
        """, (data['id_cliente'], data.get('id_marca'), data['id_modelo'], data['placa'],
             data.get('color'), data.get('kilometraje'), data.get('vin'),
             data.get('num_serie'), data.get('anio'), id))
        return jsonify({'message': 'Motocicleta actualizada'})
    except Exception as e:
        return jsonify({'error': 'Error interno'}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_motocicleta(id):
    try:
        execute("UPDATE Motociletas SET estado = 0 WHERE id_moto = ?", (id,))
        return jsonify({'message': 'Motocicleta eliminada'})
    except Exception as e:
        return jsonify({'error': 'Error interno'}), 500