from flask import Blueprint, request, jsonify
from db import get_all, get_one, execute
from routes import require_auth

bp = Blueprint('nomina', __name__, url_prefix='/api/nomina')


@bp.route('/empleados/comisiones', methods=['GET'])
@require_auth
def listar_comisiones():
    try:
        comisiones = get_all("""
            SELECT c.*, e.nombre AS empleado
            FROM Comisiones c
            INNER JOIN Empleados e ON c.id_empleado = e.id_empleado
            WHERE c.estado = 1
            ORDER BY e.nombre
        """)
        return jsonify(comisiones)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/empleados/<int:id>/comisiones', methods=['GET'])
@require_auth
def comisiones_empleado(id):
    try:
        comisiones = get_all("""
            SELECT * FROM Comisiones
            WHERE id_empleado = ? AND estado = 1
        """, (id,))
        return jsonify(comisiones)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/empleados/<int:id>/comisiones', methods=['POST'])
@require_auth
def crear_comision(id):
    try:
        data = request.json
        if not data or not data.get('tipo_comision') or data.get('porcentaje') is None:
            return jsonify({'error': 'Tipo y porcentaje requeridos'}), 400
        
        id_comision = execute("""
            INSERT INTO Comisiones (id_empleado, tipo_comision, porcentaje)
            VALUES (?, ?, ?)
        """, (id, data['tipo_comision'], data['porcentaje']))
        return jsonify({'id_comision': id_comision}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/comisiones/<int:id>', methods=['PUT'])
@require_auth
def actualizar_comision(id):
    try:
        data = request.json
        execute("UPDATE Comisiones SET tipo_comision = ?, porcentaje = ? WHERE id_comision = ?",
            (data['tipo_comision'], data['porcentaje'], id))
        return jsonify({'message': 'Comisión actualizada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/comisiones/<int:id>', methods=['DELETE'])
@require_auth
def eliminar_comision(id):
    try:
        execute("UPDATE Comisiones SET estado = 0 WHERE id_comision = ?", (id,))
        return jsonify({'message': 'Comisión eliminada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/empleados/<int:id>/calcular', methods=['GET'])
@require_auth
def calcular_comisiones(id):
    try:
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        
        # Obtener facturas pagadas del empleado (solo mano de obra - servicios)
        facturas = get_all("""
            SELECT f.id_factura, f.numero_factura, f.fecha_factura, f.mano_obra, f.id_orden
            FROM Facturas f
            WHERE f.id_empleado = ? AND f.estado = 'Pagada'
            AND f.fecha_factura BETWEEN ? AND ?
        """, (id, desde or '1900-01-01', hasta or '2100-12-31'))
        
        # Obtener porcentaje de comisión del empleado
        comisiones = get_all("SELECT * FROM Comisiones WHERE id_empleado = ? AND estado = 1", (id,))
        
        # Obtener nombre del empleado
        empleado = get_one("SELECT nombre, cargo FROM Empleados WHERE id_empleado = ?", (id,))
        
        total_comisiones = 0
        detalle = []
        
        for factura in facturas:
            mano_obra = factura.get('mano_obra', 0) or 0
            for com in comisiones:
                if com['tipo_comision'] == 'servicio':
                    comision = mano_obra * com['porcentaje'] / 100
                    total_comisiones += comision
                    detalle.append({
                        'id_factura': factura['id_factura'],
                        'numero_factura': factura['numero_factura'],
                        'id_orden': factura.get('id_orden'),
                        'tipo': 'servicio',
                        'porcentaje': com['porcentaje'],
                        'base': mano_obra,
                        'comision': round(comision, 2)
                    })
        
        return jsonify({
            'empleado': empleado,
            'total_comisiones': round(total_comisiones, 2),
            'detalle': detalle
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/periodos', methods=['GET'])
@require_auth
def listar_nominas():
    try:
        nominas = get_all("""
            SELECT n.*, e.nombre AS empleado
            FROM Nomina n
            INNER JOIN Empleados e ON n.id_empleado = e.id_empleado
            ORDER BY n.periodo DESC, e.nombre
        """)
        return jsonify(nominas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/empleados/<int:id>/nominas', methods=['POST'])
@require_auth
def crear_nomina(id):
    try:
        data = request.json
        if not data or not data.get('periodo'):
            return jsonify({'error': 'Periodo requerido'}), 400
        
        id_nomina = execute("""
            INSERT INTO Nomina (id_empleado, periodo, salario_base, total_comisiones, bonificaciones, deducciones, total_pagar, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id, data['periodo'], data.get('salario_base', 0), data.get('total_comisiones', 0),
             data.get('bonificaciones', 0), data.get('deducciones', 0), data.get('total_pagar', 0),
             data.get('estado', 'Pendiente')))
        return jsonify({'id_nomina': id_nomina}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500