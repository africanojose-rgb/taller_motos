from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth

bp = Blueprint('config', __name__, url_prefix='/api/config')


@bp.route('', methods=['GET'])
@require_auth
def listar_config():
    try:
        config = get_all("SELECT * FROM Config ORDER BY clave")
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/dict', methods=['GET'])
@require_auth
def listar_config_dict():
    try:
        config_items = get_all("SELECT clave, valor FROM Config")
        config_dict = {item['clave']: item['valor'] for item in config_items}
        return jsonify(config_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<clave>', methods=['GET'])
@require_auth
def obtener_config(clave):
    try:
        item = get_one("SELECT * FROM Config WHERE clave = ?", (clave,))
        if not item:
            return jsonify({'error': 'Configuración no encontrada'}), 404
        return jsonify(item)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@require_auth
def guardar_config():
    try:
        data = request.json
        if not data or not data.get('clave'):
            return jsonify({'error': 'Clave requerida'}), 400
        
        existing = get_one("SELECT id_config FROM Config WHERE clave = ?", (data['clave'],))
        if existing:
            execute("""
                UPDATE Config SET valor = ?, descripcion = ?, fecha_actualizacion = datetime('now')
                WHERE clave = ?
            """, (data.get('valor'), data.get('descripcion'), data['clave']))
            return jsonify({'message': 'Configuración actualizada'})
        else:
            execute("""
                INSERT INTO Config (clave, valor, descripcion)
                VALUES (?, ?, ?)
            """, (data['clave'], data.get('valor'), data.get('descripcion')))
            return jsonify({'message': 'Configuración creada'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bulk', methods=['POST'])
@require_auth
def guardar_bulk():
    try:
        data = request.json
        for item in data:
            clave = item.get('clave')
            valor = item.get('valor')
            descripcion = item.get('descripcion')
            
            existing = get_one("SELECT id_config FROM Config WHERE clave = ?", (clave,))
            if existing:
                execute("UPDATE Config SET valor = ?, fecha_actualizacion = datetime('now') WHERE clave = ?", (valor, clave))
            else:
                execute("INSERT INTO Config (clave, valor, descripcion) VALUES (?, ?, ?)", (clave, valor, descripcion))
        
        return jsonify({'message': 'Configuraciones actualizadas'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500