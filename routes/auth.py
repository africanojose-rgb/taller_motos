from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
import bcrypt
import os
from db import get_one, execute, get_all
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

SECRET_KEY = os.getenv('JWT_SECRET', 'taller_motos_secret_key_2024_seguro')
TOKEN_EXPIRES_HOURS = int(os.getenv('JWT_EXPIRES_HOURS', 24))


def create_token(user_id: int, rol: str) -> str:
    payload = {
        'user_id': user_id,
        'rol': rol,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRES_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401
        
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        request.user_id = payload.get('user_id')
        request.user_rol = payload.get('rol')
        
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.user_rol not in roles:
                return jsonify({'error': 'Sin permisos'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('usuario') or not data.get('contrasena'):
        return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
    
    usuario = get_one("SELECT * FROM Usuarios WHERE usuario = ? AND estado = 1", (data['usuario'],))
    
    if not usuario:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    try:
        if bcrypt.checkpw(data['contrasena'].encode('utf-8'), usuario['contrasena'].encode('utf-8')):
            token = create_token(usuario['id_usuario'], usuario['rol'])
            return jsonify({
                'id_usuario': usuario['id_usuario'],
                'nombre': usuario['nombre'],
                'rol': usuario['rol'],
                'usuario': usuario['usuario'],
                'token': token
            })
    except Exception as e:
        current_app.logger.error(f"Error en verificación de password: {e}")
    
    return jsonify({'error': 'Credenciales inválidas'}), 401


@bp.route('/registro', methods=['POST'])
@require_auth
def registro():
    data = request.json
    if not data or not data.get('usuario') or not data.get('contrasena') or not data.get('nombre'):
        return jsonify({'error': 'Campos requeridos: usuario, contrasena, nombre'}), 400
    
    usuario = data['usuario'].strip()
    contrasena = data['contrasena']
    nombre = data['nombre'].strip()
    email = (data.get('email') or '').strip()
    rol = data.get('rol', 'Admin')
    
    if len(contrasena) < 8:
        return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
    
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Email inválido'}), 400
    
    existing = get_one("SELECT id_usuario FROM Usuarios WHERE usuario = ?", (usuario,))
    if existing:
        return jsonify({'error': 'El usuario ya existe'}), 400
    
    hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
    
    id_usuario = execute("""
        INSERT INTO Usuarios (usuario, contrasena, nombre, email, rol)
        VALUES (?, ?, ?, ?, ?)
    """, (usuario, hashed.decode('utf-8'), nombre, email, rol))
    
    return jsonify({'id_usuario': id_usuario}), 201


@bp.route('/crear-desde-empleado', methods=['POST'])
@require_auth
def crear_desde_empleado():
    if request.user_rol not in ('Admin', 'Administrador'):
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.json
    if not data or not data.get('id_empleado') or not data.get('usuario') or not data.get('contrasena'):
        return jsonify({'error': 'Campos requeridos: id_empleado, usuario, contrasena'}), 400
    
    # Verificar empleado existe
    empleado = get_one("SELECT * FROM Empleados WHERE id_empleado = ?", (data['id_empleado'],))
    if not empleado:
        return jsonify({'error': 'Empleado no encontrado'}), 404
    
    # Verificar usuario no existe
    existing = get_one("SELECT id_usuario FROM Usuarios WHERE usuario = ?", (data['usuario'],))
    if existing:
        return jsonify({'error': 'Usuario ya existe'}), 400
    
    # Mapear cargo a rol
    cargo = (empleado['cargo'] or '').lower()
    rol = 'Mecanico' if 'mecan' in cargo else ('Auxiliar' if 'aux' in cargo else 'Mecanico')
    if data.get('rol'):
        allowed_roles = {'Admin', 'Administrador', 'Mecanico', 'Auxiliar'}
        if data['rol'] not in allowed_roles:
            return jsonify({'error': 'Rol inválido'}), 400
        rol = data['rol']
    
    hashed = bcrypt.hashpw(data['contrasena'].encode('utf-8'), bcrypt.gensalt())
    
    id_usuario = execute("""
        INSERT INTO Usuarios (usuario, contrasena, nombre, email, rol)
        VALUES (?, ?, ?, ?, ?)
    """, (data['usuario'], hashed.decode('utf-8'), empleado['nombre'], 
         empleado['email'], rol))
    
    return jsonify({'id_usuario': id_usuario, 'rol': rol}), 201


@bp.route('/me', methods=['GET'])
@require_auth
def me():
    usuario = get_one("SELECT id_usuario, usuario, nombre, email, rol FROM Usuarios WHERE id_usuario = ?", 
                      (request.user_id,))
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario)


@bp.route('/refresh', methods=['POST'])
@require_auth
def refresh():
    usuario = get_one("SELECT id_usuario, rol FROM Usuarios WHERE id_usuario = ?", 
                      (request.user_id,))
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    token = create_token(usuario['id_usuario'], usuario['rol'])
    return jsonify({'token': token})


@bp.route('/usuarios', methods=['GET'])
@require_auth
def listar_usuarios():
    try:
        usuarios = get_all("SELECT id_usuario, usuario, nombre, email, rol, estado, fecha_registro FROM Usuarios WHERE estado = 1 ORDER BY nombre")
        return jsonify(usuarios)
    except Exception as e:
        current_app.logger.error(f"Error listando usuarios: {e}")
        return jsonify({'error': 'Error interno'}), 500


@bp.route('/usuarios/<int:id>', methods=['PUT'])
@require_auth
def actualizar_usuario(id):
    try:
        data = request.json
        execute("""
            UPDATE Usuarios SET nombre=?, email=?, rol=?
            WHERE id_usuario = ?
        """, (data.get('nombre'), data.get('email'), data.get('rol'), id))
        return jsonify({'message': 'Usuario actualizado'})
    except Exception as e:
        current_app.logger.error(f"Error actualizando usuario: {e}")
        return jsonify({'error': 'Error interno'}), 500


@bp.route('/usuarios/<int:id>', methods=['DELETE'])
@require_auth
@require_role('Admin')
def eliminar_usuario(id):
    try:
        execute("UPDATE Usuarios SET estado = 0 WHERE id_usuario = ?", (id,))
        return jsonify({'message': 'Usuario eliminado'})
    except Exception as e:
        current_app.logger.error(f"Error eliminando usuario: {e}")
        return jsonify({'error': 'Error interno'}), 500