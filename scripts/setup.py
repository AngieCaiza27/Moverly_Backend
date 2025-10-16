#!/usr/bin/env python3
"""
Script de configuración inicial para Moverly Backend
Ejecuta la configuración básica del proyecto
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Se requiere Python 3.11 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True


def check_postgresql():
    """Verifica que PostgreSQL esté disponible"""
    print("🐘 Verificando PostgreSQL...")
    try:
        result = subprocess.run("psql --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL no encontrado")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL no está instalado o no está en el PATH")
        return False


def create_env_file():
    """Crea el archivo .env si no existe"""
    print("📝 Configurando archivo .env...")
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Archivo .env creado desde env.example")
        print("⚠️  Recuerda editar .env con tus configuraciones")
        return True
    else:
        print("❌ Archivo env.example no encontrado")
        return False


def create_virtual_environment():
    """Crea un entorno virtual si no existe"""
    print("🔧 Configurando entorno virtual...")
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Entorno virtual ya existe")
        return True
    
    if run_command("python -m venv venv", "Creando entorno virtual"):
        print("✅ Entorno virtual creado")
        return True
    return False


def install_dependencies():
    """Instala las dependencias del proyecto"""
    print("📦 Instalando dependencias...")
    
    # Determinar el comando pip según el SO
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Linux/Mac
        pip_cmd = "venv/bin/pip"
    
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Actualizando pip"),
        (f"{pip_cmd} install -r requirements.txt", "Instalando dependencias")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    print("✅ Dependencias instaladas")
    return True


def create_database():
    """Crea la base de datos si no existe"""
    print("🗄️ Configurando base de datos...")
    
    # Verificar si la base de datos ya existe
    check_db_cmd = "psql -U postgres -lqt | cut -d \\| -f 1 | grep -qw moverly"
    try:
        result = subprocess.run(check_db_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Base de datos 'moverly' ya existe")
            return True
    except:
        pass
    
    # Crear base de datos
    create_db_cmd = "psql -U postgres -c 'CREATE DATABASE moverly;'"
    if run_command(create_db_cmd, "Creando base de datos 'moverly'"):
        print("✅ Base de datos creada")
        return True
    
    print("⚠️  No se pudo crear la base de datos automáticamente")
    print("   Crea manualmente: CREATE DATABASE moverly;")
    return False


def show_next_steps():
    """Muestra los siguientes pasos"""
    print("\n" + "="*60)
    print("🎉 ¡Configuración completada!")
    print("="*60)
    print("\n📋 Próximos pasos:")
    print("\n1. Activar entorno virtual:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("   source venv/bin/activate")
    
    print("\n2. Editar archivo .env con tus configuraciones")
    
    print("\n3. Ejecutar el servidor:")
    print("   uvicorn main:app --reload")
    
    print("\n4. Abrir documentación:")
    print("   http://localhost:8000/docs")
    
    print("\n5. Health check:")
    print("   http://localhost:8000/health")
    
    print("\n📚 Documentación completa en:")
    print("   docs/API_DOCUMENTATION.md")
    print("   README.md")
    
    print("\n🚀 ¡Moverly Backend está listo!")


def main():
    """Función principal del script"""
    print("🚚⚡ Configuración inicial de Moverly Backend")
    print("="*50)
    
    # Verificaciones previas
    if not check_python_version():
        sys.exit(1)
    
    if not check_postgresql():
        print("⚠️  PostgreSQL no está disponible, pero puedes continuar")
        print("   Asegúrate de instalarlo antes de ejecutar la aplicación")
    
    # Configuración
    steps = [
        create_env_file,
        create_virtual_environment,
        install_dependencies,
        create_database,
    ]
    
    failed_steps = []
    for step in steps:
        if not step():
            failed_steps.append(step.__name__)
    
    if failed_steps:
        print(f"\n⚠️  Algunos pasos fallaron: {', '.join(failed_steps)}")
        print("   Revisa los errores arriba y ejecuta manualmente los pasos fallidos")
    
    show_next_steps()


if __name__ == "__main__":
    main()
