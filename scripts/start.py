#!/usr/bin/env python3
"""
Script de inicio rápido para Moverly Backend
Inicia el servidor con configuración automática
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_env_file():
    """Verifica que el archivo .env exista"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        print("   Copia env.example a .env y configura tus variables")
        return False
    return True


def check_venv():
    """Verifica que el entorno virtual esté activo"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return True
    return False


def start_server(host="localhost", port=8000, reload=True, workers=None):
    """Inicia el servidor FastAPI"""
    print(f"🚀 Iniciando Moverly Backend...")
    print(f"   Host: {host}")
    print(f"   Puerto: {port}")
    print(f"   Modo: {'Desarrollo' if reload else 'Producción'}")
    
    if not check_env_file():
        sys.exit(1)
    
    if not check_venv():
        print("⚠️  No estás en un entorno virtual")
        print("   Se recomienda activar el entorno virtual antes de continuar")
        response = input("¿Continuar de todos modos? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Construir comando uvicorn
    cmd = ["uvicorn", "main:app"]
    cmd.extend(["--host", host])
    cmd.extend(["--port", str(port)])
    
    if reload:
        cmd.append("--reload")
    
    if workers:
        cmd.extend(["--workers", str(workers)])
    
    print(f"\n📡 Comando: {' '.join(cmd)}")
    print(f"🌐 URL: http://{host}:{port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"❤️  Health: http://{host}:{port}/health")
    print("\n" + "="*50)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al iniciar el servidor: {e}")
        sys.exit(1)


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Inicia Moverly Backend")
    parser.add_argument("--host", default="localhost", help="Host del servidor (default: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Puerto del servidor (default: 8000)")
    parser.add_argument("--no-reload", action="store_true", help="Desactivar recarga automática")
    parser.add_argument("--workers", type=int, help="Número de workers (modo producción)")
    parser.add_argument("--prod", action="store_true", help="Modo producción")
    
    args = parser.parse_args()
    
    # Configuración según el modo
    reload = not args.no_reload and not args.prod
    workers = args.workers if args.workers else (4 if args.prod else None)
    
    if args.prod:
        print("🏭 Modo producción")
        reload = False
        workers = workers or 4
    
    start_server(args.host, args.port, reload, workers)


if __name__ == "__main__":
    main()
