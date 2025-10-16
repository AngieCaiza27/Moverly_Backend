# Configuración local — Moverly Backend (Guía en Español)

Esta guía explica paso a paso cómo levantar el backend en tu máquina usando Docker para la base de datos y un entorno virtual Python para la aplicación.

Requisitos previos
- Docker y Docker Compose instalados y en ejecución
- Python 3.11+ instalado
- Git
- (Windows) PowerShell

1) Clona el repositorio y abre el proyecto

```powershell
git clone <repo-url> moverly-backend
cd moverly-backend
```

2) Levantar PostgreSQL con Docker

```powershell
docker compose up -d db
```

Esto crea un volumen Docker llamado `db_data` que persiste la base de datos.

3) Crear y activar el entorno virtual

```powershell
python -m venv .\venv
.\venv\Scripts\Activate.ps1
```

4) Instalar dependencias

```powershell
pip install -r requirements.txt
```

Notas:
- El proyecto ya incluye correcciones para Windows (pin de `bcrypt` y `greenlet`) para evitar errores de compilación.
- Usamos `psycopg[binary,async]` para el driver async en vez de `asyncpg` para evitar necesitar herramientas de compilación adicionales en Windows.

5) Ejecutar migraciones (Alembic)

```powershell
.\venv\Scripts\python.exe -m alembic upgrade head
```

6) Poblar datos de prueba (opcional)

```powershell
.\venv\Scripts\python.exe scripts\seed_data.py
```

En Windows el script ajusta la política del loop de asyncio para compatibilidad con `psycopg`.

7) Ejecutar la aplicación

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

URL por defecto: http://127.0.0.1:8000

8) Ver la documentación Swagger / ReDoc

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Desde PowerShell puedes abrirla así:

```powershell
Start-Process 'http://127.0.0.1:8000/docs'
```

9) Problemas comunes y soluciones

- Error `ProactorEventLoop` con psycopg en Windows: el script de seed ya fuerza `WindowsSelectorEventLoopPolicy`. Si ejecutas otro script async en Windows y aparece este error, aplica la misma política antes de `asyncio.run()`.
- Error al instalar `bcrypt`: usamos una versión publicada con ruedas precompiladas para Windows; asegúrate de ejecutar `pip install -r requirements.txt` en el venv.
- Error `DuplicateObject` al crear ENUM: la migración fue ajustada para no crear tipos explícitos dos veces.

10) Automatización (opcional)

- Si prefieres, puedo añadir un archivo `scripts/init.ps1` que ejecute estos pasos en orden (levantar DB, instalar deps, migrar, seed y arrancar la app).

---

¿Quieres que añada el script de PowerShell `scripts/init.ps1` para ejecutar todo con un solo comando?