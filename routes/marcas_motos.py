from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth

bp = Blueprint('marcas_motos', __name__, url_prefix='/api/marcas-motos')


@bp.route('', methods=['GET'])
@require_auth
def listar_marcas():
    try:
        marcas = get_all("SELECT * FROM MarcasMoto WHERE estado = 1 ORDER BY nombre")
        return jsonify(marcas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['GET'])
@require_auth
def obtener_marca(id):
    try:
        marca = get_one("SELECT * FROM MarcasMoto WHERE id_marca = ?", (id,))
        if not marca:
            return jsonify({'error': 'Marca no encontrada'}), 404
        return jsonify(marca)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@require_auth
def crear_marca():
    try:
        data = request.json
        if not data or not data.get('nombre'):
            return jsonify({'error': 'Nombre requerido'}), 400
        
        id_marca = execute("INSERT INTO MarcasMoto (nombre, logo) VALUES (?, ?)",
            (data['nombre'], data.get('logo')))
        return jsonify({'id_marca': id_marca}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['PUT'])
@require_auth
def actualizar_marca(id):
    try:
        data = request.json
        execute("UPDATE MarcasMoto SET nombre = ?, logo = ? WHERE id_marca = ?",
            (data['nombre'], data.get('logo'), id))
        return jsonify({'message': 'Marca actualizada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_marca(id):
    try:
        execute("UPDATE MarcasMoto SET estado = 0 WHERE id_marca = ?", (id,))
        return jsonify({'message': 'Marca eliminada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/modelos', methods=['GET'])
@require_auth
def listar_modelos(id):
    try:
        modelos = get_all("""
            SELECT * FROM ModelosMoto 
            WHERE id_marca = ? AND estado = 1 
            ORDER BY nombre
        """, (id,))
        return jsonify(modelos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id_marca>/modelos', methods=['POST'])
@require_auth
def crear_modelo(id_marca):
    try:
        data = request.json
        if not data or not data.get('nombre'):
            return jsonify({'error': 'Nombre requerido'}), 400
        
        id_modelo = execute("""
            INSERT INTO ModelosMoto (id_marca, nombre, cilindrada, anio_inicio, anio_fin)
            VALUES (?, ?, ?, ?, ?)
        """, (id_marca, data['nombre'], data.get('cilindrada'), data.get('anio_inicio'), data.get('anio_fin')))
        return jsonify({'id_modelo': id_modelo}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/modelos/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_modelo(id):
    try:
        execute("UPDATE ModelosMoto SET estado = 0 WHERE id_modelo = ?", (id,))
        return jsonify({'message': 'Modelo eliminado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500