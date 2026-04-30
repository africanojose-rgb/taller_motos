from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder=None)
CORS(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'taller.db')
FRONTEND_DIST = os.path.join(BASE_DIR, 'frontend', 'dist')


def get_db_connection():
    import sqlite3
    return sqlite3.connect(DATABASE)


def init_database():
    if not os.path.exists(DATABASE):
        import db
        db.init_db()
        print("Base de datos creada exitosamente")


from routes import config, marcas_motos, clientes, empleados, nomina
from routes import motocicletas, ordenes, servicios, inventario, facturas
from routes import reportes, auth, citas, pagos

app.register_blueprint(config.bp)
app.register_blueprint(marcas_motos.bp)
app.register_blueprint(clientes.bp)
app.register_blueprint(empleados.bp)
app.register_blueprint(nomina.bp)
app.register_blueprint(motocicletas.bp)
app.register_blueprint(ordenes.bp)
app.register_blueprint(servicios.bp)
app.register_blueprint(inventario.bp)
app.register_blueprint(facturas.bp)
app.register_blueprint(reportes.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(citas.bp)
app.register_blueprint(pagos.bp)


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/')
def serve_frontend():
    if os.path.exists(FRONTEND_DIST):
        return send_from_directory(FRONTEND_DIST, 'index.html')
    return jsonify({'error': 'Frontend no encontrado. Ejecuta: cd frontend && npm run build'}), 404


@app.route('/<path:filename>')
def serve_static(filename):
    if os.path.exists(FRONTEND_DIST):
        file_path = os.path.join(FRONTEND_DIST, filename)
        if os.path.exists(file_path):
            return send_from_directory(FRONTEND_DIST, filename)
    # Si no existe el archivo, servir el index.html para Vue Router (SPA)
    if os.path.exists(FRONTEND_DIST):
        return send_from_directory(FRONTEND_DIST, 'index.html')
    return jsonify({'error': 'Archivo no encontrado'}), 404


if __name__ == '__main__':
    init_database()
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    print(f"\n{'='*50}")
    print("TALLER DE MOTOS - Sistema de Gestion")
    print(f"{'='*50}")
    print(f"API Backend: http://localhost:{port}/api")
    if os.path.exists(FRONTEND_DIST):
        print(f"Frontend:   http://localhost:{port}")
    else:
        print(f"Frontend:   Ejecuta 'cd frontend && npm run dev'")
    print(f"Login:     admin / admin123")
    print(f"{'='*50}\n")
    app.run(debug=debug, host='0.0.0.0', port=port)