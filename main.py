#!/usr/bin/env python3
"""
Taller Mecánico - Launcher
Inicia el servidor Flask y abre el navegador automáticamente
"""

import subprocess
import sys
import os
import socket
import time
import webbrowser
from pathlib import Path

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_color(text, color):
    print(f"{color}{text}{Colors.END}")

def get_port():
    """Obtiene el puerto desde .env o usa 5000 por defecto"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return int(os.getenv('PORT', 5000))
    except:
        return 5000

def check_port_in_use(port):
    """Verifica si un puerto está en uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_server(port, timeout=30):
    """Espera a que el servidor responda"""
    print(f"  Esperando respuesta en http://localhost:{port}...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            import urllib.request
            url = f"http://localhost:{port}/api/health"
            response = urllib.request.urlopen(url, timeout=2)
            if response.status == 200:
                data = response.read().decode()
                return True
        except Exception as e:
            pass
        time.sleep(0.5)
    return False

def create_virtualenv():
    """Crea el entorno virtual si no existe"""
    venv_path = Path(__file__).parent / '.venv'
    if not venv_path.exists():
        print_color("Creando entorno virtual...", Colors.YELLOW)
        subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
        print_color("Entorno virtual creado", Colors.GREEN)

def install_dependencies():
    """Instala las dependencias de requirements.txt"""
    venv_path = Path(__file__).parent / '.venv'
    pip = venv_path / ('Scripts/python.exe' if os.name == 'nt' else 'bin/pip')
    
    if not pip.exists():
        create_virtualenv()
        pip = venv_path / ('Scripts/python.exe' if os.name == 'nt' else 'bin/pip')
    
    print_color("Instalando dependencias...", Colors.YELLOW)
    
    # Actualizar pip
    subprocess.run([str(pip), 'install', '--upgrade', 'pip'], check=False)
    
    # Instalar requirements
    req_file = Path(__file__).parent / 'requirements.txt'
    if req_file.exists():
        subprocess.run([str(pip), 'install', '-r', str(req_file)], check=True)
    
    print_color("Dependencias instaladas", Colors.GREEN)
    return pip.parent

def init_database(python):
    """Inicializa la base de datos SQLite"""
    db_path = Path(__file__).parent / 'taller.db'
    if not db_path.exists():
        print_color("Creando base de datos...", Colors.YELLOW)
        subprocess.run([str(python), '-c', 'from app import init_database; init_database()'], check=True)
        print_color("Base de datos creada", Colors.GREEN)
    return db_path.exists()

def find_available_port(start_port):
    """Encuentra un puerto disponible"""
    port = start_port
    max_attempts = 10
    for i in range(max_attempts):
        if not check_port_in_use(port):
            return port
        port += 1
    return None

def show_info():
    """Muestra información del sistema"""
    port = get_port()
    db_path = Path(__file__).parent / 'taller.db'
    
    print_color("=" * 50, Colors.BLUE)
    print_color("  INFORMACIÓN DEL SISTEMA", Colors.BLUE)
    print_color("=" * 50, Colors.BLUE)
    print()
    
    # Python
    print(f"{Colors.YELLOW}Python: {Colors.END}{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Puerto
    if check_port_in_use(port):
        print(f"{Colors.YELLOW}Puerto API: {Colors.END}{port} (en uso)")
    else:
        print(f"{Colors.YELLOW}Puerto API: {Colors.END}{port} (disponible)")
    
    # Base de datos
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"{Colors.YELLOW}Base de datos: {Colors.END}taller.db ({size:,} bytes)")
    else:
        print(f"{Colors.YELLOW}Base de datos: {Colors.END}No existe")
    
    # Frontend build
    frontend = Path(__file__).parent / 'frontend' / 'dist'
    if frontend.exists():
        print(f"{Colors.YELLOW}Frontend: {Colors.END}Listo (frontend/dist)")
    else:
        print(f"{Colors.YELLOW}Frontend: {Colors.END}No construido")
        print("  Ejecuta: cd frontend && npm run build")
    
    # Entorno virtual
    venv = Path(__file__).parent / '.venv'
    if venv.exists():
        print(f"{Colors.YELLOW}Entorno virtual: {Colors.END}.venv/")
    else:
        print(f"{Colors.YELLOW}Entorno virtual: {Colors.END}No existe")
    
    print()
    print_color("URLs:", Colors.BLUE)
    print(f"  Servidor: http://localhost:{port}")
    print(f"  API:     http://localhost:{port}/api")
    print(f"  Login:   admin / admin123")
    print()


def main():
    project_dir = Path(__file__).parent.resolve()
    os.chdir(project_dir)
    
    port = get_port()
    
    print_color("=" * 50, Colors.BLUE)
    print_color("  TALLER MECÁNICO - Sistema de Gestión", Colors.BLUE)
    print_color("=" * 50, Colors.BLUE)
    print()
    
    # 1. Verificar Python
    print_color("[1/6] Verificando Python...", Colors.YELLOW)
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print_color("Error: Se requiere Python 3.8+", Colors.RED)
        sys.exit(1)
    print_color(f"  Python {python_version.major}.{python_version.minor}.{python_version.micro}", Colors.GREEN)
    
    # 2. Verificar/instalar dependencias
    print_color("[2/6] Verificando dependencias...", Colors.YELLOW)
    venv_path = project_dir / '.venv'
    python = venv_path / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    
    if not python.exists():
        python = install_dependencies()
    else:
        print_color("  Dependencias ya instaladas", Colors.GREEN)
    
    # 3. Verificar base de datos
    print_color("[3/6] Verificando base de datos...", Colors.YELLOW)
    init_database(python)
    
    # 4. Encontrar puerto disponible
    print_color("[4/6] Verificando puerto...", Colors.YELLOW)
    if check_port_in_use(port):
        print_color(f"  Puerto {port} en uso, buscando alternativo...", Colors.YELLOW)
        new_port = find_available_port(port + 1)
        if new_port:
            port = new_port
            print_color(f"  Usando puerto {port}", Colors.GREEN)
        else:
            print_color("  Error: No hay puertos disponibles", Colors.RED)
            sys.exit(1)
    else:
        print_color(f"  Puerto {port} disponible", Colors.GREEN)
    
    # 5. Iniciar servidor Flask
    print_color("[5/6] Iniciando servidor...", Colors.YELLOW)
    print()
    
    env = os.environ.copy()
    env['PORT'] = str(port)
    
    server = subprocess.Popen(
        [str(python), 'app.py'],
        cwd=str(project_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    print_color("  Servidor Flask iniciando...", Colors.GREEN)
    
    # 6. Esperar y abrir navegador
    print_color("[6/6] Esperando servidor...", Colors.YELLOW)
    
    if wait_for_server(port, timeout=15):
        print_color("  Servidor listo!", Colors.GREEN)
        print()
        print_color("=" * 50, Colors.GREEN)
        print_color(f"  Servidor: http://localhost:{port}", Colors.GREEN)
        print_color(f"  API:     http://localhost:{port}/api", Colors.GREEN)
        print_color("  Credenciales: admin / admin123", Colors.BLUE)
        print_color("=" * 50, Colors.GREEN)
        print()
        print_color("Abriendo navegador...", Colors.YELLOW)
        
        webbrowser.open(f"http://localhost:{port}")
        print()
        print_color("Presiona Ctrl+C para detener el servidor", Colors.YELLOW)
        print()
        
        # Mantener corriendo y mostrar logs
        try:
            for line in server.stdout:
                line = line.decode('utf-8', errors='ignore').rstrip()
                if 'Running on' in line:
                    print_color(f"  → {line}", Colors.GREEN)
                elif 'Error' in line or 'error' in line:
                    print_color(f"  → {line}", Colors.RED)
                elif line.startswith(' *'):
                    print(f"  {line}")
        except KeyboardInterrupt:
            print()
            print_color("\nDeteniendo servidor...", Colors.YELLOW)
            server.terminate()
            server.wait()
            print_color("Servidor detenido", Colors.GREEN)
    else:
        print_color("  Error: El servidor no respondió a tiempo", Colors.RED)
        server.terminate()
        server.wait()
        sys.exit(1)

if __name__ == '__main__':
    try:
        # Verificar argumentos
        if '--info' in sys.argv or '-i' in sys.argv:
            show_info()
        else:
            main()
    except KeyboardInterrupt:
        print()
        print_color("Operación cancelada por el usuario", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_color(f"Error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)