# Documentación Técnica - API Moverly

## Arquitectura del Sistema

### Stack Tecnológico
- **Framework**: FastAPI (Python 3.13+)
- **Base de Datos**: PostgreSQL con SQLAlchemy 2.0 (Async)
- **Autenticación**: JWT (JSON Web Tokens)
- **Validación**: Pydantic v2
- **Servidor**: Uvicorn (ASGI)

### Patrón de Arquitectura
```
app/
├── core/           # Configuración y seguridad
├── db/            # Conexión a base de datos
├── models/        # Modelos SQLAlchemy (ORM)
├── schemas/       # Esquemas Pydantic (validación)
├── routes/        # Endpoints de la API
├── services/      # Lógica de negocio
└── utils/         # Utilidades generales
```

##  Modelo de Datos

### Entidades Principales

#### 1. **Usuarios** (`usuarios`)
```sql
- id: UUID (PK)
- correo: VARCHAR(255) UNIQUE
- telefono: VARCHAR(32) NULLABLE
- contrasena_hash: VARCHAR(255)
- rol: ENUM (cliente, conductor, admin)
- nombre_completo: VARCHAR(255) NOT NULL
- activo: BOOLEAN DEFAULT true
- creado_en: TIMESTAMPTZ DEFAULT now()
```

#### 2. **Perfil Conductor** (`perfil_conductor`)
```sql
- usuario_id: UUID (PK, FK -> usuarios.id)
- licencia_numero: VARCHAR NOT NULL
- licencia_categoria: VARCHAR NOT NULL (CHECK = 'E')
- licencia_vigente: BOOLEAN DEFAULT false
- licencia_documento: VARCHAR NULLABLE (URL del archivo escaneado)
- documento_respaldo: VARCHAR NULLABLE (Certificado de cooperativa)
- verificado: BOOLEAN DEFAULT false
- verificado_por: UUID (FK -> usuarios.id) NULLABLE
- fecha_verificacion: TIMESTAMPTZ NULLABLE
- promedio_calificacion: DECIMAL(3,2) DEFAULT 0.00
- total_calificaciones: INTEGER DEFAULT 0
```

#### 3. **Vehículos** (`vehiculos`)
```sql
- id: UUID (PK)
- conductor_id: UUID (FK -> usuarios.id)
- placa: VARCHAR UNIQUE
- tipo: VARCHAR NOT NULL DEFAULT 'camión'
- capacidad_kg: INTEGER NOT NULL
- documento_respaldo: VARCHAR NULLABLE (Matrícula o certificado de propiedad)
- activo: BOOLEAN DEFAULT true
- creado_en: TIMESTAMPTZ DEFAULT now()
```

#### 4. **Órdenes** (`ordenes`)
```sql
- id: UUID (PK)
- cliente_id: UUID (FK -> usuarios.id)
- conductor_id: UUID (FK -> usuarios.id) NULLABLE
- estado: ENUM (pendiente, aceptada, en_curso, completada, cancelada)
- direccion_origen: VARCHAR NOT NULL
- lat_origen: DECIMAL(9,6) NOT NULL
- lng_origen: DECIMAL(9,6) NOT NULL
- direccion_destino: VARCHAR NOT NULL
- lat_destino: DECIMAL(9,6) NOT NULL
- lng_destino: DECIMAL(9,6) NOT NULL
- distancia_km: DECIMAL(8,2) NULLABLE
- tiempo_estimado_min: INTEGER NULLABLE
- precio_estimado: DECIMAL(10,2) NULLABLE
- creado_en: TIMESTAMPTZ DEFAULT now()
- actualizado_en: TIMESTAMPTZ DEFAULT now()
```

#### 5. **Eventos de Orden** (`eventos_orden`)
```sql
- id: BIGSERIAL (PK)
- orden_id: UUID (FK -> ordenes.id)
- tipo_evento: VARCHAR NOT NULL
- usuario_actor_id: UUID (FK -> usuarios.id) NULLABLE
- origen: ENUM (cliente, conductor, admin, sistema)
- detalles: JSONB NULLABLE
- creado_en: TIMESTAMPTZ DEFAULT now()
```

#### 6. **Mensajes de Chat** (`mensajes_chat`)
```sql
- id: BIGSERIAL (PK)
- orden_id: UUID (FK -> ordenes.id)
- remitente_id: UUID (FK -> usuarios.id)
- mensaje: VARCHAR NOT NULL
- enviado_en: TIMESTAMPTZ DEFAULT now()
```

#### 7. **Disponibilidad Conductor** (`disponibilidad_conductor`)
```sql
- id: BIGSERIAL (PK)
- conductor_id: UUID (FK -> usuarios.id)
- disponible: BOOLEAN DEFAULT false
- zona: VARCHAR NULLABLE
- latitud: DECIMAL(9,6) NULLABLE
- longitud: DECIMAL(9,6) NULLABLE
- actualizado_en: TIMESTAMPTZ DEFAULT now()
```

#### 8. **Calificaciones** (`calificaciones`)
```sql
- id: BIGSERIAL (PK)
- orden_id: UUID (FK -> ordenes.id)
- usuario_califica_id: UUID (FK -> usuarios.id)
- usuario_calificado_id: UUID (FK -> usuarios.id)
- puntaje: SMALLINT (1-5)
- comentario: VARCHAR NULLABLE
- creado_en: TIMESTAMPTZ DEFAULT now()
```

### Índices de Base de Datos
- `ix_usuarios_correo` (correo) - Único
- `ix_vehiculos_conductor` (conductor_id)
- `ix_ordenes_estado` (estado)
- `ix_ordenes_cliente` (cliente_id)
- `ix_ordenes_conductor` (conductor_id)
- `ix_eventos_orden_id` (orden_id)
- `ix_eventos_usuario_actor` (usuario_actor_id)
- `ix_chat_orden` (orden_id)
- `ix_disp_conductor` (conductor_id)
- `ix_disp_zona` (zona)
- `ix_rating_usuario_calificado` (usuario_calificado_id)
- `ix_rating_orden_usuario` (orden_id, usuario_califica_id) - Único

## Sistema de Autenticación

### JWT Token Structure
```json
{
  "sub": "user-uuid",
  "exp": 1640995200,
  "iat": 1640908800
}
```

### Flujo de Autenticación
1. **Registro**: `POST /auth/register`
2. **Login**: `POST /auth/login`
3. **Autorización**: Header `Authorization: Bearer <token>`

### Seguridad
- Contraseñas hasheadas con bcrypt
- Tokens JWT con expiración configurable
- Middleware de CORS configurado
- Validación de entrada con Pydantic

## Endpoints de la API

### Autenticación (`/auth`)
- `POST /auth/register` - Registro de usuario
- `POST /auth/login` - Inicio de sesión

### Usuarios (`/users`)
- `GET /users/me` - Perfil del usuario autenticado

### Órdenes (`/orders`)
- `POST /orders/` - Crear orden
- `GET /orders/` - Listar mis órdenes
- `GET /orders/{order_id}` - Detalle de orden
- `PATCH /orders/{order_id}/status` - Actualizar estado
- `DELETE /orders/{order_id}` - Eliminar orden

### Conductores (`/drivers`)
- `POST /drivers/profile` - Crear/actualizar perfil conductor
- `POST /drivers/vehicles` - Agregar vehículo
- `GET /drivers/vehicles` - Listar mis vehículos
- `PUT /drivers/availability` - Actualizar disponibilidad

### Chat y Calificaciones (`/chat`)
- `POST /chat/{order_id}/messages` - Enviar mensaje
- `GET /chat/{order_id}/messages` - Listar mensajes
- `POST /chat/{order_id}/ratings` - Crear calificación

### Administración (`/admin`)
- `GET /admin/stats` - Estadísticas del sistema
- `GET /admin/drivers/pending` - Conductores pendientes de verificación
- `POST /admin/drivers/verify` - Verificar o rechazar conductor
- `GET /admin/drivers/{driver_id}/profile` - Perfil detallado de conductor
- `GET /admin/drivers/verified` - Lista de conductores verificados
- `GET /admin/drivers/all` - Todos los conductores
- `PUT /admin/drivers/{driver_id}/documents` - Actualizar documentos de conductor

## Configuración

### Variables de Entorno
```env
ENV=dev
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/moverly
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_ALGORITHM=HS256
```

### Configuración de Base de Datos
- **Driver**: asyncpg (PostgreSQL async)
- **Pool**: Configuración automática de SQLAlchemy
- **Creación de tablas**: Automática al inicio (desarrollo)
- **Migraciones**: Alembic (recomendado para producción)

## Despliegue

### Desarrollo
```bash
uvicorn main:app --reload
```

### Producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Opcional)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoreo y Logs

### Health Check
- `GET /health` - Estado del servicio
- `GET /` - Información básica de la API

### Documentación Interactiva
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

### Estructura de Tests
```
tests/
├── conftest.py
├── test_auth.py
├── test_orders.py
├── test_drivers.py
└── test_chat.py
```

### Ejecutar Tests
```bash
pytest -v
pytest --cov=app tests/
```

## Flujos de Negocio

### Flujo de Verificación de Conductor (Cumplimiento ANT)
1. **Registro**: Conductor se registra con rol "conductor"
2. **Perfil**: Crea perfil con licencia tipo E y documentos
3. **Documentos**: Sube licencia escaneada y certificado de cooperativa
4. **Revisión**: Administrador revisa documentos manualmente
5. **Verificación**: Admin aprueba o rechaza (con comentarios)
6. **Activación**: Solo conductores verificados pueden aceptar órdenes

### Flujo de Orden
1. Cliente crea orden (`POST /orders/`)
2. Sistema busca conductores disponibles **Y verificados**
3. Conductor acepta orden (actualiza estado)
4. Chat entre cliente y conductor
5. Orden completada
6. Calificaciones mutuas

### Flujo de Conductor
1. Registro como conductor
2. Crear perfil con licencia tipo E
3. Subir documentos (licencia + certificado cooperativa)
4. Esperar verificación del administrador
5. Agregar vehículos con documentos
6. Actualizar disponibilidad
7. Recibir y aceptar órdenes (solo si verificado)
8. Completar servicios

## Consideraciones de Seguridad

### Validación de Datos
- Todos los inputs validados con Pydantic
- Sanitización automática de strings
- Validación de tipos y rangos

### Autorización
- JWT tokens con expiración
- Verificación de roles en endpoints sensibles
- Validación de ownership (usuarios solo ven sus datos)

### Base de Datos
- Foreign Keys para integridad referencial
- Índices para optimización de consultas
- Constraints de unicidad donde corresponde

## Escalabilidad

### Optimizaciones Implementadas
- Consultas async con SQLAlchemy 2.0
- Índices en campos de búsqueda frecuente
- Paginación en listados (futuro)
- Caché de sesiones (futuro)

### Consideraciones Futuras
- Redis para caché
- WebSockets para chat en tiempo real

WebSocket chat
----------------

Endpoint: `/ws/chat/{order_id}`

- Conexión: aceptar WebSocket y pasar token JWT como query param `?token=...` para autenticación.
- Mensajes: mensajes recibidos como texto se persisten en la base de datos y se difunden a todos los clientes conectados a la misma `order_id`.
- Nota: Implementación in-memory; en despliegues multi-worker usar Pub/Sub (Redis) para broadcasting.
- Microservicios para funcionalidades específicas
- Load balancing con múltiples workers
