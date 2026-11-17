# Docker - Base de datos local para Moverly Backend

Este documento explica cómo levantar un contenedor de PostgreSQL para desarrollo y conectar la aplicación.

Requisitos
- Docker y Docker Compose instalados en tu máquina.

Archivos añadidos
- `docker-compose.yml` - define un servicio `db` con PostgreSQL 15 y un volumen persistente.
- `.env.docker` - variables de entorno ejemplo que apuntan a la base de datos del contenedor.

Levantar el contenedor (PowerShell)

```powershell
# Desde la raíz del proyecto
docker compose up -d

# Ver logs si es necesario
docker compose logs -f db
```

Iniciar migraciones y datos de prueba (db-init)

```powershell
# Tras levantar el servicio db, ejecuta el servicio de inicialización una vez
docker compose run --rm db-init

# Esto instalará dependencias dentro del contenedor temporal, ejecutará
# `alembic upgrade head` y luego el script `python scripts/seed_data.py`.
```

Verificar que PostgreSQL está escuchando en 5432

```powershell
# Desde PowerShell local puedes comprobar el puerto
Get-NetTCPConnection -LocalPort 5432
```

Conectar la app
- Copia `.env.docker` a `.env` (esto hace que la app lea `DATABASE_URL` apuntando al contenedor):

```powershell
Copy-Item .env.docker .env
```

- Luego ejecuta la app (con el entorno virtual activado):

```powershell
# Activar virtualenv (si no está activo)
venv\Scripts\Activate

pip install -r requirements.txt
uvicorn main:app --reload
```

Ejecutar migraciones (Alembic)

```powershell
alembic upgrade head
```

Notas
- El `DATABASE_URL` en `.env.docker` usa `localhost:5432`. Si ejecutas la API dentro de otro contenedor (por ejemplo con `docker-compose` en un servicio separado), cambia el host a `db` en la URL: `postgresql+asyncpg://postgres:postgres@db:5432/moverly`.
- Si necesitas datos iniciales, usa `scripts/seed_data.py` o monta un script de inicialización en `docker-compose.yml`.
- El volumen `db_data` persiste los datos en la máquina host; para borrar la DB local ejecuta: `docker compose down -v`.
