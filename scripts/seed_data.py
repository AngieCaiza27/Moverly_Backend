#!/usr/bin/env python3
"""
Script para generar datos de prueba en Moverly Backend
Crea usuarios, conductores, vehículos y órdenes de ejemplo
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.driver import DriverProfile, Vehicle, DriverAvailability
from app.models.order import Order, OrderStatus
from app.models.chat_rating import ChatMessage, Rating
from app.core.security import hash_password
import uuid
from datetime import datetime, timedelta


async def create_sample_data():
    """Crea datos de muestra para testing"""
    print("🌱 Creando datos de prueba...")
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. Crear usuarios de prueba
            print("👥 Creando usuarios...")
            
            # Cliente de prueba
            cliente_first, cliente_last = "Juan", "Pérez"
            cliente = User(
                id=uuid.uuid4(),
                correo="cliente@example.com",
                telefono="+1234567890",
                contrasena_hash=hash_password("password123"),
                # Use the Enum value (Spanish) to match the DB ENUM
                rol=UserRole.client.value,
                nombre_completo=f"{cliente_first} {cliente_last}",
                activo=True
            )
            session.add(cliente)
            
            # Conductor de prueba
            conductor_first, conductor_last = "Carlos", "González"
            conductor = User(
                id=uuid.uuid4(),
                correo="conductor@example.com",
                telefono="+1234567891",
                contrasena_hash=hash_password("password123"),
                rol=UserRole.driver.value,
                nombre_completo=f"{conductor_first} {conductor_last}",
                activo=True
            )
            session.add(conductor)
            
            # Admin de prueba
            admin_first, admin_last = "María", "Admin"
            admin = User(
                id=uuid.uuid4(),
                correo="admin@example.com",
                telefono="+1234567892",
                contrasena_hash=hash_password("password123"),
                rol=UserRole.admin.value,
                nombre_completo=f"{admin_first} {admin_last}",
                activo=True
            )
            session.add(admin)
            
            await session.commit()
            print(f"✅ Usuarios creados: {cliente.correo}, {conductor.correo}, {admin.correo}")
            
            # 2. Crear perfil de conductor
            print("🚚 Creando perfil de conductor...")
            perfil_conductor = DriverProfile(
                usuario_id=conductor.id,
                licencia_numero="LIC123456789",
                licencia_categoria="E",
                licencia_vigente=True,
                licencia_documento="https://example.com/licencia.pdf",
                documento_respaldo="https://example.com/certificado_cooperativa.pdf",
                verificado=True,
                verificado_por=admin.id,
                fecha_verificacion=datetime.utcnow(),
                promedio_calificacion=4.5,
                total_calificaciones=10
            )
            session.add(perfil_conductor)
            
            # 3. Crear vehículo
            print("🚛 Creando vehículo...")
            vehiculo = Vehicle(
                id=uuid.uuid4(),
                conductor_id=conductor.id,
                placa="ABC-123",
                tipo="camión",
                capacidad_kg=1500,
                documento_respaldo="https://example.com/matricula.pdf",
                activo=True,
                creado_en=datetime.utcnow()
            )
            session.add(vehiculo)
            
            # 4. Crear disponibilidad
            print("📍 Creando disponibilidad...")
            disponibilidad = DriverAvailability(
                conductor_id=conductor.id,
                disponible=True,
                zona="Centro",
                latitud=19.4326,
                longitud=-99.1332,
                actualizado_en=datetime.utcnow()
            )
            session.add(disponibilidad)
            
            await session.commit()
            
            # 5. Crear órdenes de prueba
            print("📦 Creando órdenes...")
            
            orden1 = Order(
                id=uuid.uuid4(),
                cliente_id=cliente.id,
                conductor_id=conductor.id,
                estado=OrderStatus.completada,
                direccion_origen="Av. Reforma 123, Ciudad de México",
                lat_origen=19.4326,
                lng_origen=-99.1332,
                direccion_destino="Calle Insurgentes 456, Ciudad de México",
                lat_destino=19.4285,
                lng_destino=-99.1276,
                distancia_km=5.2,
                tiempo_estimado_min=25,
                precio_estimado=150.00,
                creado_en=datetime.utcnow() - timedelta(days=2),
                actualizado_en=datetime.utcnow() - timedelta(days=1)
            )
            session.add(orden1)
            
            orden2 = Order(
                id=uuid.uuid4(),
                cliente_id=cliente.id,
                conductor_id=None,
                estado=OrderStatus.pendiente,
                direccion_origen="Calle Roma Norte 789, Ciudad de México",
                lat_origen=19.4194,
                lng_origen=-99.1551,
                direccion_destino="Av. Insurgentes Sur 321, Ciudad de México",
                lat_destino=19.3456,
                lng_destino=-99.1625,
                distancia_km=8.5,
                tiempo_estimado_min=35,
                precio_estimado=220.00,
                creado_en=datetime.utcnow() - timedelta(hours=2),
                actualizado_en=datetime.utcnow() - timedelta(hours=2)
            )
            session.add(orden2)
            
            await session.commit()
            
            # 6. Crear mensajes de chat
            print("💬 Creando mensajes de chat...")
            
            mensaje1 = ChatMessage(
                orden_id=orden1.id,
                remitente_id=cliente.id,
                mensaje="Hola, ¿a qué hora llegas?",
                enviado_en=datetime.utcnow() - timedelta(days=2, hours=1)
            )
            session.add(mensaje1)
            
            mensaje2 = ChatMessage(
                orden_id=orden1.id,
                remitente_id=conductor.id,
                mensaje="Hola! Llegaré en 15 minutos",
                enviado_en=datetime.utcnow() - timedelta(days=2, minutes=45)
            )
            session.add(mensaje2)
            
            # 7. Crear calificaciones
            print("⭐ Creando calificaciones...")
            
            calificacion = Rating(
                orden_id=orden1.id,
                usuario_califica_id=cliente.id,
                usuario_calificado_id=conductor.id,
                puntaje=5,
                comentario="Excelente servicio, muy puntual y cuidadoso",
                creado_en=datetime.utcnow() - timedelta(days=1)
            )
            session.add(calificacion)
            
            await session.commit()
            
            print("\n🎉 ¡Datos de prueba creados exitosamente!")
            print("\n📋 Resumen:")
            print(f"   👥 Usuarios: 3 (cliente, conductor, admin)")
            print(f"   🚚 Perfil conductor: 1")
            print(f"   🚛 Vehículos: 1")
            print(f"   📍 Disponibilidad: 1")
            print(f"   📦 Órdenes: 2")
            print(f"   💬 Mensajes: 2")
            print(f"   ⭐ Calificaciones: 1")
            
            print("\n🔑 Credenciales de prueba:")
            print(f"   Cliente: cliente@example.com / password123")
            print(f"   Conductor: conductor@example.com / password123")
            print(f"   Admin: admin@example.com / password123")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creando datos: {e}")
            raise


async def clear_sample_data():
    """Elimina los datos de prueba"""
    print("🧹 Eliminando datos de prueba...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Eliminar en orden inverso para respetar foreign keys
            await session.execute("DELETE FROM calificaciones WHERE orden_id IN (SELECT id FROM ordenes WHERE cliente_id IN (SELECT id FROM usuarios WHERE correo LIKE '%@example.com'))")
            await session.execute("DELETE FROM mensajes_chat WHERE orden_id IN (SELECT id FROM ordenes WHERE cliente_id IN (SELECT id FROM usuarios WHERE correo LIKE '%@example.com'))")
            await session.execute("DELETE FROM eventos_orden WHERE orden_id IN (SELECT id FROM ordenes WHERE cliente_id IN (SELECT id FROM usuarios WHERE correo LIKE '%@example.com'))")
            await session.execute("DELETE FROM ordenes WHERE cliente_id IN (SELECT id FROM usuarios WHERE correo LIKE '%@example.com')")
            await session.execute("DELETE FROM disponibilidad_conductor WHERE conductor_id IN (SELECT id FROM usuarios WHERE correo LIKE '%@example.com')")
            await session.execute("DELETE FROM vehiculos WHERE conductor_id IN (SELECT id FROM usuarios WHERE correo LIKE '%@example.com')")
            await session.execute("DELETE FROM perfil_conductor WHERE usuario_id IN (SELECT id FROM usuarios WHERE correo LIKE '%@example.com')")
            await session.execute("DELETE FROM usuarios WHERE correo LIKE '%@example.com'")
            
            await session.commit()
            print("✅ Datos de prueba eliminados")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error eliminando datos: {e}")
            raise


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestiona datos de prueba de Moverly")
    parser.add_argument("--clear", action="store_true", help="Eliminar datos de prueba")
    parser.add_argument("--recreate", action="store_true", help="Eliminar y recrear datos de prueba")
    
    args = parser.parse_args()
    
    if args.clear:
        await clear_sample_data()
    elif args.recreate:
        await clear_sample_data()
        await create_sample_data()
    else:
        await create_sample_data()


if __name__ == "__main__":
    # On Windows the default ProactorEventLoop is not compatible with
    # psycopg async; force the selector event loop policy so async
    # DB drivers work correctly.
    if sys.platform.startswith("win"):
        try:
            # type: ignore[attr-defined]
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception:
            # best-effort; if this fails, asyncio.run will surface the original error
            pass

    asyncio.run(main())
